# backend/app/services/simplify_service.py
import os
import json
import logging
from typing import Dict, List

import google.generativeai as genai
import spacy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Gemini config ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment.")
genai.configure(api_key=GEMINI_KEY)

# Choose a model that exists in your account (from list_models output)
# Recommended stable option:
DEFAULT_GEMINI_MODEL = "models/gemini-2.5-flash"

# --- spaCy NER (graceful) ---
try:
    nlp = spacy.load("xx_ent_wiki_sm")
except Exception as e:
    logger.warning("spaCy model load failed (%s). NER fallback will be used.", e)
    nlp = None

def extract_sanskrit_terms(text: str) -> List[str]:
    """Extract candidate Sanskrit terms using spaCy NER or a simple fallback tokeniser."""
    if not text:
        return []
    if nlp:
        doc = nlp(text)
        terms = {ent.text for ent in doc.ents}
        if terms:
            return list(terms)
    # Fallback: crude tokenization for Devanagari words (tokens of length >= 2)
    import re
    tokens = re.findall(r"[\u0900-\u097F]{2,}", text)
    uniq = []
    for t in tokens:
        if t not in uniq:
            uniq.append(t)
    return uniq[:40]

def _build_prompt(sanskrit_text: str, hindi_text: str, terms: List[str]) -> str:
    terms_text = ", ".join(terms) if terms else "none"
    prompt = f"""
You are an expert in Sanskrit and Hindi simplification. Output ONLY valid JSON with two keys:
  1) "simplified_hindi": a simplified Hindi version understandable by high-school readers.
  2) "glossary": a list of objects {{ "word": "<sanskrit>", "meaning": "<simple hindi explanation>" }}.

Original Sanskrit:
{sanskrit_text}

Hindi translation:
{hindi_text}

Important Sanskrit terms detected: {terms_text}

Produce clean JSON only. Keep glossary concise (5-20 entries max) and explanations short (one sentence).
"""
    return prompt

def simplify_with_glossary(sanskrit_text: str, hindi_text: str) -> Dict:
    """
    Use Gemini 2.5 Flash to simplify Hindi and generate a glossary for Sanskrit terms.
    Returns dict: {"simplified_hindi": str, "glossary": [ {word, meaning}, ... ] }
    """
    terms = extract_sanskrit_terms(sanskrit_text)
    prompt = _build_prompt(sanskrit_text, hindi_text, terms)

    try:
        model = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
        # generate_content is supported for this model per your account's list_models
        response = model.generate_content(prompt)
        output_text = getattr(response, "text", "") or str(response)
    except Exception as e:
        logger.exception("Generation failed with model %s: %s", DEFAULT_GEMINI_MODEL, e)
        raise RuntimeError(f"Generation failed: {e}")

    # Try to parse JSON strictly, else try to extract a JSON object substring.
    try:
        parsed = json.loads(output_text.strip())
        simplified = parsed.get("simplified_hindi", parsed.get("simplified", ""))
        glossary = parsed.get("glossary", [])
        return {"simplified_hindi": simplified, "glossary": glossary}
    except Exception:
        # Attempt to extract {...} substring
        import re
        m = re.search(r"\{.*\}", output_text, flags=re.S)
        if m:
            try:
                parsed = json.loads(m.group(0))
                simplified = parsed.get("simplified_hindi", parsed.get("simplified", ""))
                glossary = parsed.get("glossary", [])
                return {"simplified_hindi": simplified, "glossary": glossary}
            except Exception:
                logger.warning("Failed to parse JSON from substring; returning raw text.")
        # Final fallback: return raw model text as simplified_hindi and empty glossary
        return {"simplified_hindi": output_text.strip(), "glossary": []}

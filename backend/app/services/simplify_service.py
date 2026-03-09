# backend/app/services/simplify_service.py
import os
import re
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
            return list(terms)[:8]
    # Fallback: crude tokenization for Devanagari words (tokens of length >= 2)
    import re
    tokens = re.findall(r"[\u0900-\u097F]{2,}", text)
    uniq = []
    for t in tokens:
        if t not in uniq:
            uniq.append(t)
    return uniq[:8]

def _build_prompt(sanskrit_text: str, hindi_text: str, terms: List[str]) -> str:
    terms_text = ", ".join(terms) if terms else "Identify important Sanskrit terms yourself."

    prompt = f"""
You are a Sanskrit scholar and expert in Indian philosophy, culture and Hindi language.

Your task is to:

1. Simplify the given Hindi translation into very clear and easy Hindi suitable for school students (age 14–16).
2. Provide a glossary of important Sanskrit terms.
3. Add a short cultural or philosophical context explaining why this verse is important.

Follow ALL instructions strictly:

-----------------------------
INPUT:
-----------------------------
Original Sanskrit:
{sanskrit_text}

Hindi Translation:
{hindi_text}

Detected Important Sanskrit Terms:
{terms_text}

-----------------------------
TASK:
-----------------------------
1. Rewrite the Hindi translation into SIMPLE, NATURAL, and CLEAR Hindi.
2. Use short sentences.
3. Avoid difficult or highly Sanskritised Hindi words.
4. Preserve the original meaning accurately.
5. If the verse relates to philosophy, ethics, devotion, duty, or cultural tradition, explain it briefly.
6.Cultural context must be 2–4 sentences only.
7. Create a glossary of important Sanskrit words:
   - Include 5–10 important terms only.
   - Each meaning must be one short and simple sentence.
   - Avoid repetition.

-----------------------------
OUTPUT FORMAT (VERY STRICT):
-----------------------------
Return ONLY valid JSON.
Do NOT add explanations.
Do NOT add markdown.
Do NOT add extra text.

The JSON must look exactly like this:

{{
  "simplified_hindi": "Simplified explanation in clear Hindi...",
  "glossary": [
    {{"word": "term1", "meaning": "simple meaning"}},
    {{"word": "term2", "meaning": "simple meaning"}}
  ]
}}

If you fail to produce valid JSON, the system will reject your answer.
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
    # -------- Robust JSON Parsing --------
    cleaned = output_text.strip()

    # Remove possible markdown wrappers
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    parsed = None

    # 1️⃣ Try direct parsing
    try:
        parsed = json.loads(cleaned)
    except Exception:
        pass

    # 2️⃣ Try extracting JSON object
    if parsed is None:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                parsed = json.loads(match.group())
            except Exception as e:
                logger.warning("JSON extraction failed: %s", e)

    # 3️⃣ Final fallback
    if parsed is None:
        logger.warning("Could not parse Gemini JSON output.")
        logger.warning("Model output was: %s", cleaned)

        return {
            "simplified_hindi": "Simplification failed. Please retry.",
            "glossary": []
        }

    simplified = parsed.get("simplified_hindi", "")
    glossary = parsed.get("glossary", [])

    return {
        "simplified_hindi": simplified,
        "glossary": glossary
   }
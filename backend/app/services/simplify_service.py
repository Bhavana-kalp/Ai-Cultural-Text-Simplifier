# backend/app/services/simplify_service.py

import os
import json
import logging
from typing import Dict, List

import google.generativeai as genai
import spacy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------- Gemini Config ----------

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise RuntimeError("GEMINI_API_KEY not set.")

genai.configure(api_key=GEMINI_KEY)

MODEL = "models/gemini-2.5-flash-lite"


# ---------- spaCy NER ----------

try:
    nlp = spacy.load("xx_ent_wiki_sm")
except Exception:
    logger.warning("spaCy model not found. Using fallback term extraction.")
    nlp = None


# ---------- Extract Sanskrit Terms ----------

def extract_sanskrit_terms(text: str) -> List[str]:

    if not text:
        return []

    # if nlp:
    #     doc = nlp(text)
    #     terms = {ent.text for ent in doc.ents}
    #     if terms:
    #         return list(terms)

    import re
    import unicodedata

    if not text:
        return []

    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    tokens = re.findall(r"[\u0900-\u097F]{2,}", text)
    
    unique = []

    for t in tokens:
        t = t.strip()
        if t in ["।", "॥"]:
            continue
        if t.isdigit():
            continue
        if len(t) <= 2:
            continue
        if t not in unique:
            unique.append(t)

    return unique[:40]


# ---------- Call 1 : Simplify Hindi ----------

def simplify_hindi(hindi_text: str) -> str:

    prompt = f"""
You are an expert in Sanskrit and Hindi explanation.

Rewrite the Hindi translation below into MUCH SIMPLER Hindi so that a 14–16 year old student can easily understand it.

Rules:
- Use short and clear sentences.
- Replace difficult Sanskritised words with common Hindi.
- If the text already looks simple, rewrite it anyway using easier wording.
- Keep the original meaning correct.

Hindi translation:
{hindi_text}

Return ONLY the simplified Hindi text.
"""

    try:

        model = genai.GenerativeModel(MODEL)

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 3000
            }
        )

        return response.text.strip()

    except Exception as e:

        logger.exception("Simplification failed")

        return "Simplification failed."


# ---------- Call 2 : Generate Glossary ----------

def generate_glossary(terms: List[str]) -> List[Dict]:

    if not terms:
        return []

    terms_text = ", ".join(terms)

    prompt = f"""
You are an expert in Sanskrit and Indian philosophy.

Below is a list of Sanskrit words detected from the verse.

Detected Sanskrit terms:
{terms_text}

Task:
From the above list, SELECT the most important Sanskrit terms and explain them in very simple Hindi.

Rules:
- Choose only meaningful Sanskrit words.
- Ignore punctuation, numbers, or meaningless tokens.
- Explain each word in one short and simple Hindi sentence.

Return ONLY valid JSON in this format:

{{
 "glossary": [
   {{"word": "term", "meaning": "simple Hindi explanation"}}
 ]
}}
"""

    try:

        model = genai.GenerativeModel(MODEL)

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 3000
            }
        )

        text = response.text.strip()

        text = text.replace("```json", "").replace("```", "").strip()

        data = json.loads(text)

        return data.get("glossary", [])

    except Exception as e:

        logger.warning("Glossary generation failed: %s", e)

        return []


# ---------- Main Function ----------

def simplify_with_glossary(sanskrit_text: str, hindi_text: str) -> Dict:

    terms = extract_sanskrit_terms(sanskrit_text)
    print("Extracted terms:", terms)
    terms = [t for t in terms if len(t) > 2 and not t.isdigit()]
    simplified = simplify_hindi(hindi_text)

    glossary = generate_glossary(terms)

    return {
        "simplified_hindi": simplified,
        "glossary": glossary
    }
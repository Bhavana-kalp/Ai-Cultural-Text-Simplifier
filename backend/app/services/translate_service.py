# backend/app/services/translate_service.py
import os
import requests
import unicodedata
import re
from typing import Tuple

GOOGLE_TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")  # set this in your env

if not GOOGLE_API_KEY:
    # allow code to run locally but will raise if you actually call translate without key
    # you can still run preprocessing functions without API key.
    pass


def preprocess_sanskrit_text(text: str) -> str:
    """
    Basic preprocessing for Sanskrit (Devanagari) text extracted via OCR.
    - Unicode NFKC normalization
    - Remove stray ASCII control characters
    - Normalize multiple spaces/newlines
    - Strip non-Devanagari garbage but keep punctuation used in Sanskrit (optional)
    """
    if not text:
        return ""

    # Unicode normalization
    t = unicodedata.normalize("NFKC", text)

    # Remove ASCII control characters
    t = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", t)

    # Replace weird repeated punctuation/characters introduced by OCR
    t = re.sub(r"[^\S\r\n]+", " ", t)  # collapse whitespace (but keep newlines)
    t = t.strip()

    # Optional: remove characters that are clearly not Devanagari (keep Devanagari + basic punctuation)
    # Unicode Devanagari block: U+0900 - U+097F
    # Keep digits (0-9) and Devanagari digits \u0966-\u096F, punctuation (।,॰,.,,?) and spaces/newlines
    cleaned_chars = []
    for ch in t:
        code = ord(ch)
        if 0x0900 <= code <= 0x097F or ch.isspace() or ch.isdigit() or 0x0966 <= code <= 0x096F:
            cleaned_chars.append(ch)
        elif ch in ("।", "॥", ",", ".", ":", ";", "?", "!", "(", ")", "-", "—", "–", "'","\""):
            cleaned_chars.append(ch)
        else:
            # skip Latin letters and other scripts introduced by OCR noise
            # you could also choose to keep them if you expect transliteration
            pass

    cleaned = "".join(cleaned_chars)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def translate_text_to_hindi(text: str, source: str = "sa", target: str = "hi") -> Tuple[str, dict]:
    """
    Translate `text` using Google Translate v2 REST API.
    - source='sa' (Sanskrit) — Google Translate supports 'sa' as language code.
    - target='hi' (Hindi)
    Returns (translated_text, raw_response_json)
    NOTE: requires GOOGLE_API_KEY env var.
    """

    if not text:
        return "", {}

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set in environment. Set it to use Google Translate API.")

    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text",
        "key": api_key,
    }

    # Use POST with application/x-www-form-urlencoded or GET with params; requests will encode for us
    resp = requests.post(GOOGLE_TRANSLATE_URL, data=payload, timeout=30)
    resp.raise_for_status()
    json_resp = resp.json()

    # Parse response: translations[0].translatedText
    translated_text = ""
    try:
        translations = json_resp.get("data", {}).get("translations", [])
        if translations:
            translated_text = translations[0].get("translatedText", "")
    except Exception:
        translated_text = ""

    return translated_text, json_resp

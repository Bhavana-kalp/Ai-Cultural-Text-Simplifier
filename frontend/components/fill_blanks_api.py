import requests
from typing import Dict
from utils.config import FILL_BLANKS_URL

TIMEOUT = 30

def fetch_fill_blanks(sanskrit_text: str, glossary: list) -> Dict:
    try:
        payload = {
            "sanskrit_text": sanskrit_text,
            "glossary": glossary,
            "num_blanks": 4
        }

        resp = requests.post(FILL_BLANKS_URL, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()

        return resp.json()

    except Exception as e:
        raise RuntimeError(f"Fill blanks API failed: {e}")
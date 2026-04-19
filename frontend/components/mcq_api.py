import requests
from typing import List, Dict
from utils.config import MCQ_URL

TIMEOUT = 30

def fetch_mcqs(glossary: List[Dict], num_questions: int = 5):
    try:
        payload = {
            "glossary": glossary,
            "num_questions": num_questions
        }

        resp = requests.post(MCQ_URL, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()

        return resp.json().get("mcqs", [])

    except Exception as e:
        raise RuntimeError(f"MCQ API failed: {e}")
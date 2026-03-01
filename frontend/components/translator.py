# frontend/components/translator.py
import requests
import streamlit as st
from typing import Tuple
from utils.config import TRANSLATE_URL

TIMEOUT = 30

@st.cache_data(show_spinner=False)
def _call_translate_api(text: str) -> dict:
    """
    Call backend /api/translate with JSON payload { "text": "<sanskrit>" }.
    Returns parsed JSON dict from backend.
    Raises RuntimeError on failure.
    """
    payload = {"text": text}
    try:
        resp = requests.post(TRANSLATE_URL, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise RuntimeError("Translate request timed out.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Could not connect to translate backend at {TRANSLATE_URL}.")
    except requests.exceptions.HTTPError as e:
        # include server message
        try:
            msg = resp.json()
        except Exception:
            msg = resp.text
        raise RuntimeError(f"Translate backend returned HTTP {resp.status_code}: {msg}")
    except Exception as e:
        raise RuntimeError(f"Translate request failed: {e}")

def translate_sanskrit(text: str) -> Tuple[str, dict]:
    """
    Returns (hindi_text, raw_response)
    """
    if not text or not text.strip():
        return "", {}
    data = _call_translate_api(text)
    # backend returns {"preprocessed_text":..., "hindi":..., "raw_response":...}
    hindi = data.get("hindi", "")
    return hindi, data

# frontend/components/simplifier.py
import requests
import streamlit as st
from typing import Dict
from utils.config import SIMPLIFY_URL

TIMEOUT = 120

# @st.cache_data(show_spinner=False)
def _call_simplify_api(sanskrit: str, hindi: str) -> Dict:
    payload = {"sanskrit": sanskrit, "hindi": hindi}
    try:
        resp = requests.post(SIMPLIFY_URL, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise RuntimeError("Simplify request timed out.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Could not connect to simplify backend at {SIMPLIFY_URL}.")
    except requests.exceptions.HTTPError as e:
        # try to get server message
        try:
            msg = resp.json()
        except Exception:
            msg = resp.text
        raise RuntimeError(f"Simplify backend returned HTTP {resp.status_code}: {msg}")
    except Exception as e:
        raise RuntimeError(f"Simplify request failed: {e}")

def simplify_text(sanskrit: str, hindi: str) -> Dict:
    if not (sanskrit and hindi):
        return {"simplified_hindi": "", "glossary": []}
    return _call_simplify_api(sanskrit, hindi)

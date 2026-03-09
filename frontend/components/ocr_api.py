# frontend/components/ocr_api.py
import io
import requests
import streamlit as st
from PIL import Image

from utils.config import OCR_URL

MAX_DIM = 1800  # max width/height in pixels to avoid huge uploads
TIMEOUT_SECONDS = 60  # increased timeout

def _resize_and_compress(pil_image: Image.Image) -> bytes:
    # Resize while keeping aspect ratio
    w, h = pil_image.size
    max_dim = max(w, h)
    if max_dim > MAX_DIM:
        scale = MAX_DIM / max_dim
        new_size = (int(w * scale), int(h * scale))
        pil_image = pil_image.resize(new_size, Image.LANCZOS)
    # Save to JPEG bytes
    buf = io.BytesIO()
    pil_image.convert("RGB").save(buf, format="JPEG", quality=85)
    return buf.getvalue()

# @st.cache_data(show_spinner=False)
def _call_backend_bytes(image_bytes: bytes) -> dict:
    files = {"file": ("upload.jpg", image_bytes, "image/jpeg")}
    try:
        resp = requests.post(OCR_URL, files=files, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise RuntimeError("Request timed out — backend may be down or slow. (timeout {})".format(TIMEOUT_SECONDS))
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Could not connect to OCR backend. Is it running and reachable at {} ?".format(OCR_URL))
    except requests.exceptions.HTTPError as e:
        text = getattr(e.response, "text", "")
        raise RuntimeError(f"OCR backend returned HTTP {e.response.status_code}: {text}")
    except Exception as e:
        raise RuntimeError(f"OCR request failed: {e}")

def call_ocr_api(pil_image: Image.Image) -> str:
    img_bytes = _resize_and_compress(pil_image)
    data = _call_backend_bytes(img_bytes)
    extracted = data.get("extracted_text", "")
    return extracted or ""

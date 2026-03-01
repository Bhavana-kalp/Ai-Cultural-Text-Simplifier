# backend/app/services/ocr_service.py
import pytesseract
from PIL import Image
import io
import os
import logging

logger = logging.getLogger(__name__)

# Optional: if tesseract is in a custom location, set path here:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def list_tesseract_langs():
    try:
        langs = pytesseract.get_languages(config='')
        return langs
    except Exception as e:
        logger.warning("Could not list tesseract langs: %s", e)
        return []

def perform_ocr(image_bytes: bytes, primary_lang: str = "san", fallback_lang: str = "hin") -> str:
    """
    Try OCR with primary_lang (san). If it fails due to missing model, fallback to fallback_lang (hin).
    Raises RuntimeError with clear message if OCR cannot be performed.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")

    # Quick check of available languages
    try:
        available = list_tesseract_langs()
    except Exception:
        available = []

    # Try primary
    try:
        if primary_lang in available or not available:
            # If get_languages failed earlier, still attempt and catch errors
            text = pytesseract.image_to_string(image, lang=primary_lang)
            if text and text.strip():
                return text.strip()
    except pytesseract.TesseractError as e:
        logger.info("Primary OCR failed with %s, will try fallback. Full error: %s", primary_lang, e)

    # Fallback
    try:
        text = pytesseract.image_to_string(image, lang=fallback_lang)
        return text.strip()
    except Exception as e:
        # Give a helpful error message for debugging / UI
        err_msg = (
            "Tesseract OCR failed. Possible cause: missing traineddata files "
            f"for languages '{primary_lang}' and '{fallback_lang}'. Error: {e}"
        )
        logger.exception(err_msg)
        raise RuntimeError(err_msg)

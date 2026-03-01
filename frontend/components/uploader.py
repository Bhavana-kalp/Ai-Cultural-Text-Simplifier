# frontend/components/uploader.py
import streamlit as st
from PIL import Image
import io

def image_uploader_section():
    """
    Returns a PIL.Image object or None
    """
    uploaded_file = st.file_uploader("Upload image (png/jpg/jpeg/tiff)", type=["png", "jpg", "jpeg", "tiff"])
    if uploaded_file is None:
        return None

    try:
        uploaded_file.seek(0)
        image = Image.open(io.BytesIO(uploaded_file.read()))
        # convert to RGB to avoid issues with some formats
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image
    except Exception as e:
        st.warning(f"Could not read image: {e}")
        return None

def text_input_section():
    """
    Return pasted text
    """
    return st.text_area("Paste Sanskrit (Devanagari) text here", height=220)

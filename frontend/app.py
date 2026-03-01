# frontend/app.py
import streamlit as st
from components.uploader import image_uploader_section, text_input_section
from components.display import show_extracted_text, show_translation, show_simplification
from components.ocr_api import call_ocr_api
from components.translator import translate_sanskrit
from components.simplifier import simplify_text
st.set_page_config(page_title="Sanskrit OCR & Translate Tester", layout="centered")
st.title("Sanskrit OCR & Translate Tester")
st.write("Upload image or paste Sanskrit text → OCR (if image) → Translate to Hindi.")

# initialize session state
if "sanskrit_text" not in st.session_state:
    st.session_state["sanskrit_text"] = ""
if "hindi_text" not in st.session_state:
    st.session_state["hindi_text"] = ""
if "simplified" not in st.session_state:
    st.session_state["simplified"] = {"simplified_hindi": "", "glossary": []}
mode = st.radio("Input type", ("Image (OCR)", "Paste Sanskrit text"))

if mode == "Image (OCR)":
    pil_image = image_uploader_section()
    if pil_image:
        st.image(pil_image, caption="Uploaded image preview", use_column_width=True)
        if st.button("Run OCR"):
            with st.spinner("Running OCR..."):
                try:
                    extracted = call_ocr_api(pil_image)
                    st.session_state["sanskrit_text"] = extracted or ""
                    show_extracted_text(st.session_state["sanskrit_text"])
                except Exception as e:
                    st.error(f"OCR failed: {e}")
else:
    pasted = text_input_section()
    if pasted:
        # Save pasted text immediately (so translate button can access it)
        st.session_state["sanskrit_text"] = pasted
        show_extracted_text(st.session_state["sanskrit_text"], key_prefix="current")

st.markdown("---")

# show current stored text for debugging
st.caption("DEBUG: current stored Sanskrit text length: {}".format(len(st.session_state["sanskrit_text"] or "")))

# Translate controls
if st.button("Translate to Hindi"):
    if not st.session_state["sanskrit_text"].strip():
        st.error("No Sanskrit text available to translate. Please OCR or paste text first.")
    else:
        with st.spinner("Translating..."):
            try:
                hindi, raw = translate_sanskrit(st.session_state["sanskrit_text"])
                st.session_state["hindi_text"] = hindi or ""
                pre = raw.get("preprocessed_text") if isinstance(raw, dict) else None
                show_translation(hindi, preprocessed=pre, key_prefix="current")
            except Exception as e:
                st.error(f"Translation failed: {e}")
if st.button("Simplify + Generate Glossary"):
    if not st.session_state["sanskrit_text"].strip() or not st.session_state["hindi_text"].strip():
        st.error("Need both Sanskrit and translated Hindi. Run OCR/Translate first.")
    else:
        with st.spinner("Simplifying and building glossary..."):
            try:
                result = simplify_text(st.session_state["sanskrit_text"], st.session_state["hindi_text"])
                # normalize result keys
                simplified = result.get("simplified_hindi") or result.get("simplified") or ""
                glossary = result.get("glossary") or []
                st.session_state["simplified"] = {"simplified_hindi": simplified, "glossary": glossary}
                show_simplification(simplified, glossary,key_prefix="current")
            except Exception as e:
                st.error(f"Simplification failed: {e}")

# Show last simplification if present
# if st.session_state["simplified"]["simplified_hindi"]:
#     st.markdown("---")
#     st.caption("Last simplification results:")
#     show_simplification(st.session_state["simplified"]["simplified_hindi"],
#                         st.session_state["simplified"]["glossary"],key_prefix="last")

st.markdown("---")
st.caption("Note: Make sure backend is running and GOOGLE_API_KEY is set on the server.")

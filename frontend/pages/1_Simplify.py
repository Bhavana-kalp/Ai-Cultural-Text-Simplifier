import streamlit as st
from components.uploader import image_uploader_section, text_input_section
from components.display import show_extracted_text, show_translation, show_simplification
from components.ocr_api import call_ocr_api
from components.translator import translate_sanskrit
from components.simplifier import simplify_text
from utils.history_manager import save_to_history

st.set_page_config(page_title="Simplify Sanskrit Text", layout="wide")

st.title("📖 Sanskrit Text Simplifier")
st.markdown("Convert Sanskrit verses into simple daily Hindi with glossary support.")

# ======================================================
# SESSION STATE INIT
# ======================================================

if "sanskrit_text" not in st.session_state:
    st.session_state.sanskrit_text = ""

if "hindi_text" not in st.session_state:
    st.session_state.hindi_text = ""

if "simplified" not in st.session_state:
    st.session_state.simplified = {"simplified_hindi": "", "glossary": []}

# ======================================================
# STEP 1 — INPUT
# ======================================================

st.markdown("## 📝 Step 1: Provide Sanskrit Input")

mode = st.radio(
    "Choose Input Type:",
    ("Upload Image (OCR)", "Paste Sanskrit Text"),
    horizontal=True
)

with st.container(border=True):

    if mode == "Upload Image (OCR)":
        pil_image = image_uploader_section()

        if pil_image:
            st.image(pil_image, caption="Uploaded Image", use_container_width=True)

            if st.button("🔍 Run OCR"):
                with st.spinner("Extracting Sanskrit text..."):
                    try:
                        # Clear downstream state
                        st.session_state.hindi_text = ""
                        st.session_state.simplified = {"simplified_hindi": "", "glossary": []}

                        extracted = call_ocr_api(pil_image)
                        st.session_state.sanskrit_text = extracted or ""

                        st.success("OCR completed successfully.")
                        show_extracted_text(st.session_state.sanskrit_text, key_prefix="ocr")

                    except Exception as e:
                        st.error(f"OCR failed: {e}")

    else:
        pasted = text_input_section()

        if pasted:
            # Clear downstream state when new text pasted
            if pasted != st.session_state.sanskrit_text:
                st.session_state.hindi_text = ""
                st.session_state.simplified = {"simplified_hindi": "", "glossary": []}

            st.session_state.sanskrit_text = pasted
            show_extracted_text(st.session_state.sanskrit_text, key_prefix="paste")

# ======================================================
# STEP 2 — TRANSLATION
# ======================================================

st.markdown("## 🔄 Step 2: Translate to Hindi")

with st.container(border=True):

    if st.button("Translate to Hindi"):
        if not st.session_state.sanskrit_text.strip():
            st.error("Please provide Sanskrit text first.")
        else:
            with st.spinner("Translating..."):
                try:
                    # Clear simplification state
                    st.session_state.simplified = {"simplified_hindi": "", "glossary": []}

                    hindi, raw = translate_sanskrit(st.session_state.sanskrit_text)
                    st.session_state.hindi_text = hindi or ""

                    st.success("Translation completed.")
                    #show_translation(st.session_state.hindi_text, key_prefix="translated")

                except Exception as e:
                    st.error(f"Translation failed: {e}")

    if st.session_state.hindi_text:
        show_translation(st.session_state.hindi_text, key_prefix="translated_display")

# ======================================================
# STEP 3 — SIMPLIFICATION
# ======================================================

st.markdown("## 🧠 Step 3: Simplify & Generate Glossary")

with st.container(border=True):

    if st.button("Simplify + Generate Glossary"):
        if not st.session_state.sanskrit_text.strip():
            st.error("Please provide Sanskrit text first.")
        elif not st.session_state.hindi_text.strip():
            st.error("Please translate text first.")
        else:
            with st.spinner("Simplifying text..."):
                try:
                    result = simplify_text(
                        st.session_state.sanskrit_text,
                        st.session_state.hindi_text
                    )

                    simplified = result.get("simplified_hindi", "")
                    glossary = result.get("glossary", [])

                    st.session_state.simplified = {
                        "simplified_hindi": simplified,
                        "glossary": glossary
                    }

                    save_to_history(
                        st.session_state.sanskrit_text,
                        st.session_state.hindi_text,
                        simplified,
                        glossary
                    )

                    st.success("Simplification completed.")
                    

                except Exception as e:
                    st.error(f"Simplification failed: {e}")

    if st.session_state.simplified["simplified_hindi"]:
        show_simplification(
            st.session_state.simplified["simplified_hindi"],
            st.session_state.simplified["glossary"],
            key_prefix="final_display"
        )

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")
st.caption("⚙ Backend must be running and API keys configured properly.")
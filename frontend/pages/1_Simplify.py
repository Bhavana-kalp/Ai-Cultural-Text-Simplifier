import streamlit as st
from components.uploader import image_uploader_section, text_input_section
from components.display import show_extracted_text, show_translation, show_simplification
from components.ocr_api import call_ocr_api
from components.translator import translate_sanskrit
from components.simplifier import simplify_text
from utils.history_manager import save_to_history
from components.mcq_api import fetch_mcqs
from components.fill_blanks_api import fetch_fill_blanks
import random
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
st.markdown("## 📝 Step 4: Practice MCQs")

with st.container(border=True):

    if st.button("🎯 Generate MCQs"):

        glossary = st.session_state.simplified.get("glossary", [])

        if not glossary:
            st.warning("No glossary available. Please run simplification first.")
        else:
            try:
                mcqs = fetch_mcqs(glossary)

                st.session_state.mcqs = mcqs
                st.session_state.mcq_answers = {}
                st.session_state.mcq_submitted = False

                st.success("MCQs generated!")

            except Exception as e:
                st.error(str(e))


# -------------------------------
# DISPLAY MCQs
# -------------------------------

if "mcqs" in st.session_state and st.session_state.mcqs:

    st.markdown("### 📚 Quiz")

    for idx, q in enumerate(st.session_state.mcqs):

        st.markdown(f"**Q{idx+1}. {q['question']}**")

        selected = st.radio(
            "Choose your answer:",
            q["options"],
            key=f"mcq_{idx}"
        )

        st.session_state.mcq_answers[idx] = selected

    # -------------------------------
    # SUBMIT BUTTON
    # -------------------------------

    if st.button("✅ Submit Answers"):

        st.session_state.mcq_submitted = True


# -------------------------------
# SHOW RESULTS
# -------------------------------

if st.session_state.get("mcq_submitted"):

    st.markdown("### 🎯 Results")

    score = 0

    for idx, q in enumerate(st.session_state.mcqs):

        user_ans = st.session_state.mcq_answers.get(idx)
        correct_ans = q["answer"]

        if user_ans == correct_ans:
            st.success(f"Q{idx+1}: Correct ✅")
            score += 1
        else:
            st.error(f"Q{idx+1}: Wrong ❌ (Correct: {correct_ans})")

    st.markdown(f"### 🏆 Score: {score} / {len(st.session_state.mcqs)}")

st.markdown("## ✍️ Step 5: Fill in the Blanks")

with st.container(border=True):

    if st.button("🧩 Generate Fill in the Blanks"):

        sanskrit = st.session_state.sanskrit_text
        glossary = st.session_state.simplified.get("glossary", [])

        if not sanskrit or not glossary:
            st.warning("Please complete simplification first.")
        else:
            try:
                data = fetch_fill_blanks(sanskrit, glossary)

                st.session_state.fill_data = data
                st.session_state.fill_answers = [""] * len(data.get("blanks", []))
                st.session_state.available_options = data.get("options", []).copy()

                # ✅ IMPORTANT: track current blank index
                st.session_state.current_blank = 0

                st.success("Exercise generated!")

            except Exception as e:
                st.error(str(e))


# -------------------------------
# DISPLAY QUESTION
# -------------------------------

if "fill_data" in st.session_state:

    data = st.session_state.fill_data
    question = data.get("question_text", "")

    st.markdown("### 📜 Fill the blanks")

    st.text_area("Shloka", value=question, height=150)

    # -------------------------------
    # OPTIONS (SEQUENTIAL FILL)
    # -------------------------------

    st.markdown("### 🧩 Choose the correct words")

    cols = st.columns(4)

    for i, option in enumerate(st.session_state.available_options):

        if cols[i % 4].button(option, key=f"opt_{i}"):

            idx = st.session_state.current_blank

            if idx < len(st.session_state.fill_answers):

                # fill current blank
                st.session_state.fill_answers[idx] = option

                # move to next blank
                st.session_state.current_blank += 1

                # remove option
                st.session_state.available_options.remove(option)

                st.rerun()

    # -------------------------------
    # SHOW FILLED ANSWERS
    # -------------------------------

    st.markdown("### ✏️ Your Answers")

    for i, ans in enumerate(st.session_state.fill_answers):
        st.write(f"Blank {i+1}: {ans if ans else '___'}")

    # -------------------------------
    # SUBMIT
    # -------------------------------

    if st.button("✅ Check Answers"):

        correct_count = 0
        blanks = data.get("blanks", [])

        for i, blank in enumerate(blanks):

            correct = blank["answer"]
            user_ans = st.session_state.fill_answers[i]

            if user_ans == correct:
                st.success(f"Blank {i+1}: Correct ✅")
                correct_count += 1
            else:
                st.error(f"Blank {i+1}: Wrong ❌ (Correct: {correct})")

        st.markdown(f"### 🏆 Score: {correct_count} / {len(blanks)}")

    # -------------------------------
    # RESET
    # -------------------------------

    if st.button("🔄 Reset Answers"):
        st.session_state.fill_answers = [""] * len(st.session_state.fill_answers)
        st.session_state.available_options = data.get("options", []).copy()
        st.session_state.current_blank = 0
        st.rerun()
# ======================================================
# FOOTER
# ======================================================

st.markdown("---")
st.caption("⚙ Backend must be running and API keys configured properly.")
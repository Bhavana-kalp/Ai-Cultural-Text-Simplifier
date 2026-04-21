import streamlit as st
from components.uploader import image_uploader_section, text_input_section
from components.display import show_extracted_text, show_simplification
from components.ocr_api import call_ocr_api
from components.translator import translate_sanskrit
from components.simplifier import simplify_text
from utils.history_manager import save_to_history
from components.mcq_api import fetch_mcqs
from components.fill_blanks_api import fetch_fill_blanks
from components.tts import text_to_speech
from components.speech_to_text import speech_to_text
import random
from rapidfuzz import fuzz

def normalize(text):
    return text.strip().lower().replace("।", "").replace(".", "")

st.set_page_config(page_title="Sanskrit Learning Assistant", layout="wide")

st.title("📖 AI Sanskrit Learning Assistant (SSC Ready)")
st.markdown("Upload or paste Sanskrit text → get simple Hindi explanation instantly.")

# ======================================================
# SESSION STATE INIT
# ======================================================

if "sanskrit_text" not in st.session_state:
    st.session_state.sanskrit_text = ""

if "simplified" not in st.session_state:
    st.session_state.simplified = {"simplified_hindi": "", "glossary": []}

# ======================================================
# INPUT
# ======================================================

st.markdown("## 📝 Provide Sanskrit Input")

mode = st.radio(
    "Choose Input Type:",
    ("Upload Image (OCR)", "Paste Sanskrit Text"),
    horizontal=True
)

pil_image = None

with st.container(border=True):

    if mode == "Upload Image (OCR)":
        pil_image = image_uploader_section()

        if pil_image:
            st.image(pil_image, caption="Uploaded Image", use_container_width=True)

    else:
        pasted = text_input_section()
        if pasted:
            st.session_state.sanskrit_text = pasted

# ======================================================
# SINGLE PIPELINE BUTTON
# ======================================================

st.markdown("## 🚀 Generate Simplified Output")

with st.container(border=True):

    if st.button("✨ Generate Simplified Explanation"):

        with st.spinner("Processing your input..."):

            try:
                # ---------- STEP 1: OCR (if image) ----------
                if mode == "Upload Image (OCR)" and pil_image:
                    sanskrit_text = call_ocr_api(pil_image)
                    st.session_state.sanskrit_text = sanskrit_text

                    show_extracted_text(sanskrit_text, key_prefix="auto_ocr")

                else:
                    sanskrit_text = st.session_state.sanskrit_text

                if not sanskrit_text.strip():
                    st.error("Please provide Sanskrit input.")
                    st.stop()

                # ---------- STEP 2: TRANSLATE ----------
                hindi, _ = translate_sanskrit(sanskrit_text)

                # ---------- STEP 3: SIMPLIFY ----------
                result = simplify_text(sanskrit_text, hindi)

                simplified = result.get("simplified_hindi", "")
                glossary = result.get("glossary", [])

                # ---------- SAVE STATE ----------
                st.session_state.simplified = {
                    "simplified_hindi": simplified,
                    "glossary": glossary
                }

                save_to_history(
                    sanskrit_text,
                    hindi,
                    simplified,
                    glossary
                )

                st.success("Done! ✨")

            except Exception as e:
                st.error(f"Processing failed: {e}")

# ======================================================
# SHOW RESULT
# ======================================================

if st.session_state.simplified["simplified_hindi"]:
    simplified_text = st.session_state.simplified["simplified_hindi"]
    show_simplification(
        st.session_state.simplified["simplified_hindi"],
        st.session_state.simplified["glossary"],
        key_prefix="final_display"
    )
    st.markdown("### 🔊 Listen Explanation")
    if st.button("▶️ Play Audio"):
        audio_path = text_to_speech(simplified_text)
        if audio_path:
            audio_file = open(audio_path, "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")



st.markdown("## 🎤 Speak & Verify Exercise")

glossary = st.session_state.simplified.get("glossary", [])

if glossary:

    # pick random word
    if "speech_word" not in st.session_state:
        st.session_state.speech_word = random.choice(glossary)

    word = st.session_state.speech_word["word"]
    correct_meaning = st.session_state.speech_word["meaning"]

    st.markdown(f"### 🧠 Speak the meaning of: **{word}**")

    if st.button("🎙️ Start Recording"):

        with st.spinner("Listening... Speak now"):
            spoken_text = speech_to_text()

        st.write(f"👉 You said: **{spoken_text}**")
        spoken_clean = normalize(spoken_text)
        correct_clean = normalize(correct_meaning)
        score = fuzz.ratio(spoken_text, correct_meaning)
        # -------- MATCHING LOGIC --------
        if score > 70:   # you can tune (60–80)
            
            st.success("✅ Correct! Well done 🎉")

        else:
            st.error("❌ Not correct")

            st.info(f"💡 Hint: {correct_meaning}")

    # Next word
    if st.button("➡️ Try Another Word"):
        st.session_state.speech_word = random.choice(glossary)
        st.rerun()

else:
    st.warning("Generate explanation first.")




#==========MCQ=========

def build_glossary_map(glossary):
    return {item["word"]: item["meaning"] for item in glossary if "word" in item and "meaning" in item}


st.markdown("## 📝 Practice MCQs")

with st.container(border=True):

    if st.button("🎯 Generate MCQs"):

        glossary = st.session_state.simplified.get("glossary", [])

        if not glossary:
            st.warning("Please generate explanation first.")
        else:
            mcqs = fetch_mcqs(glossary)

            st.session_state.mcqs = mcqs
            st.session_state.mcq_answers = {}
            st.session_state.mcq_submitted = False

            st.success("MCQs generated!")

if "mcqs" in st.session_state:

    for idx, q in enumerate(st.session_state.mcqs):

        st.markdown(f"**Q{idx+1}. {q['question']}**")

        st.session_state.mcq_answers[idx] = st.radio(
            "Choose answer:",
            q["options"],
            key=f"mcq_{idx}"
        )

    # if st.button("✅ Submit Answers"):
    #     score = 0

    #     for idx, q in enumerate(st.session_state.mcqs):
    #         if st.session_state.mcq_answers[idx] == q["answer"]:
    #             st.success(f"Q{idx+1}: Correct ✅")
    #             score += 1
    #         else:
    #             st.error(f"Q{idx+1}: Wrong ❌ (Correct: {q['answer']})")

    #     st.markdown(f"### 🏆 Score: {score} / {len(st.session_state.mcqs)}")
    if st.button("✅ Submit Answers"):

        score = 0
        mistakes = []

        glossary = st.session_state.simplified.get("glossary", [])
        glossary_map = build_glossary_map(glossary)

        for idx, q in enumerate(st.session_state.mcqs):

            user_ans = st.session_state.mcq_answers.get(idx)
            correct = q["answer"]

            if not user_ans:
               st.warning(f"Q{idx+1}: Not attempted ⚠️")

            elif user_ans == correct:
               st.success(f"Q{idx+1}: Correct ✅")
               score += 1

            else:
               st.error(f"Q{idx+1}: Wrong ❌ (Correct: {correct})")

               #🧠 Build explanation
               wrong_meaning = glossary_map.get(user_ans, "No meaning found")
               correct_meaning = glossary_map.get(correct, "No meaning found")

               explanation = f"""
    ❌ You chose: **{user_ans}** → {wrong_meaning}  
    ✅ Correct: **{correct}** → {correct_meaning}

    👉 This question required understanding the correct context.
    """

               mistakes.append({
                   "question": q["question"],
                   "explanation": explanation
                })

        st.markdown(f"### 🏆 Score: {score} / {len(st.session_state.mcqs)}")
    
        if "mistakes" not in st.session_state:
            st.session_state.mistakes = []

        # Save mistakes
        st.session_state.mistakes = mistakes

        # -------------------------------
        # REVIEW SECTION
        # -------------------------------

        if st.session_state.mistakes:

            st.markdown("## 📌 Review Your Mistakes")

            for i, m in enumerate(st.session_state.mistakes):

                with st.expander(f"❌ Mistake {i+1}"):

                    st.markdown(f"**Question:** {m['question']}")
                    st.markdown(m["explanation"])


# ======================================================
# FILL IN THE BLANKS
# ======================================================

st.markdown("## ✍️ Fill in the Blanks")

with st.container(border=True):

    if st.button("🧩 Generate Fill in the Blanks"):

        glossary = st.session_state.simplified.get("glossary", [])
        sanskrit = st.session_state.sanskrit_text

        if not glossary:
            st.warning("Please generate explanation first.")
        else:
            data = fetch_fill_blanks(sanskrit, glossary)

            st.session_state.fill_data = data
            st.session_state.fill_answers = [""] * len(data["blanks"])
            st.session_state.available_options = data["options"].copy()
            st.session_state.current_blank = 0

            st.success("Exercise generated!")

if "fill_data" in st.session_state:

    data = st.session_state.fill_data

    st.text_area("Shloka", value=data["question_text"], height=150)

    cols = st.columns(4)

    for i, option in enumerate(st.session_state.available_options):

        if cols[i % 4].button(option, key=f"opt_{i}"):

            idx = st.session_state.current_blank

            if idx < len(st.session_state.fill_answers):
                st.session_state.fill_answers[idx] = option
                st.session_state.current_blank += 1
                st.session_state.available_options.remove(option)
                st.rerun()

    for i, ans in enumerate(st.session_state.fill_answers):
        st.write(f"Blank {i+1}: {ans if ans else '___'}")

    if st.button("✅ Check Answers"):

        score = 0

        for i, blank in enumerate(data["blanks"]):
            if st.session_state.fill_answers[i] == blank["answer"]:
                st.success(f"Blank {i+1}: Correct ✅")
                score += 1
            else:
                st.error(f"Blank {i+1}: Wrong ❌ (Correct: {blank['answer']})")

        st.markdown(f"### 🏆 Score: {score} / {len(data['blanks'])}")

    if st.button("🔄 Reset"):
        st.session_state.fill_answers = [""] * len(data["blanks"])
        st.session_state.available_options = data["options"].copy()
        st.session_state.current_blank = 0
        st.rerun()

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")
st.caption("⚙ Backend must be running and API keys configured properly.")
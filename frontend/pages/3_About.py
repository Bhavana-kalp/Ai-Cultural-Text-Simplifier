# frontend/pages/3_About.py

import streamlit as st

st.set_page_config(page_title="About Project", layout="wide")

st.title("ℹ About This Project")

st.markdown("""
## 📖 AI-Based Cultural Sanskrit Text Simplifier

This project is designed to simplify complex Sanskrit cultural texts 
into easy-to-understand Hindi using Artificial Intelligence.

It combines OCR, machine translation, and large language models 
to assist students and general readers in understanding ancient Indian texts.
""")

st.markdown("---")

# ---------------------------------------------------
# Problem Statement
# ---------------------------------------------------

st.markdown("## 🎯 Problem Statement")

st.markdown("""
Ancient Sanskrit texts such as the *Mahabharata*, *Ramayana*, and *Bhagavad Gita* 
contain deep philosophical meanings. However:

- Sanskrit is difficult for modern readers.
- Traditional Hindi translations are often complex.
- Cultural concepts may not be easily understood by students.

This creates a gap between classical knowledge and modern accessibility.
""")

# ---------------------------------------------------
# Solution Overview
# ---------------------------------------------------

st.markdown("## 💡 Proposed Solution")

st.markdown("""
This system provides:

1. 📷 OCR extraction of Sanskrit text from images  
2. 🔄 Automatic translation from Sanskrit to Hindi  
3. 🧠 AI-based simplification into daily spoken Hindi  
4. 📘 Glossary generation for key Sanskrit terms  
5. 📜 History tracking of previous simplifications  

The goal is to make classical Indian literature more accessible.
""")

# ---------------------------------------------------
# System Workflow
# ---------------------------------------------------

st.markdown("## ⚙ System Workflow")

st.markdown("""
**Step 1:** User uploads image or pastes Sanskrit text  
**Step 2:** OCR extracts Sanskrit text (if image)  
**Step 3:** Google Translation API converts Sanskrit → Hindi  
**Step 4:** Gemini AI model simplifies Hindi into easy language  
**Step 5:** Important Sanskrit words are identified and explained  
**Step 6:** Results are displayed and stored in history  

The system integrates multiple AI components to produce final output.
""")

# ---------------------------------------------------
# Technologies Used
# ---------------------------------------------------

st.markdown("## 🛠 Technologies Used")

st.markdown("""
### Backend
- Python
- FastAPI
- Google Translate API
- Google Gemini API
- spaCy (NER)
- Tesseract OCR

### Frontend
- Streamlit
- REST API communication
- JSON-based persistent storage
""")

# ---------------------------------------------------
# Key Features
# ---------------------------------------------------

st.markdown("## ✨ Key Features")

st.markdown("""
- Image-based Sanskrit text recognition
- Automatic translation
- Simplified Hindi explanation
- Glossary generation
- Persistent history tracking
- Lightweight architecture (No heavy database)
""")

# ---------------------------------------------------
# Future Scope
# ---------------------------------------------------

st.markdown("## 🚀 Future Scope")

st.markdown("""
- Multilingual support (English, Marathi, etc.)
- Voice-based Sanskrit input
- Audio output for simplified text
- Web deployment with authentication
- Integration with educational platforms
""")

st.markdown("---")
st.caption("Final Year Computer Science Project — AI & NLP Based System")
# frontend/app.py
import streamlit as st

st.set_page_config(
    page_title="AI Sanskrit Text Simplifier",
    page_icon="📖",
    layout="wide"
)

st.title("📖 AI-Based Sanskrit Cultural Text Simplifier")

st.markdown("""
Welcome to the AI-powered Sanskrit Text Simplifier.

This system allows you to:

- 📷 Extract Sanskrit text from images (OCR)
- 🔄 Translate Sanskrit → Hindi
- 🧠 Simplify complex Hindi into easy daily language
- 📘 Generate glossary of Sanskrit terms

Use the sidebar to navigate between pages.
""")

st.sidebar.success("Select a page above.")
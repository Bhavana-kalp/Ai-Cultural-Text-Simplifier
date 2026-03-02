# frontend/components/display.py
import streamlit as st
import pandas as pd

def show_extracted_text(text: str, key_prefix: str = "extracted"):
    st.subheader("Extracted Sanskrit Text")
    if not text:
        st.warning("No text was extracted. Try better image quality or fallback language in backend.")
    st.text_area("Sanskrit (Devanagari)", value=text, height=220, key=f"{key_prefix}_sanskrit")

def show_translation(hindi_text: str, preprocessed: str = None, key_prefix: str = "translate"):
    st.subheader("Translated Hindi")
    if preprocessed:
        st.caption("Preprocessed Sanskrit (sent to translator):")
        st.code(preprocessed, language=None)
    if not hindi_text:
        st.warning("No Hindi translation returned.")
    st.text_area("Hindi translation", value=hindi_text, height=220, key=f"{key_prefix}_hindi")

def show_simplification(simplified: str, glossary: list,key_prefix: str = "simplified"):
    st.subheader("Simplified Hindi (Easy Read)")
    if not simplified:
        st.warning("No simplified text returned.")
    st.text_area("Simplified Hindi", value=simplified or "", height=220, key=f"{key_prefix}_simplified")

    st.subheader("Glossary (Sanskrit → Simple Hindi)")
    if not glossary:
        st.info("No glossary entries returned.")
        return

    try:
        df = pd.DataFrame(glossary)
        if "word" in df.columns and "meaning" in df.columns:
            df = df[["word", "meaning"]]
        st.dataframe(df, use_container_width=True, key=f"{key_prefix}_glossary")
    except Exception:
        for i, entry in enumerate(glossary):
            w = entry.get("word", "")
            m = entry.get("meaning", "")
            st.markdown(f"**{w}** — {m}", unsafe_allow_html=False)

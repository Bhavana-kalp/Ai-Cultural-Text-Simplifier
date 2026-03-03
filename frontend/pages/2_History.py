# frontend/pages/2_History.py

import streamlit as st
import pandas as pd
from utils.history_manager import load_history
import os
import json

st.set_page_config(page_title="History", layout="wide")

st.title("📜 Simplification History")

st.markdown("View previously simplified Sanskrit texts.")

history = load_history()

# -----------------------------
# Clear History Button
# -----------------------------
col1, col2 = st.columns([1, 5])

with col1:
    if st.button("🗑 Clear All History"):
        with open(os.path.join("data", "history.json"), "w", encoding="utf-8") as f:
            json.dump([], f)
        st.success("History cleared successfully.")
        st.rerun()

# -----------------------------
# If No History
# -----------------------------
if not history:
    st.info("No history records found.")
    st.stop()

# -----------------------------
# Display History Entries
# -----------------------------
for idx, entry in enumerate(history):

    with st.expander(f"📘 Record {idx + 1} — {entry.get('timestamp', '')}"):

        st.markdown("### 📝 Sanskrit Text")
        st.text_area(
            "Sanskrit",
            value=entry.get("sanskrit", ""),
            height=150,
            key=f"sanskrit_{idx}"
        )

        st.markdown("### 🔄 Hindi Translation")
        st.text_area(
            "Hindi",
            value=entry.get("hindi", ""),
            height=150,
            key=f"hindi_{idx}"
        )

        st.markdown("### 🧠 Simplified Hindi")
        st.text_area(
            "Simplified",
            value=entry.get("simplified", ""),
            height=150,
            key=f"simplified_{idx}"
        )

        st.markdown("### 📚 Glossary")

        glossary = entry.get("glossary", [])

        if glossary:
            try:
                df = pd.DataFrame(glossary)
                if "word" in df.columns and "meaning" in df.columns:
                    df = df[["word", "meaning"]]
                st.dataframe(df, use_container_width=True)
            except Exception:
                for g in glossary:
                    st.markdown(f"**{g.get('word','')}** — {g.get('meaning','')}")
        else:
            st.info("No glossary available for this record.")

st.markdown("---")
st.caption("Showing latest records first. Maximum 30 records stored.")
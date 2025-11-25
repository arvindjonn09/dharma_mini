import streamlit as st

def apply_global_css():
    st.markdown(
        """
        <style>
        .source-text { white-space: pre-wrap; padding: 6px; background: #fafafa; }
        .mantra-box { white-space: pre-wrap; padding: 6px; background: #eef6ff; }
        </style>
        """,
        unsafe_allow_html=True
    )

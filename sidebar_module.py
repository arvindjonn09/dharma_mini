# sidebar_module.py

import streamlit as st

def render_sidebar():
    """Render sidebar options exactly like original app.py."""
    with st.sidebar:
        st.header("Options")
        st.checkbox(
            "Generate cartoon illustration for each story",
            key="generate_image",
            help="Automatically creates ACK or Clay style images."
        )

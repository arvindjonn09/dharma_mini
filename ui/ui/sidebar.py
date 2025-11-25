import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.header("Options")
        st.checkbox(
            "Generate cartoon illustration for each story",
            key="generate_image",
            help="Automatically creates story illustrations."
        )

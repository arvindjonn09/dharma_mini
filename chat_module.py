# chat_module.py

import streamlit as st
from rag_module import get_answer, get_sources, generate_image
from ui_module import render_answer_html, render_source_html, render_mantra_html
from database import load_favourites, save_favourites

def render_story_chat(age_group):
    """Main story chat interface (question → answer)."""
    st.markdown("### 📝 Ask a question")

    question = st.text_input(
        "Ask anything from the dharmic stories:",
        key="question_input"
    )

    if st.button("Ask"):
        if not question.strip():
            st.error("Please enter a question.")
            return

        with st.spinner("Thinking..."):
            answer = get_answer(question, age_group)
            sources = get_sources()

            if st.session_state.get("generate_image"):
                img_path = generate_image(question)
            else:
                img_path = None

        st.session_state.messages.append({
            "question": question,
            "answer": answer,
            "sources": sources,
            "image_path": img_path,
        })

        st.rerun()

    _render_messages()

def _render_messages():
    """Render previous Q/A results."""
    msgs = st.session_state.get("messages", [])
    if not msgs:
        return

    st.markdown("---")
    st.markdown("### 📚 Story responses")

    for msg in msgs:
        st.markdown(render_answer_html(msg["answer"]), unsafe_allow_html=True)

        if msg.get("image_path"):
            st.image(msg["image_path"], use_column_width=True)

        if msg.get("sources"):
            st.markdown(render_source_html(msg["sources"]), unsafe_allow_html=True)

        st.markdown("---")

def render_saved_stories():
    """Show user's saved stories."""
    fav = load_favourites()
    if not fav:
        st.info("No saved stories yet.")
        return

    st.header("📜 Saved Stories")
    for entry in fav:
        st.markdown(render_answer_html(entry["answer"]), unsafe_allow_html=True)

        if entry.get("image_path"):
            st.image(entry["image_path"], use_column_width=True)

        if entry.get("sources"):
            st.markdown(render_source_html(entry["sources"]), unsafe_allow_html=True)

        st.markdown("---")

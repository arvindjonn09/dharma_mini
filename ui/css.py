import streamlit as st

def apply_global_css():
    st.markdown(
        """
        <style>
        .source-text {
            white-space: pre-wrap;
            padding: 6px;
            background: #fafafa;
            border-radius: 6px;
        }
        .mantra-box {
            white-space: pre-wrap;
            padding: 6px;
            background: #eef6ff;
            border-radius: 6px;
        }
        .answer-box {
            background: #fff8e6;
            padding: 14px;
            border-left: 5px solid #f4c542;
            border-radius: 4px;
            margin-bottom: 12px;
            font-size: 1.1rem;
            line-height: 1.6;
        }
        .sources-box {
            background: #e8f4ff;
            padding: 10px;
            border-left: 4px solid #3a8dde;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

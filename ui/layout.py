import streamlit as st
from ui.css import apply_global_css

def setup_page():
    st.set_page_config(
        page_title="Dharma Story Chat",
        page_icon="📚",
        layout="wide"
    )
    apply_global_css()

def render_topbar(on_logout):
    col_title, col_user = st.columns([4, 1])

    with col_title:
        st.title("📚 Dharma Story Chat — Story Mode (All Books)")
        st.write("Stories come from all uploaded books. Answers include source books.")

    with col_user:
        role = st.session_state.get("role", "guest")
        name = st.session_state.get("user_name")
        age_group = st.session_state.get("age_group")

        if role == "admin":
            st.markdown("👑 **Admin**")
        elif role == "user":
            label = "🙂 User"
            if age_group == "child":
                label += " (Child)"
            elif age_group == "adult":
                label += " (Adult)"
            if name:
                label += f": {name}"
            st.markdown(label)

        if role in ("admin", "user"):
            if st.button("Logout"):
                on_logout()

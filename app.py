# app.py — CLEAN & MODULAR

import streamlit as st

# 1. global UI
from ui_module import apply_global_css

# 2. session + auth
from session_module import restore_session, show_session_expiry_warning
from auth_module import login_or_signup_screen

# 3. sidebar
from sidebar_module import render_sidebar

# 4. chat/story engine
from chat_module import render_story_chat, render_saved_stories

# 5. admin panel
from admin_module import render_admin_panel


# ---------------------
# PAGE CONFIG
# ---------------------
st.set_page_config(page_title="Dharma Story Chat", page_icon="📚", layout="wide")
apply_global_css()


# ---------------------
# RESTORE SESSION (if ?session=token)
# ---------------------
restore_session()


# ---------------------
# LOGIN SCREEN (if guest)
# ---------------------
if st.session_state.get("role", "guest") == "guest":
    login_or_signup_screen()


# ---------------------
# SIDEBAR OPTIONS
# ---------------------
render_sidebar()


# ---------------------
# SESSION WARNING
# ---------------------
show_session_expiry_warning()


# ---------------------
# ROUTING (admin or user)
# ---------------------
role = st.session_state.get("role")

if role == "admin":
    render_admin_panel()
else:
    age_group = st.session_state.get("age_group")
    render_story_chat(age_group)

    if st.session_state.get("show_history_panel"):
        render_saved_stories()

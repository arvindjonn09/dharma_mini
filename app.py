import streamlit as st

from ui.layout import setup_page, render_topbar, render_sidebar
from core.session_manager import restore_session, handle_logout
from core.auth_flow import render_login_screen
from ui.home_view import render_home
from ui.admin_view import render_admin_console

def main():
    setup_page()

    restore_session()

    role = st.session_state.get("role", "guest")

    if role == "guest":
        render_login_screen()
        return

    render_topbar(on_logout=handle_logout)
    render_sidebar()

    if role == "admin":
        render_admin_console()
    else:
        render_home()

if __name__ == "__main__":
    main()

import datetime
import secrets
import streamlit as st

from auth import (
    hash_password,
    check_password,
    load_users,
    save_users,
    get_admin_credentials,
)
from database import load_sessions, save_sessions

def render_login_screen():
    st.title("📚 Dharma Story Chat")
    st.subheader("Sign in to continue")
    st.markdown("---")

    mode = st.radio("Login as:", ["User", "Admin"], horizontal=True)

    if mode == "Admin":
        render_admin_login()
    else:
        render_user_login_signup()

def render_admin_login():
    admin_user, admin_pass = get_admin_credentials()

    username = st.text_input("Admin username")
    password = st.text_input("Admin password", type="password")

    if st.button("Sign in as Admin"):
        if username == admin_user and password == admin_pass:
            start_session("admin", username)
            st.success("Logged in as admin.")
            st.rerun()
        else:
            st.error("Invalid admin credentials.")

def render_user_login_signup():
    mode = st.radio("Mode:", ["Sign in", "Sign up"], horizontal=True)

    if mode == "Sign in":
        return render_user_signin()
    else:
        return render_user_signup()

def render_user_signin():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign in as User"):
        users = load_users()
        profile = users.get(username)

        if not profile:
            st.error("No account found. Please sign up.")
            return

        if not check_password(password.strip(), profile.get("password", "")):
            st.error("Incorrect password.")
            return

        year = profile.get("year_of_birth")
        age_group = None
        if isinstance(year, int):
            age = datetime.datetime.now().year - year
            age_group = "adult" if age >= 22 else "child"

        st.session_state.update({
            "role": "user",
            "user_name": profile.get("first_name") or username,
            "age_group": age_group,
            "user_profile": profile,
        })

        start_session("user", username)

        st.success("Logged in as user.")
        st.rerun()

def render_user_signup():
    username = st.text_input("Choose a username")
    first = st.text_input("First name")
    last = st.text_input("Last name")
    yob = st.text_input("Year of birth (YYYY)")
    password = st.text_input("Create password", type="password")
    lang = st.selectbox(
        "Preferred language",
        ["English", "Hindi", "Telugu", "Tamil", "Kannada", "Malayalam", "Gujarati", "Marathi", "Other"],
    )
    location = st.text_input("Location (City, Country)")

    if st.button("Sign up"):
        try:
            year = int(yob)
            age = datetime.datetime.now().year - year
            age_group = "adult" if age >= 22 else "child"
        except ValueError:
            st.error("Invalid birth year.")
            return

        users = load_users()
        if username in users:
            st.error("Username already taken.")
            return

        profile = {
            "username": username,
            "first_name": first,
            "last_name": last or None,
            "year_of_birth": year,
            "language": lang,
            "location": location or None,
            "password": hash_password(password.strip()),
        }

        users[username] = profile
        save_users(users)

        st.session_state.update({
            "role": "user",
            "user_name": first,
            "age_group": age_group,
            "user_profile": profile,
        })

        start_session("user", username)

        st.success("Signed up and logged in.")
        st.rerun()

def start_session(role, username):
    sessions = load_sessions()
    token = secrets.token_urlsafe(16)
    sessions[token] = {
        "role": role,
        "username": username,
        "created_at": datetime.datetime.now().isoformat(),
    }
    save_sessions(sessions)
    st.session_state["session_token"] = token

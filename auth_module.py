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


# ---------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------
def _start_session(role: str, username: str):
    """Create a new session token and save it to disk."""
    sessions = load_sessions()
    token = secrets.token_urlsafe(16)

    sessions[token] = {
        "role": role,
        "username": username,
        "created_at": datetime.datetime.now().isoformat(),
    }

    save_sessions(sessions)
    st.session_state["session_token"] = token


def _set_logged_in_user(username: str, profile: dict):
    """Save user session state values."""
    year = profile.get("year_of_birth")
    age_group = None

    if isinstance(year, int):
        current_year = datetime.datetime.now().year
        age = current_year - year
        age_group = "adult" if age >= 22 else "child"

    st.session_state.update({
        "role": "user",
        "user_name": profile.get("first_name") or username,
        "age_group": age_group,
        "user_profile": profile,
    })


# ---------------------------------------------
# ADMIN LOGIN SCREEN
# ---------------------------------------------
def _render_admin_login():
    admin_user, admin_pass = get_admin_credentials()

    username = st.text_input("Admin username")
    password = st.text_input("Admin password", type="password")

    if st.button("Sign in as Admin"):
        if username == admin_user and password == admin_pass:
            st.session_state.update({
                "role": "admin",
                "user_name": username,
                "age_group": None,
                "user_profile": {},
            })

            _start_session("admin", username)

            st.success("Logged in as admin.")
            st.rerun()
        else:
            st.error("Invalid admin credentials.")


# ---------------------------------------------
# USER SIGN-IN LOGIC
# ---------------------------------------------
def _render_user_signin():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign in as User"):
        # Password rule
        if len(password.strip()) < 8 or not any(
            ch in "!@#$%^&*()-_=+[]{};:'\",.<>/?|" for ch in password
        ):
            st.error("Password must be at least 8 characters and contain a special character.")
            return

        users = load_users()
        profile = users.get(username)

        if not profile:
            st.error("No account found with that username. Please sign up first.")
            return

        stored_pw = profile.get("password", "")
        if not check_password(password.strip(), stored_pw):
            st.error("Incorrect password.")
            return

        # Mark user logged in
        _set_logged_in_user(username, profile)
        _start_session("user", username)

        st.success("Logged in successfully.")
        st.rerun()


# ---------------------------------------------
# USER SIGN-UP LOGIC
# ---------------------------------------------
def _render_user_signup():
    username = st.text_input("Choose a username")
    first_name = st.text_input("First name")
    last_name = st.text_input("Last name")
    yob = st.text_input("Year of birth (YYYY)")
    password = st.text_input("Create Password", type="password")

    language = st.selectbox(
        "Preferred language",
        [
            "English",
            "Hindi",
            "Telugu",
            "Tamil",
            "Kannada",
            "Malayalam",
            "Gujarati",
            "Marathi",
            "Other",
        ],
    )

    location = st.text_input("Location (City, Country)")

    if st.button("Sign up"):
        # Basic field validations
        if not username.strip():
            st.error("Please choose a username.")
            return
        if not first_name.strip():
            st.error("Please enter your first name.")
            return
        if len(password.strip()) < 8 or not any(
            ch in "!@#$%^&*()-_=+[]{};:'\",.<>/?|" for ch in password
        ):
            st.error("Password must be at least 8 characters and contain a special character.")
            return

        # Parse birth year
        try:
            current_year = datetime.datetime.now().year
            year = int(yob)
            if year < 1900 or year > current_year:
                st.error("Please enter a valid birth year.")
                return
        except ValueError:
            st.error("Please enter birth year as numbers (YYYY).")
            return

        # Check username availability
        users = load_users()
        if username in users:
            st.error("That username is already taken. Choose another.")
            return

        # Compute age group
        age = current_year - year
        age_group = "adult" if age >= 22 else "child"
        hashed_pw = hash_password(password.strip())

        # Prepare profile
        profile = {
            "username": username.strip(),
            "first_name": first_name.strip(),
            "last_name": last_name.strip() or None,
            "year_of_birth": year,
            "language": language,
            "location": location.strip() or None,
            "password": hashed_pw,
        }

        # Save to users database
        users[username] = profile
        save_users(users)

        # Begin user session
        _set_logged_in_user(username, profile)
        _start_session("user", username)

        st.success(f"Signed up and logged in as ({age_group} mode).")
        st.rerun()


# ---------------------------------------------
# PUBLIC ENTRY POINT
# ---------------------------------------------
def login_or_signup_screen():
    """UI for guest users. Blocks until logged in."""

    st.title("📚 Dharma Story Chat")
    st.subheader("Sign in to continue")
    st.markdown("---")

    mode = st.radio("Login as:", ["User", "Admin"], horizontal=True)

    if mode == "Admin":
        _render_admin_login()
    else:
        auth_mode = st.radio("Mode:", ["Sign in", "Sign up"], horizontal=True)
        if auth_mode == "Sign in":
            _render_user_signin()
        else:
            _render_user_signup()

    st.stop()  # Critical: prevents rendering the rest of the app for guests

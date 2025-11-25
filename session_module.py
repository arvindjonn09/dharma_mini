import datetime
import streamlit as st
from database import load_sessions, save_sessions, SESSION_TTL_MINUTES
from auth import load_users

def restore_session():
    """Restore login if user visits with ?session=token."""
    if st.session_state.get("role") != "guest":
        return

    token_list = st.query_params.get("session", [])
    if isinstance(token_list, str):
        token_list = [token_list]

    if not token_list:
        return

    token = token_list[0]
    sessions = load_sessions()
    sess = sessions.get(token)

    if not sess:
        return

    created_str = sess.get("created_at")
    expired = False

    try:
        created_dt = datetime.datetime.fromisoformat(created_str)
        if datetime.datetime.now() - created_dt > datetime.timedelta(
            minutes=SESSION_TTL_MINUTES
        ):
            expired = True
    except Exception:
        expired = True

    if expired:
        sessions.pop(token, None)
        save_sessions(sessions)
        return

    role = sess.get("role")
    username = sess.get("username")

    if role == "admin":
        st.session_state.update({
            "role": "admin",
            "user_name": username,
            "age_group": None,
            "user_profile": {},
            "session_token": token,
        })
        return

    users = load_users()
    profile = users.get(username)
    if not profile:
        return

    year = profile.get("year_of_birth")
    age_group = "adult" if (datetime.datetime.now().year - year) >= 22 else "child"

    st.session_state.update({
        "role": "user",
        "user_name": profile.get("first_name") or username,
        "age_group": age_group,
        "user_profile": profile,
        "session_token": token,
    })

def show_session_expiry_warning():
    """Warn user when session is close to expiring."""
    token = st.session_state.get("session_token")
    if not token:
        return

    try:
        sess = load_sessions().get(token)
        if not sess:
            return
        created_str = sess.get("created_at")
        created_dt = datetime.datetime.fromisoformat(created_str)
        minutes_used = (datetime.datetime.now() - created_dt).total_seconds() / 60
        if 30 <= minutes_used < SESSION_TTL_MINUTES:
            st.info(
                "⚠️ Session will expire after 40 minutes. "
                "Please save your reflection soon."
            )
    except Exception:
        pass

def logout_user():
    token = st.session_state.get("session_token")
    if token:
        sessions = load_sessions()
        sessions.pop(token, None)
        save_sessions(sessions)

    st.session_state.clear()
    st.session_state["role"] = "guest"

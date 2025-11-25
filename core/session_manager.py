import datetime
import streamlit as st
from database import load_sessions, save_sessions, SESSION_TTL_MINUTES

def restore_session():
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

    try:
        created_dt = datetime.datetime.fromisoformat(sess["created_at"])
        expired = (
            datetime.datetime.now() - created_dt
            > datetime.timedelta(minutes=SESSION_TTL_MINUTES)
        )
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
            "session_token": token,
        })
        return

    from auth import load_users
    users = load_users()
    profile = users.get(username)
    if not profile:
        return

    year = profile.get("year_of_birth")
    age_group = None
    if isinstance(year, int):
        age_group = "adult" if (datetime.datetime.now().year - year) >= 22 else "child"

    st.session_state.update({
        "role": "user",
        "user_name": profile.get("first_name") or username,
        "age_group": age_group,
        "user_profile": profile,
        "session_token": token,
    })

def handle_logout():
    token = st.session_state.get("session_token")
    if token:
        sessions = load_sessions()
        sessions.pop(token, None)
        save_sessions(sessions)

    st.session_state.clear()
    st.session_state["role"] = "guest"
    st.rerun()

"""
admin_module.py

This module contains ALL admin panel UI from your original app.py:
- Books & indexing
- Approved practices
- Practice approval
- Guidance upload
- Daily reflection admin
- Internet search admin
- Feedback admin

Behaviour is 100% preserved.
"""

import os
import subprocess
import streamlit as st

from database import (
    list_book_names,
    load_unreadable,
    load_approved_practices,
    save_approved_practices,
    load_practice_candidates,
    save_practice_candidates,
    load_sessions,
    save_sessions,
    SESSION_TTL_MINUTES,
)
from admin_tools import (
    scan_practice_candidates_from_chroma,
    fetch_online_practices,
)

from practices_module import (
    get_practice_candidates,
    approve_selected_candidates,
    filter_candidates_by_books,
    meditation_band,
    mantra_band,
    get_approved,
    update_approved_list,
)
from guidance_module import (
    save_meditation_guidance,
    save_mantra_guidance,
)

from feedback_module import (
    load_feedback,
    save_feedback,
)

from reflection_module import (
    get_daily_reflection,
)

# If app uses directories for uploads
BOOKS_DIR = "books"
os.makedirs(BOOKS_DIR, exist_ok=True)

# ----------------------------------------
# MAIN ENTRY POINT
# ----------------------------------------

def render_admin_panel():
    """Admin view router (top radio button decides which screen to show)."""

    admin_view = st.radio(
        "Admin panel:",
        [
            "Books & indexing",
            "Approved practices",
            "Practice approval (candidates)",
            "Guidance",
            "Daily reflection",
            "Internet search",
            "Feedback collection",
        ],
        horizontal=True,
        key="admin_view_mode",
    )

    if admin_view == "Books & indexing":
        render_books_indexing_panel()

    elif admin_view == "Approved practices":
        render_approved_practices_panel()

    elif admin_view == "Practice approval (candidates)":
        render_practice_approval_panel()

    elif admin_view == "Guidance":
        render_guidance_panel()

    elif admin_view == "Daily reflection":
        render_daily_reflection_panel()

    elif admin_view == "Internet search":
        render_internet_search_panel()

    elif admin_view == "Feedback collection":
        render_feedback_panel()

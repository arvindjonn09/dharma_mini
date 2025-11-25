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


# ============================================================
#  B O O K S   &   I N D E X I N G
# ============================================================

def render_books_indexing_panel():
    st.subheader("📚 Books & indexing")

    st.write(
        "Upload new PDF/EPUB books. They are stored in the server's `books/` folder.\n"
        "After uploading, click **Reindex books now** to parse and update the database."
    )

    # --------------------------
    # 1) Upload new books
    # --------------------------
    uploaded_books = st.file_uploader(
        "Upload one or more books (PDF / EPUB)",
        type=["pdf", "epub"],
        accept_multiple_files=True,
        key="admin_books_uploader",
    )

    if uploaded_books and st.button("📥 Save uploaded books", key="save_uploaded_books"):
        saved_files = []

        for f in uploaded_books:
            original_name = os.path.basename(f.name)
            if not original_name:
                continue

            base, ext = os.path.splitext(original_name)
            if not ext:
                ext = ".pdf"

            dest_path = os.path.join(BOOKS_DIR, original_name)

            # Avoid overwrite
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(BOOKS_DIR, f"{base}_{counter}{ext}")
                counter += 1

            with open(dest_path, "wb") as out:
                out.write(f.getbuffer())

            saved_files.append(os.path.basename(dest_path))

        if saved_files:
            st.success(f"Saved {len(saved_files)}: {', '.join(saved_files)}")
            st.info("Click **Reindex books now** next.")

    st.markdown("---")

    # --------------------------
    # 2) Reindex
    # --------------------------
    if st.button("🔄 Reindex books now", key="admin_reindex"):
        with st.spinner("Reindexing..."):
            try:
                result = subprocess.run(
                    ["python3", "prepare_data.py"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                st.success("Reindexing completed.")

                if result.stdout:
                    st.text_area("stdout", result.stdout, height=200)
                if result.stderr:
                    st.text_area("stderr", result.stderr, height=200)

                st.cache_data.clear()
                st.cache_resource.clear()

            except subprocess.CalledProcessError as e:
                st.error("Reindex failed.")
                st.text_area("error", e.stderr or str(e), height=200)

    st.markdown("---")

    # --------------------------
    # 3) Unreadable books
    # --------------------------
    unreadable = load_unreadable()
    if unreadable:
        st.warning("Unreadable books:")
        for path, reason in unreadable.items():
            st.write(f"- `{os.path.basename(path)}` — {reason}")

    # --------------------------
    # 4) List all books
    # --------------------------
    book_list = list_book_names()
    if book_list:
        with st.expander("Books available"):
            for b in book_list:
                st.write("•", b)
    else:
        st.info("No books found in `books/`.")

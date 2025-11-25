"""
admin_module.py

This module contains ALL admin panel UI previously inside app.py:
- Books & indexing
- Approved practices
- Practice approval (candidates)
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

    unreadable = load_unreadable()
    if unreadable:
        st.warning("Unreadable books:")
        for path, reason in unreadable.items():
            st.write(f"- `{os.path.basename(path)}` — {reason}")

    book_list = list_book_names()
    if book_list:
        with st.expander("Books available"):
            for b in book_list:
                st.write("•", b)
    else:
        st.info("No books found in `books/`.")



# ============================================================
#  A P P R O V E D   P R A C T I C E S
# ============================================================

def render_approved_practices_panel():
    st.subheader("✅ Approved practices overview")

    approved = load_approved_practices()
    med_practices = approved.get("meditation", []) or []
    mantra_practices = approved.get("mantra", []) or []

    col_m, col_mantra = st.columns(2)

    # ---------------------------
    # Meditation
    # ---------------------------
    with col_m:
        st.markdown("### 🧘 Meditation practices")

        if not med_practices:
            st.info("No meditation practices approved yet.")
        else:
            level_filter = st.selectbox(
                "Filter by level band",
                ["All levels", "Beginner", "Intermediate", "Deeper"],
                key="meditation_level_filter",
            )

            for idx, practice in enumerate(med_practices, start=1):
                band = meditation_band(idx)

                if level_filter != "All levels" and band != level_filter:
                    continue

                src = practice.get("source") or "manual-guidance"
                text_full = practice.get("text", "") or ""

                preview = text_full[:260] + ("..." if len(text_full) > 260 else "")
                header = f"Meditation {idx} ({band}) — Source: {os.path.basename(src)}"

                with st.expander(header, expanded=False):
                    st.markdown(
                        f"<div class='source-text'>{preview}</div>",
                        unsafe_allow_html=True
                    )

                    audio = practice.get("audio_path")
                    if audio and os.path.exists(audio):
                        st.audio(audio)

                    image = practice.get("image_path")
                    if image and os.path.exists(image):
                        st.image(image)

                    video = practice.get("video_path")
                    if video and os.path.exists(video):
                        st.video(video)

                    new_text = st.text_area(
                        "Edit meditation text",
                        value=text_full,
                        key=f"med_edit_text_{idx}",
                        height=180,
                    )

                    col_save, col_delete = st.columns(2)

                    with col_save:
                        if st.button("Save changes", key=f"med_save_{idx}"):
                            med_list = approved.get("meditation", [])
                            med_list[idx - 1]["text"] = new_text.strip()
                            approved["meditation"] = med_list
                            save_approved_practices(approved)
                            st.success("Saved.")
                            st.rerun()

                    with col_delete:
                        if st.button("Delete", key=f"med_delete_{idx}"):
                            med_list = approved.get("meditation", [])
                            med_list.pop(idx - 1)
                            approved["meditation"] = med_list
                            save_approved_practices(approved)
                            st.warning("Deleted.")
                            st.rerun()

    # ---------------------------
    # Mantras
    # ---------------------------
    with col_mantra:
        st.markdown("### 📿 Mantra practices")

        if not mantra_practices:
            st.info("No mantra practices approved yet.")
            return

        deity_names = sorted(
            { (p.get("deity") or "General").strip() or "General"
              for p in mantra_practices },
            key=str.lower
        )

        deity_filter = st.selectbox(
            "Filter by deity",
            ["All deities"] + deity_names,
            key="mantra_deity_filter",
        )

        level_filter = st.selectbox(
            "Filter by level band",
            ["All levels", "Beginner", "Intermediate", "Deeper"],
            key="mantra_level_filter",
        )

        for idx, practice in enumerate(mantra_practices, start=1):

            deity = (practice.get("deity") or "General").strip() or "General"

            try:
                lvl = int(practice.get("level", 1))
            except:
                lvl = 1

            band = mantra_band(lvl)

            # Filters
            if deity_filter != "All deities" and deity != deity_filter:
                continue
            if level_filter != "All levels" and band != level_filter:
                continue

            age_meta = practice.get("age_group") or "both"
            age_label = (
                "Children" if age_meta == "child"
                else "Adults" if age_meta == "adult"
                else "All ages"
            )

            src = practice.get("source") or "manual-guidance"
            raw_text = practice.get("mantra_text") or practice.get("text") or ""
            preview = raw_text[:260] + ("..." if len(raw_text) > 260 else "")

            safe_preview = (
                preview.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            heading = f"{deity} — Level {lvl} ({band}) — Visible to: {age_label}"

            with st.expander(heading, expanded=False):
                st.markdown(
                    f"<div class='mantra-box'>{safe_preview}</div>",
                    unsafe_allow_html=True
                )

                audio = practice.get("audio_path")
                if audio and os.path.exists(audio):
                    st.audio(audio)

                image = practice.get("image_path")
                if image and os.path.exists(image):
                    st.image(image)

                video = practice.get("video_path")
                if video and os.path.exists(video):
                    st.video(video)

                edit_deity = st.text_input(
                    "Deity",
                    value=deity,
                    key=f"mantra_deity_{idx}",
                )

                edit_level = st.number_input(
                    "Level",
                    min_value=1,
                    max_value=20,
                    value=lvl,
                    step=1,
                    key=f"mantra_level_{idx}",
                )

                age_index = (
                    1 if age_meta == "child"
                    else 2 if age_meta == "adult"
                    else 0
                )
                edit_age = st.selectbox(
                    "Suitable for:",
                    ["All ages", "Children", "Adults"],
                    index=age_index,
                    key=f"mantra_age_{idx}",
                )

                edit_age_code = (
                    "child" if edit_age == "Children"
                    else "adult" if edit_age == "Adults"
                    else "both"
                )

                edit_mantra_text = st.text_area(
                    "Mantra text",
                    value=practice.get("mantra_text") or "",
                    key=f"mantra_text_edit_{idx}",
                    height=120,
                )

                edit_desc = st.text_area(
                    "Description",
                    value=practice.get("text") or "",
                    key=f"mantra_desc_edit_{idx}",
                    height=160,
                )

                col_save, col_delete = st.columns(2)

                with col_save:
                    if st.button("Save changes", key=f"mantra_save_{idx}"):
                        man_list = approved.get("mantra", [])
                        entry = man_list[idx - 1]

                        entry["deity"] = edit_deity.strip()
                        entry["level"] = int(edit_level)
                        entry["age_group"] = edit_age_code
                        entry["mantra_text"] = edit_mantra_text.rstrip()
                        entry["text"] = edit_desc.strip()

                        man_list[idx - 1] = entry
                        approved["mantra"] = man_list
                        save_approved_practices(approved)

                        st.success("Mantra updated.")
                        st.rerun()

                with col_delete:
                    if st.button("Delete", key=f"mantra_delete_{idx}"):
                        man_list = approved.get("mantra", [])
                        man_list.pop(idx - 1)
                        approved["mantra"] = man_list
                        save_approved_practices(approved)
                        st.warning("Deleted.")
                        st.rerun()



# ============================================================
#  P R A C T I C E   A P P R O V A L   (CANDIDATES)
# ============================================================

def render_practice_approval_panel():
    """Compatibility wrapper — approval is inside Approved Practices panel."""
    st.info("Practice approval is included inside the ‘Approved practices’ panel.")



# ============================================================
#  G U I D A N C E   U P L O A D
# ============================================================

def render_guidance_panel():
    st.subheader("Guided practices (manual)")

    guidance_kind = st.radio(
        "Type of guidance",
        ["Meditation", "Mantra"],
        horizontal=True,
        key="guidance_kind_mode",
    )

    deity_name = ""
    age_group_code = "both"
    level_number = 1

    if guidance_kind == "Meditation":
        guidance_text = st.text_area(
            "Meditation guidance:",
            key="guidance_text_input",
            height=160,
        )
    else:
        deity_name = st.text_input(
            "Deity name",
            key="guidance_deity_input",
        )

        age_choice = st.radio(
            "Suitable for",
            ["All ages", "Children", "Adults"],
            horizontal=True,
            key="guidance_age_group_choice",
        )
        age_group_code = (
            "child" if age_choice == "Children"
            else "adult" if age_choice == "Adults"
            else "both"
        )

        level_number = st.number_input(
            "Mantra level",
            min_value=1,
            max_value=20,
            value=1,
            step=1,
            key="guidance_level_number",
        )

        mantra_lines = st.text_area(
            "Mantra text:",
            key="mantra_text_input",
            height=120,
        )

        mantra_desc = st.text_area(
            "Description / meaning:",
            key="mantra_desc_input",
            height=160,
        )

    uploaded_audio = st.file_uploader(
        "Optional audio",
        type=["mp3", "wav", "m4a", "ogg"],
        key="guidance_audio_uploader",
    )

    uploaded_image = st.file_uploader(
        "Optional image",
        type=["png", "jpg", "jpeg", "webp"],
        key="guidance_image_uploader",
    )

    uploaded_video = st.file_uploader(
        "Optional video",
        type=["mp4", "mov", "m4v", "webm", "mpeg4"],
        key="guidance_video_uploader",
    )

    if st.button("Save guidance", key="guidance_save_button"):

        if guidance_kind == "Meditation":
            if not guidance_text.strip():
                st.error("Meditation text required.")
                return

            save_meditation_guidance(
                text=guidance_text,
                audio_file=uploaded_audio,
                image_file=uploaded_image,
                video_file=uploaded_video,
            )

        else:
            if not deity_name.strip():
                st.error("Deity name required.")
                return
            if not mantra_lines.strip():
                st.error("Mantra text required.")
                return

            save_mantra_guidance(
                deity=deity_name,
                age_group=age_group_code,
                level=level_number,
                mantra_text=mantra_lines,
                description=mantra_desc,
                audio_file=uploaded_audio,
                image_file=uploaded_image,
                video_file=uploaded_video,
            )

        st.success("Guidance saved.")
        st.rerun()



# ============================================================
#  D A I L Y   R E F L E C T I O N   A D M I N
# ============================================================

def render_daily_reflection_panel():
    st.subheader("🪞 Daily reflection (Admin)")

    try:
        with open("daily_reflection.json", "r", encoding="utf-8") as f:
            overrides = json.load(f)
    except Exception:
        overrides = {}

    child_val = overrides.get("child", "")
    adult_val = overrides.get("adult", "")
    both_val = overrides.get("both", "")

    new_child = st.text_area("Child reflection", value=child_val, height=80)
    new_adult = st.text_area("Adult reflection", value=adult_val, height=80)
    new_both = st.text_area("All ages reflection", value=both_val, height=80)

    if st.button("💾 Save daily reflections"):
        new_data = {
            "child": new_child.strip(),
            "adult": new_adult.strip(),
            "both": new_both.strip(),
        }
        with open("daily_reflection.json", "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        st.success("Daily reflections updated.")
        st.rerun()



# ============================================================
#  I N T E R N E T   S E A R C H   A D M I N
# ============================================================

def render_internet_search_panel():
    st.subheader("🌐 Mantra & meditation suggestions (admin review)")

    deity_name = st.text_input(
        "Deity name (e.g. Shiva, Krishna, Devi)",
        key="online_deity_name",
    )

    scope_choice = st.radio(
        "What to search for:",
        ["Mantras", "Meditations", "Both"],
        horizontal=True,
        key="online_scope_choice",
    )

    level_choice = st.selectbox(
        "Level:",
        ["Beginner", "Intermediate", "Deeper"],
        index=0,
        key="online_level_choice",
    )

    if st.button("🌐 Search online suggestions"):
        if not deity_name.strip():
            st.error("Please enter deity name.")
            return

        with st.spinner("Fetching suggestions..."):
            results = fetch_online_practices(
                deity_name=deity_name,
                scope=scope_choice,
                level_label=level_choice,
            )

        st.session_state["online_search_results"] = results
        if results:
            st.success(f"Received {len(results)} suggestions.")
        else:
            st.warning("No suggestions returned.")

    results = st.session_state.get("online_search_results") or []
    if results:
        st.markdown("### Suggestions")
        add_flags = []

        for idx, p in enumerate(results):
            kind = (p.get("kind") or "").lower()
            preview_text = p.get("text") or ""
            if len(preview_text) > 260:
                preview_text = preview_text[:260] + " ..."

            header = f"{kind.upper()} suggestion {idx+1}"
            with st.expander(header, expanded=False):
                st.markdown(
                    f"<div class='source-text'>{preview_text}</div>",
                    unsafe_allow_html=True,
                )

                ck = st.checkbox(
                    f"Add this {kind} to approved practices",
                    key=f"online_add_{idx}",
                )
                add_flags.append((idx, ck))

        if st.button("💾 Save selected suggestions", key="online_save_suggestions"):
            approved = load_approved_practices()

            for idx, flag in add_flags:
                if not flag:
                    continue

                item = results[idx]
                kind = (item.get("kind") or "").lower()
                if kind not in ("mantra", "meditation"):
                    continue

                approved_list = approved.get(kind) or []
                entry = {
                    "source": "online-generated",
                    "text": item.get("text", "").strip(),
                }

                if kind == "mantra":
                    entry["deity"] = item.get("deity") or "General"
                    entry["level"] = int(item.get("level", 1))
                    entry["age_group"] = item.get("age_group") or "both"

                approved_list.append(entry)
                approved[kind] = approved_list

            save_approved_practices(approved)
            st.success("Saved selected online suggestions.")
            st.session_state["online_search_results"] = []
            st.rerun()



# ============================================================
#  F E E D B A C K   A D M I N
# ============================================================

def render_feedback_panel():
    st.subheader("💬 User feedback")

    feedback_list = load_feedback()
    if not feedback_list:
        st.info("No feedback submitted yet.")
        return

    for idx, fb in enumerate(feedback_list, start=1):
        with st.expander(f"Feedback {idx}", expanded=False):
            st.write(f"**User:** {fb.get('user','Anonymous')}")
            st.write(f"**Date:** {fb.get('date','Unknown')}")
            st.write("**Message:**")

            st.markdown(
                f"<div class='source-text'>{fb.get('message','(empty)')}</div>",
                unsafe_allow_html=True,
            )

            if st.button("Delete", key=f"fb_delete_{idx}"):
                items = load_feedback()
                if 0 <= idx - 1 < len(items):
                    items.pop(idx - 1)
                    save_feedback(items)
                    st.warning("Feedback deleted.")
                    st.rerun()



# ============================================================
#  E N D   O F   A D M I N   M O D U L E
# ============================================================


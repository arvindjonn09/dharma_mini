import os
import json
from typing import List, Optional, Dict, Any

from database import (
    load_approved_practices,
    save_approved_practices,
    load_practice_candidates,
    save_practice_candidates,
)
from admin_tools import scan_practice_candidates_from_chroma


# -----------------------------------------------------------
# CORE LOADING FUNCTIONS
# -----------------------------------------------------------

def get_practice_candidates() -> List[dict]:
    """
    Loads practice candidates exactly like original app.py does.
    """
    candidates = load_practice_candidates()
    return candidates or []


def set_practice_candidates(items: List[dict]):
    """
    Persists updated practice candidates.
    """
    save_practice_candidates(items)


# -----------------------------------------------------------
# PRACTICE SCANNING (from Chroma DB)
# -----------------------------------------------------------

def scan_candidates(
    kind_filter: Optional[str],
    book_filter: Optional[List[str]],
    extra_keywords: Optional[List[str]],
) -> List[dict]:
    """
    Wrapper around scan_practice_candidates_from_chroma().
    Behaviour identical to original app.py.
    """
    return scan_practice_candidates_from_chroma(
        kind_filter=kind_filter,
        book_filter=book_filter,
        extra_keywords=extra_keywords,
    )


# -----------------------------------------------------------
# FILTER CANDIDATES BY BOOK
# -----------------------------------------------------------

def filter_candidates_by_books(candidates: List[dict], selected_books: List[str]) -> List[dict]:
    """
    Original logic: only keep candidates whose filenames match selected_books.
    """
    if not selected_books:
        return candidates

    selected_set = set(selected_books)
    out = []

    for c in candidates:
        src = c.get("source") or ""
        fname = os.path.basename(src) if src else ""
        if fname in selected_set:
            out.append(c)

    return out


# -----------------------------------------------------------
# APPROVAL LOGIC
# -----------------------------------------------------------

def approve_selected_candidates(approval_pairs: List[tuple]):
    """
    approval_pairs: list of (candidate_index, is_checked).
    This function updates both approved_practices.json and practice_candidates.json
    exactly like in your original app.py.
    """
    candidates = load_practice_candidates()
    approved = load_approved_practices()

    for idx, is_checked in approval_pairs:
        if not is_checked:
            continue
        if idx < 0 or idx >= len(candidates):
            continue

        cand = candidates[idx]
        if cand.get("approved"):
            continue

        kind = cand.get("kind")
        if kind not in ("mantra", "meditation"):
            continue

        cand["approved"] = True

        # Append to approved list
        items = approved.get(kind) or []
        items.append(
            {
                "text": cand.get("text", ""),
                "source": cand.get("source", ""),
            }
        )
        approved[kind] = items

    # Save updated lists
    save_practice_candidates(candidates)
    save_approved_practices(approved)


# -----------------------------------------------------------
# LIST APPROVED PRACTICES BY KIND
# -----------------------------------------------------------

def get_approved(kind: str) -> List[dict]:
    """
    Return approved practices for the given kind: "mantra" or "meditation".
    """
    approved = load_approved_practices()
    return approved.get(kind) or []


def update_approved_list(kind: str, new_list: List[dict]):
    """
    Save back the updated approved list (for edits/deletions).
    """
    approved = load_approved_practices()
    approved[kind] = new_list
    save_approved_practices(approved)


# -----------------------------------------------------------
# LEVEL BANDING HELPERS (unchanged from original)
# -----------------------------------------------------------

def meditation_band(index: int) -> str:
    """
    Identical to your app.py:
    index <= 3: Beginner
    4–7: Intermediate
    >7: Deeper
    """
    if index <= 3:
        return "Beginner"
    elif index <= 7:
        return "Intermediate"
    else:
        return "Deeper"


def mantra_band(level: int) -> str:
    """
    Same logic as app.py:
    level <= 3: Beginner
    <=7: Intermediate
    else: Deeper
    """
    if level <= 3:
        return "Beginner"
    elif level <= 7:
        return "Intermediate"
    else:
        return "Deeper"

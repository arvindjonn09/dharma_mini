import json
import datetime
import streamlit as st

DAILY_REFLECTION_FILE = "daily_reflection.json"


# -----------------------------------------------------------
# LOAD OVERRIDES
# -----------------------------------------------------------
def _load_reflection_overrides():
    """Load the admin-defined reflection overrides, if any."""
    try:
        with open(DAILY_REFLECTION_FILE, "r", encoding="utf-8") as f:
            overrides = json.load(f)
        if isinstance(overrides, dict):
            return overrides
        return {}
    except Exception:
        return {}


# -----------------------------------------------------------
# GET DAILY REFLECTION (MAIN PUBLIC FUNCTION)
# -----------------------------------------------------------
def get_daily_reflection(age_group: str):
    """
    Returns a gentle reflection for today.
    Behaviour is 100% identical to your original app.py.
    """

    # 1) Load admin-specified overrides
    overrides = _load_reflection_overrides()

    # Age-specific overrides
    if age_group == "child" and overrides.get("child"):
        return overrides["child"]
    if age_group == "adult" and overrides.get("adult"):
        return overrides["adult"]
    if overrides.get("both"):
        return overrides["both"]

    # 2) Static reflections (same as original)
    adult_reflections = [
        "Pause once today and remember: every small act of kindness can be placed at the Lord's feet like a flower.",
        "When the mind becomes restless, gently return to the breath and recall one quality of your chosen deity.",
        "Before sleep, think of one moment today where you could have been softer. Offer that moment into inner light.",
        "Wherever you are today, imagine you are standing in a sacred space. Speak and act as if the Divine is listening.",
        "If worry arises, quietly say: 'I am not alone in this. May I act with dharma and trust.'",
    ]

    child_reflections = [
        "Can you share something today and imagine you are sharing it with God?",
        "If you feel angry today, take three slow breaths and think of your favourite form of the Divine smiling at you.",
        "Try to tell the truth today even in small things. Saints smile when you are honest.",
        "Before you sleep, thank the Divine for one happy moment from your day.",
        "When you see someone sad today, can you say one kind word for them in your heart?",
    ]

    # 3) Pick today's reflection (same algorithm)
    today = datetime.date.today()
    idx = today.toordinal()

    if age_group == "child":
        items = child_reflections
    else:
        items = adult_reflections

    return items[idx % len(items)]

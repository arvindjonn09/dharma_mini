import json

FEEDBACK_FILE = "feedback.json"


def load_feedback():
    """
    Load all user feedback entries.
    Behaviour is identical to your original app.py.
    """
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except FileNotFoundError:
        return []
    except Exception:
        return []


def save_feedback(items):
    """
    Save all feedback entries back to disk.
    Same behaviour as original app.py.
    """
    try:
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except Exception:
        # Silent fail (matching original behaviour)
        pass

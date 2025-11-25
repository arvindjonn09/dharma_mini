import os
import datetime

from database import (
    GUIDANCE_AUDIO_DIR,
    GUIDANCE_MEDIA_DIR,
    load_approved_practices,
    save_approved_practices,
)


# -----------------------------------------------------------
# INTERNAL FILE-SAVE HELPERS
# -----------------------------------------------------------

def _save_uploaded_file(upload, base_prefix: str, directory: str):
    """
    Saves uploaded audio/image/video using the same logic from your original app.py:
    - timestamped filenames
    - spaces replaced with underscores
    """
    if upload is None:
        return None, None

    try:
        original_name = upload.name
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = original_name.replace(" ", "_")
        filename = f"{base_prefix}_{ts}_{safe_name}"
        dest_path = os.path.join(directory, filename)

        with open(dest_path, "wb") as f:
            f.write(upload.getbuffer())

        return dest_path, original_name
    except Exception:
        return None, None


# -----------------------------------------------------------
# SAVE MEDITATION GUIDANCE
# -----------------------------------------------------------

def save_meditation_guidance(text: str, audio_file, image_file, video_file):
    """
    Saves meditation guidance exactly the same way as your original app.py.
    """
    # Save media files
    audio_path, audio_orig = _save_uploaded_file(audio_file, "meditation", GUIDANCE_AUDIO_DIR)
    image_path, image_orig = _save_uploaded_file(image_file, "meditation_img", GUIDANCE_MEDIA_DIR)
    video_path, video_orig = _save_uploaded_file(video_file, "meditation_vid", GUIDANCE_MEDIA_DIR)

    # Load existing practices
    approved = load_approved_practices()
    med_list = approved.get("meditation") or []

    entry = {
        "source": "manual-guidance",
        "text": text.strip(),
    }

    if audio_path:
        entry["audio_path"] = audio_path
        entry["audio_original_name"] = audio_orig

    if image_path:
        entry["image_path"] = image_path
        entry["image_original_name"] = image_orig

    if video_path:
        entry["video_path"] = video_path
        entry["video_original_name"] = video_orig

    # Append and save
    med_list.append(entry)
    approved["meditation"] = med_list
    save_approved_practices(approved)


# -----------------------------------------------------------
# SAVE MANTRA GUIDANCE
# -----------------------------------------------------------

def save_mantra_guidance(
    deity: str,
    age_group: str,
    level: int,
    mantra_text: str,
    description: str,
    audio_file,
    image_file,
    video_file,
):
    """
    Fully mirrors mantra guidance saving in your original app.py.
    """

    # Save media files
    audio_path, audio_orig = _save_uploaded_file(audio_file, "mantra", GUIDANCE_AUDIO_DIR)
    image_path, image_orig = _save_uploaded_file(image_file, "mantra_img", GUIDANCE_MEDIA_DIR)
    video_path, video_orig = _save_uploaded_file(video_file, "mantra_vid", GUIDANCE_MEDIA_DIR)

    # Load existing
    approved = load_approved_practices()
    mantra_list = approved.get("mantra") or []

    entry = {
        "source": "manual-guidance",
        "deity": deity.strip(),
        "age_group": age_group,
        "level": int(level),
        "mantra_text": mantra_text.rstrip(),
        "text": description.strip(),
    }

    if audio_path:
        entry["audio_path"] = audio_path
        entry["audio_original_name"] = audio_orig

    if image_path:
        entry["image_path"] = image_path
        entry["image_original_name"] = image_orig

    if video_path:
        entry["video_path"] = video_path
        entry["video_original_name"] = video_orig

    # Save
    mantra_list.append(entry)
    approved["mantra"] = mantra_list
    save_approved_practices(approved)

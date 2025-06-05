"""Tone mirroring and fallback helpers."""

from typing import Literal

Tone = Literal["hesitant", "confident", "overwhelmed", "neutral"]


def mirror_tone(user_tone: Tone) -> str:
    """Return Ava's tone based on user tone."""
    mapping = {
        "hesitant": "warm",
        "confident": "snappy",
        "overwhelmed": "soft",
    }
    return mapping.get(user_tone, "neutral")


def fallback_response() -> str:
    """Generic soft exit used when no module matches."""
    return "Totally. I can text you some options if that's easier."

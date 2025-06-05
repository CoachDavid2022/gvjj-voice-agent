"""Helpers for booking and follow-up actions."""

from __future__ import annotations

from typing import List, Dict
from . import twilio_bridge


# --- Booking handlers ---------------------------------------------------

def get_availability() -> List[str]:
    """Return mockable availability slots."""
    return ["Tuesday 4:30", "Thursday 6:00"]


def create_booking(slot: str, lead_name: str) -> Dict[str, str]:
    """Create a booking record (placeholder implementation)."""
    return {"slot": slot, "lead": lead_name, "status": "confirmed"}


# --- Follow-up helpers --------------------------------------------------

def send_followup_sms(to_number: str, message: str) -> str:
    """Send a follow-up SMS via Twilio or the mock interface."""
    sid = twilio_bridge.send_sms(to_number, message)
    return sid or "mock-sid"


def schedule_callback(to_number: str, day: str) -> Dict[str, str]:
    """Schedule a callback (stub for Zapier or CRM)."""
    return {"number": to_number, "day": day, "status": "scheduled"}

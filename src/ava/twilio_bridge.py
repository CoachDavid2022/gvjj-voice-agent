"""Lightweight wrapper around the Twilio client with optional mock fallback."""

from __future__ import annotations

import logging
import os
from typing import Optional
import importlib.util
from pathlib import Path

try:
    from twilio.rest import Client  # type: ignore
except Exception:  # Twilio may not be installed
    Client = None

try:
    from . import twilio_mock
except Exception:  # pragma: no cover - allow import when run as script
    _p = Path(__file__).resolve().parent / "twilio_mock.py"
    spec = importlib.util.spec_from_file_location("twilio_mock", _p)
    twilio_mock = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(twilio_mock)


def _get_client() -> Optional["Client"]:
    """Return a Twilio Client or ``None`` if credentials/library missing."""
    if os.getenv("USE_TWILIO_MOCK", "false").lower() == "true":
        return None
    if Client is None:
        logging.warning("Twilio library not available; falling back to mock.")
        return None
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        logging.error("Twilio credentials missing; set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
        return None
    return Client(sid, token)


def send_sms(to_number: str, body: str, from_number: str | None = None) -> str | None:
    """Send an SMS using Twilio or the mock implementation."""
    client = _get_client()
    if client is None:
        return twilio_mock.send_sms(to_number, body, from_number)
    from_number = from_number or os.getenv("TWILIO_FROM_NUMBER")
    if not from_number:
        logging.error("TWILIO_FROM_NUMBER not set; using mock sender")
        return twilio_mock.send_sms(to_number, body, from_number)
    msg = client.messages.create(to=to_number, from_=from_number, body=body)
    return msg.sid


def make_call(to_number: str, from_number: str | None = None, twiml_url: str | None = None) -> str | None:
    """Initiate a voice call via Twilio or the mock implementation."""
    client = _get_client()
    if client is None:
        return twilio_mock.make_call(to_number, from_number, twiml_url)
    from_number = from_number or os.getenv("TWILIO_FROM_NUMBER")
    twiml_url = twiml_url or os.getenv("TWILIO_TWIML_URL")
    if not from_number or not twiml_url:
        logging.error("TWILIO_FROM_NUMBER or TWILIO_TWIML_URL missing; using mock caller")
        return twilio_mock.make_call(to_number, from_number, twiml_url)
    call = client.calls.create(to=to_number, from_=from_number, url=twiml_url)
    return call.sid

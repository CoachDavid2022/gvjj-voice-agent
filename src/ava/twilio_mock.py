import logging

def send_sms(to_number: str, body: str, from_number: str | None = None) -> str:
    """Mock SMS sender that logs the message."""
    logging.info("[MOCK SMS] to=%s from=%s body=%s", to_number, from_number, body)
    return "mock-sms-id"


def make_call(to_number: str, from_number: str | None = None, twiml_url: str | None = None) -> str:
    """Mock call initiator that logs the call details."""
    logging.info("[MOCK CALL] to=%s from=%s url=%s", to_number, from_number, twiml_url)
    return "mock-call-id"

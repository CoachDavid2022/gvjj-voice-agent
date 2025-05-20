# Integration Notes

## Twilio Bridge
- Added `src/ava/twilio_bridge.py` as a lightweight wrapper around the Twilio REST client.
- Fallback to `src/ava/twilio_mock.py` when the library or credentials are missing or `USE_TWILIO_MOCK=true`.
- `ModuleManager.log_interaction` now sends an SMS summary when environment variable `ENABLE_TWILIO_NOTIFICATIONS` is set to `"true"`.
  - Destination number read from `NOTIFY_NUMBER` environment variable.

## CRM Stub
- Created `src/ava/crm_bridge.py` with `update_contact_status` placeholder.

## Assumptions & TODOs
- Real Twilio credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`) and `TWILIO_TWIML_URL` must be provided in the environment for production use.
- CRM integration requires implementation in `crm_bridge.py`.

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ava import booking_utils


class TestBookingUtils(unittest.TestCase):
    def test_get_availability(self):
        slots = booking_utils.get_availability()
        self.assertEqual(len(slots), 2)

    def test_create_booking(self):
        result = booking_utils.create_booking("Tuesday 4:30", "Sam")
        self.assertEqual(result["status"], "confirmed")

    def test_send_followup_sms(self):
        sid = booking_utils.send_followup_sms("+10000000000", "Hi")
        self.assertTrue(sid)

    def test_schedule_callback(self):
        cb = booking_utils.schedule_callback("+10000000000", "Friday")
        self.assertEqual(cb["status"], "scheduled")


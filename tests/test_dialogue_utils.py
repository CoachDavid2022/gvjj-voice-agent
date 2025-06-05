import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ava import dialogue_utils


class TestDialogueUtils(unittest.TestCase):
    def test_mirror_tone(self):
        self.assertEqual(dialogue_utils.mirror_tone("hesitant"), "warm")
        self.assertEqual(dialogue_utils.mirror_tone("confident"), "snappy")
        self.assertEqual(dialogue_utils.mirror_tone("overwhelmed"), "soft")
        self.assertEqual(dialogue_utils.mirror_tone("neutral"), "neutral")

    def test_fallback_response(self):
        text = dialogue_utils.fallback_response()
        self.assertIn("text", text.lower() if isinstance(text, str) else "")


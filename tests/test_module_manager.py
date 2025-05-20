import unittest
import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ava"
    / "module_manager.py"
)
spec = importlib.util.spec_from_file_location("module_manager", MODULE_PATH)
module_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_manager)
ModuleManager = module_manager.ModuleManager


class TestModuleManager(unittest.TestCase):
    def setUp(self):
        self.fallback = {
            "module_id": "AVAMOD0010",
            "title": "Fallback",
            "intent": "",
            "phase": "greeting",
            "tags": "",
            "trigger_phrases": [],
        }
        self.override = {
            "module_id": "AVAMOD0019",
            "title": "Consent",
            "intent": "",
            "phase": "",
            "tags": "consent_checked=true",
            "trigger_phrases": [],
        }
        self.regular = {
            "module_id": "AVAMOD1000",
            "title": "Booking",
            "intent": "booking",
            "phase": "booking",
            "tags": "tone_ava=neutral",
            "trigger_phrases": ["book"],
        }

    def test_dynamic_retrieval_fallback(self):
        manager = ModuleManager([self.fallback])
        selected = manager.dynamic_retrieval("hello")
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].module_id, "AVAMOD0010")
        self.assertEqual(manager.conversation_state["phase"], "greeting")

    def test_dynamic_retrieval_override(self):
        manager = ModuleManager([self.fallback, self.override])
        selected = manager.dynamic_retrieval("any input")
        self.assertEqual(selected[0].module_id, "AVAMOD0019")
        self.assertTrue(manager.conversation_state["consent_checked"])

    def test_dynamic_retrieval_updates_state(self):
        manager = ModuleManager([self.fallback, self.regular])
        selected = manager.dynamic_retrieval("I want to book")
        self.assertEqual(selected[0].module_id, "AVAMOD1000")
        self.assertEqual(manager.conversation_state["phase"], "booking")
        self.assertEqual(manager.conversation_state["current_intent"], "booking")

    def test_handle_silence_short(self):
        manager = ModuleManager([self.fallback])
        result = manager.handle_silence(3.0)
        self.assertEqual(result, [])
        self.assertEqual(manager.conversation_state["silence_duration"], 3.0)

    def test_handle_silence_long(self):
        manager = ModuleManager([self.fallback])
        result = manager.handle_silence(6.0)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].module_id, "AVAMOD0010")
        self.assertEqual(manager.conversation_state["silence_duration"], 6.0)


if __name__ == "__main__":
    unittest.main()

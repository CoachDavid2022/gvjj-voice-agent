import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ava.validate_modules import VALID_PHASES

class TestModuleValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_path = Path(__file__).resolve().parent.parent / "gvjj-voice-agent_ready for embeding" / "ava_modlist_chunks.jsonl"
        cls.modules = []
        with data_path.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    cls.modules.append(json.loads(line))

    def test_required_fields_present(self):
        required = ["module_id", "intent", "phase", "tags", "trigger_phrases", "response_snippet"]
        for mod in self.modules:
            for field in required:
                self.assertIn(field, mod, f"{mod.get('module_id')} missing {field}")
                self.assertTrue(mod[field], f"{mod.get('module_id')} empty {field}")

    def test_module_ids_unique(self):
        ids = [m["module_id"] for m in self.modules]
        self.assertEqual(len(ids), len(set(ids)), "module_id values are not unique")

    def test_phase_values_valid(self):
        for mod in self.modules:
            phase = mod.get("phase")
            self.assertIn(
                phase,
                VALID_PHASES,
                f"{mod.get('module_id')} invalid phase '{phase}'",
            )

    def test_trigger_phrases_non_empty(self):
        for mod in self.modules:
            self.assertIsInstance(mod.get("trigger_phrases"), list, f"{mod.get('module_id')} trigger_phrases not a list")
            self.assertGreater(len(mod["trigger_phrases"]), 0, f"{mod.get('module_id')} has no trigger_phrases")

    def test_tag_format_key_value(self):
        for mod in self.modules:
            tags = mod.get("tags", [])
            for tag in tags:
                self.assertRegex(tag, r"^[^=]+=.+$", f"Tag '{tag}' in {mod.get('module_id')} not key=value")

if __name__ == "__main__":
    unittest.main()

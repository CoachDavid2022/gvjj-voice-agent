import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ava import synthflow_export


class TestSynthflowExport(unittest.TestCase):
    def test_conversion(self):
        mod_path = Path(__file__).resolve().parents[1] / "gvjj-voice-agent_ready for embeding" / "ava_modlist_chunks.jsonl"
        modules = synthflow_export.load_modules(str(mod_path))
        sf = synthflow_export.convert_to_synthflow(modules)
        self.assertIsInstance(sf, list)
        self.assertGreater(len(sf), 0)
        first = sf[0]
        self.assertIn('id', first)
        self.assertIn('utterances', first)
        self.assertIsInstance(first['utterances'], list)


# module_manager.py
import time
import json
import logging
import argparse
import os
import importlib.util
from pathlib import Path

try:
    from . import twilio_bridge  # type: ignore
except Exception:  # pragma: no cover - module may be loaded outside package
    _p = Path(__file__).resolve().parent / "twilio_bridge.py"
    spec = importlib.util.spec_from_file_location("twilio_bridge", _p)
    twilio_bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(twilio_bridge)

logging.basicConfig(
    filename='module_performance.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s'
)

class Module:
    def __init__(self, mod_data):
        self.module_id = mod_data.get('module_id', '')
        self.title = mod_data.get('title', '')
        self.intent = mod_data.get('intent', '')
        self.phase = mod_data.get('phase', '')
        raw_tags = mod_data.get('tags', '')
        if isinstance(raw_tags, list):
            self.tags = {k: v for k, v in (t.split('=', 1) for t in raw_tags if '=' in t)}
        else:
            self.tags = dict(item.split('=')
                             for item in raw_tags.split(', ')
                             if '=' in item)
        self.trigger_phrases = mod_data.get('trigger_phrases', [])
        self.response = mod_data.get('response', '')
        self.fallback = mod_data.get('fallback', '')
        self.notes = mod_data.get('notes', '')

class ModuleManager:
    ORCHESTRATION_SEQ = [
        "AVAMOD0001","AVAMOD0018","AVAMOD0019",
        "AVAMOD0002","AVAMOD0003","AVAMOD0004",
        "AVAMOD0005","AVAMOD0006","AVAMOD0007",
        "AVAMOD0008","AVAMOD0009","AVAMOD0020",
        "AVAMOD0021","AVAMOD0022","AVAMOD0027",
        "AVAMOD0014","AVAMOD0015","AVAMOD0012",
        "AVAMOD0011","AVAMOD0013","AVAMOD0016",
        "AVAMOD0017","AVAMOD0025","AVAMOD0028",
        "AVAMOD0029","AVAMOD0024","AVAMOD0026",
        "AVAMOD0032","AVAMOD0033","AVAMOD0034",
        "AVAMOD0010","AVAMOD0023","AVAMOD0030",
        "AVAMOD0035NarrativeIntegrityLockPhantomWallPatch"
    ]

    def __init__(self, mod_list):
        self.modules = [Module(m) for m in mod_list]
        self.conversation_state = {
            'tone_user': 'neutral',
            'phase': 'greeting',
            'consent_checked': False,
            'silence_duration': 0.0,
            'current_intent': None
        }

    def _calculate_priority(self, m):
        w_intent = 0.4 if m.intent == self.conversation_state['current_intent'] else 0
        w_tone   = 0.3 if m.tags.get('tone_ava') == self.conversation_state['tone_user'] else 0
        w_phase  = 0.3 if m.phase == self.conversation_state['phase'] else 0
        return w_intent + w_tone + w_phase

    def _check_activation(self, m, user_input):
        if m.tags.get('consent_checked') == 'true' and not self.conversation_state['consent_checked']:
            return True
        ui = user_input.lower()
        return any(isinstance(kw, str) and kw.lower() in ui for kw in m.trigger_phrases)

    def update_state(self, m):
        if m.module_id == "AVAMOD0019":
            self.conversation_state['consent_checked'] = True
        if m.intent == "booking":
            self.conversation_state['current_intent'] = "booking"
        if m.phase in ("booking","intake","recovery","confirmation"):
            self.conversation_state['phase'] = m.phase

    def dynamic_retrieval(self, user_input):
        # override critical modules
        for t in (
            "AVAMOD0035NarrativeIntegrityLockPhantomWallPatch",
            "AVAMOD0019",
            "AVAMOD0032",
            "AVAMOD0025"):
            m = next((x for x in self.modules if x.module_id==t), None)
            if m and self._check_activation(m, user_input):
                self.update_state(m)
                return [m]
        # eligible set
        elig = [m for m in self.modules if self._check_activation(m, user_input)]
        if not elig:
            fb = next(x for x in self.modules if x.module_id=="AVAMOD0010")
            self.update_state(fb)
            return [fb]
        # score & pick top
        for m in elig:
            m.priority = self._calculate_priority(m)
        best = max(elig, key=lambda x:x.priority)
        self.update_state(best)
        return [best]

    def handle_silence(self, duration):
        self.conversation_state['silence_duration'] = duration
        if duration > 4.5:
            fb = next(x for x in self.modules if x.module_id=="AVAMOD0010")
            self.update_state(fb)
            return [fb]
        return []

    def orchestrate(self, user_input):
        hits = []
        for mid in self.ORCHESTRATION_SEQ:
            m = next((x for x in self.modules if x.module_id==mid), None)
            if m and self._check_activation(m, user_input):
                self.update_state(m)
                hits.append(m)
        if not hits:
            fb = next(x for x in self.modules if x.module_id=="AVAMOD0010")
            self.update_state(fb)
            hits.append(fb)
        return hits

    def log_interaction(self, user_input, activated_modules):
        entry = {
            'timestamp': time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            'input_hash': hash(user_input),
            'primary_module': activated_modules[0].title,
            'co_activated': [m.title for m in activated_modules[1:]],
            'phase': self.conversation_state['phase']
        }
        logging.info(json.dumps(entry))
        if os.getenv("ENABLE_TWILIO_NOTIFICATIONS") == "true":
            # Send a brief SMS summary when enabled
            summary = f"AVA phase: {self.conversation_state['phase']} | {activated_modules[0].title}"
            try:
                twilio_bridge.send_sms(os.getenv("NOTIFY_NUMBER", ""), summary)
            except Exception as exc:  # pragma: no cover - notification failures shouldn't break
                logging.error("Twilio notification failed: %s", exc)

def print_module(m):
    print(f"\n--- {m.title} ---")
    print(m.response or m.fallback or "(no response)")
    print(f"Triggers: {m.trigger_phrases}")
    print(f"Tags: {m.tags}\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        '-m',
        '--modules',
        default='gvjj-voice-agent_ready for embeding/ava_modlist_chunks.jsonl',
        help='path to module JSONL'
    )
    p.add_argument('-i','--input', help='user input text')
    p.add_argument('-o','--orchestrate', action='store_true',
                   help='full orchestration stack')
    p.add_argument('-s','--silence', type=float,
                   help='silence duration in seconds')
    args = p.parse_args()

    with open(args.modules, 'r', encoding='utf-8') as f:
        try:
            mod_list = json.load(f)
        except json.JSONDecodeError:
            f.seek(0)
            mod_list = [json.loads(line) for line in f if line.strip()]
    manager = ModuleManager(mod_list)

    if args.input:
        if args.orchestrate:
            stack = manager.orchestrate(args.input)
            print("Orchestration stack:")
            for m in stack:
                print_module(m)
            manager.log_interaction(args.input, stack)
        else:
            sel = manager.dynamic_retrieval(args.input)
            print_module(sel[0])
            manager.log_interaction(args.input, sel)

    if args.silence is not None:
        sil = manager.handle_silence(args.silence)
        for m in sil:
            print_module(m)
        if sil:
            manager.log_interaction(f"<silence:{args.silence}>", sil)

if __name__ == "__main__":
    main()

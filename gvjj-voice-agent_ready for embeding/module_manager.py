# module_manager.py
import time
import json
import logging
import argparse

logging.basicConfig(
    filename='module_performance.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s'
)

class Module:
    def __init__(self, mod_data):
        self.title = mod_data.get('title', '')
        self.intent = mod_data.get('intent', '')
        self.phase = mod_data.get('phase', '')
        self.tags = dict(item.split('=') 
                         for item in mod_data.get('tags','').split(', ') 
                         if '=' in item)
        self.trigger_phrases = mod_data.get('trigger_phrases', [])
        self.response = mod_data.get('response', '')
        self.fallback = mod_data.get('fallback', '')
        self.notes = mod_data.get('notes', '')

class ModuleManager:
    ORCHESTRATION_SEQ = [
        "AVA-MOD-0001","AVA-MOD-0018","AVA-MOD-0019",
        "AVA-MOD-0002","AVA-MOD-0003","AVA-MOD-0004",
        "AVA-MOD-0005","AVA-MOD-0006","AVA-MOD-0007",
        "AVA-MOD-0008","AVA-MOD-0009","AVA-MOD-0020",
        "AVA-MOD-0021","AVA-MOD-0022","AVA-MOD-0027",
        "AVA-MOD-0014","AVA-MOD-0015","AVA-MOD-0012",
        "AVA-MOD-0011","AVA-MOD-0013","AVA-MOD-0016",
        "AVA-MOD-0017","AVA-MOD-0025","AVA-MOD-0028",
        "AVA-MOD-0029","AVA-MOD-0024","AVA-MOD-0026",
        "AVA-MOD-0032","AVA-MOD-0033","AVA-MOD-0034",
        "AVA-MOD-0010","AVA-MOD-0023","AVA-MOD-0030",
        "AVA-MOD-0035"
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
        if m.title == "AVA-MOD-0019":
            self.conversation_state['consent_checked'] = True
        if m.intent == "booking":
            self.conversation_state['current_intent'] = "booking"
        if m.phase in ("booking","intake","recovery","confirmation"):
            self.conversation_state['phase'] = m.phase

    def dynamic_retrieval(self, user_input):
        # override critical modules
        for t in ("AVA-MOD-0035","AVA-MOD-0019","AVA-MOD-0032","AVA-MOD-0025"):
            m = next((x for x in self.modules if x.title==t), None)
            if m and self._check_activation(m, user_input):
                self.update_state(m)
                return [m]
        # eligible set
        elig = [m for m in self.modules if self._check_activation(m, user_input)]
        if not elig:
            fb = next(x for x in self.modules if x.title=="AVA-MOD-0010")
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
            fb = next(x for x in self.modules if x.title=="AVA-MOD-0010")
            self.update_state(fb)
            return [fb]
        return []

    def orchestrate(self, user_input):
        hits = []
        for title in self.ORCHESTRATION_SEQ:
            m = next((x for x in self.modules if x.title==title), None)
            if m and self._check_activation(m, user_input):
                self.update_state(m)
                hits.append(m)
        if not hits:
            fb = next(x for x in self.modules if x.title=="AVA-MOD-0010")
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

def print_module(m):
    print(f"\n--- {m.title} ---")
    print(m.response or m.fallback or "(no response)")
    print(f"Triggers: {m.trigger_phrases}")
    print(f"Tags: {m.tags}\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-m','--modules', default='modules.json',
                   help='path to module JSON')
    p.add_argument('-i','--input', help='user input text')
    p.add_argument('-o','--orchestrate', action='store_true',
                   help='full orchestration stack')
    p.add_argument('-s','--silence', type=float,
                   help='silence duration in seconds')
    args = p.parse_args()

    with open(args.modules, 'r', encoding='utf-8') as f:
        mod_list = json.load(f)
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

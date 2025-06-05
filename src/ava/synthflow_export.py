import json
import argparse
from pathlib import Path
from typing import List, Dict, Any


def load_modules(path: str) -> List[Dict[str, Any]]:
    modules: List[Dict[str, Any]] = []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            modules = json.load(f)
        except json.JSONDecodeError:
            f.seek(0)
            for line in f:
                line = line.strip()
                if line:
                    modules.append(json.loads(line))
    return modules


def convert_to_synthflow(modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sf_modules = []
    for m in modules:
        raw_tags = m.get('tags', [])
        if isinstance(raw_tags, list):
            tags = {k: v for k, v in (t.split('=', 1) for t in raw_tags if '=' in t)}
        else:
            tags = dict(item.split('=') for item in raw_tags.split(', ') if '=' in item)
        sf_modules.append({
            'id': m.get('module_id'),
            'name': m.get('title'),
            'intent': m.get('intent'),
            'phase': m.get('phase'),
            'tags': tags,
            'utterances': m.get('trigger_phrases', []),
            'response': m.get('response_snippet') or m.get('response') or '',
            'fallback': m.get('fallback', '')
        })
    return sf_modules


def export_to_file(data: List[Dict[str, Any]], path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:  # pragma: no cover - CLI helper
    p = argparse.ArgumentParser(description='Export modules for Synthflow.')
    p.add_argument('-i', '--input', default=str(Path('gvjj-voice-agent_ready for embeding') / 'ava_modlist_chunks.jsonl'),
                   help='Path to ava_modlist_chunks.jsonl')
    p.add_argument('-o', '--output', default='synthflow_modules.json', help='Output file path')
    args = p.parse_args()

    modules = load_modules(args.input)
    sf_modules = convert_to_synthflow(modules)
    export_to_file(sf_modules, args.output)
    print(f'Exported {len(sf_modules)} modules to {args.output}')


if __name__ == '__main__':
    main()

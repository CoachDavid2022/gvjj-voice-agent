import json
import argparse
from pathlib import Path

VALID_PHASES = {
    "booking",
    "intake",
    "recovery",
    "greeting",
    "escalation",
    "confirmation",
    "all",
    "tonal",
    "soft",
}


def load_modules(path: str):
    modules = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                modules.append(json.loads(line))
    return modules


def validate_modules(modules):
    issues = []
    seen_ids = set()
    for idx, m in enumerate(modules, start=1):
        mid = m.get("module_id")
        if not mid:
            issues.append(f"Line {idx}: missing module_id")
        elif mid in seen_ids:
            issues.append(f"Duplicate module_id '{mid}' at line {idx}")
        else:
            seen_ids.add(mid)

        triggers = m.get("trigger_phrases")
        if not triggers:
            issues.append(f"Module {mid}: missing trigger_phrases")

        phase = m.get("phase")
        if phase not in VALID_PHASES:
            issues.append(f"Module {mid}: invalid phase '{phase}'")
    return issues


def build_manifest(modules):
    return [
        {
            "module_id": m.get("module_id"),
            "intent": m.get("intent"),
            "phase": m.get("phase"),
            "tags": m.get("tags"),
        }
        for m in modules
    ]


def main():
    parser = argparse.ArgumentParser(description="Validate modules and output manifest")
    parser.add_argument(
        "-i",
        "--input",
        default=str(Path("gvjj-voice-agent_ready for embeding") / "ava_modlist_chunks.jsonl"),
        help="Path to ava_modlist_chunks.jsonl",
    )
    parser.add_argument("-o", "--output", help="Optional path to write manifest JSON")
    args = parser.parse_args()

    modules = load_modules(args.input)
    issues = validate_modules(modules)
    manifest = build_manifest(modules)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))

    if issues:
        print("\nInconsistencies found:")
        for issue in issues:
            print(f" - {issue}")
    else:
        print("\nNo issues found.")


if __name__ == "__main__":
    main()

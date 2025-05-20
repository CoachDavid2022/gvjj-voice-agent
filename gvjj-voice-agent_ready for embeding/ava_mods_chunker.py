import re
import json
import argparse
try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # allow running without embeddings
    SentenceTransformer = None
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:  # fallback if dotenv missing
    def load_dotenv(*args, **kwargs):
        pass
try:
    import pinecone
except ImportError:
    pinecone = None

try:
    from docx import Document
except ImportError:
    Document = None

def load_source(path):
    if path.lower().endswith('.docx'):
        if Document is None:
            raise RuntimeError("python-docx is required to read .docx files")
        doc = Document(path)
        # join all non-empty paragraphs
        return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    else:
        with open(path, encoding='utf-8') as f:
            return f.read()

def parse_modules(text):
    """Split text into module blocks and parse fields."""
    blocks = re.split(r'BEGIN_MODULE', text)[1:]
    modules = []
    for raw in blocks:
        block = 'BEGIN_MODULE' + raw
        if 'END_MODULE' not in block:
            continue
        lines = block.splitlines()
        m = {
            "module_id": None,
            "title": None,
            "intent": None,
            "phase": None,
            "tags": [],
            "trigger_phrases": [],
            "response_snippet": "",
            "raw_text_chunk": block.strip()
        }
        current = None
        for line in lines:
            s = line.strip()
            if s.startswith("title:"):
                _, val = s.split(":", 1)
                title = val.strip()
                m["title"] = title
                base_id = title.split(":")[0].strip()
                base_id = base_id.replace(" ", "-")
                base_id = re.sub(r"[\s\W]+", "", base_id)
                m["module_id"] = base_id
                current = None
            elif s.startswith("intent:"):
                m["intent"] = s.split(":",1)[1].strip()
                current = None
            elif s.startswith("phase:"):
                m["phase"] = s.split(":",1)[1].strip()
                current = None
            elif s.startswith("tags:"):
                tag_str = s.split(":", 1)[1]
                raw_tags = [t.strip() for t in tag_str.split(",") if t.strip()]
                parsed = []
                for t in raw_tags:
                    if "=" in t:
                        parsed.append(t)
                    else:
                        parsed.append(f"tone_style={t}")
                m["tags"] = parsed
                current = None
            elif s.startswith("trigger_phrases:"):
                current = "trigger"
            elif s.startswith("response:"):
                current = "response"
            elif s.startswith("fallback:") or s.startswith("notes:"):
                current = None
            else:
                if current == "trigger" and s.startswith("•"):
                    phrase = s.lstrip("• ").strip().strip('“”"')
                    m["trigger_phrases"].append(phrase)
                elif current == "response" and s:
                    m["response_snippet"] += s + " "
        m["response_snippet"] = m["response_snippet"].strip()
        modules.append(m)
    return modules

def embed_modules(modules, model_name):
    if SentenceTransformer is None or model_name.lower() == "none":
        for m in modules:
            m["embedding"] = []
        return modules

    model = SentenceTransformer(model_name)
    texts = [m["raw_text_chunk"] for m in modules]
    embs = model.encode(texts, show_progress_bar=True)
    for m, vec in zip(modules, embs):
        m["embedding"] = vec.tolist()
    return modules

def write_jsonl(modules, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for m in modules:
            json.dump(m, f, ensure_ascii=False)
            f.write("\n")

def main():
    p = argparse.ArgumentParser(description="Chunk, embed & (optionally) upload AVA CORE KB MODS")
    p.add_argument(
        "-i","--input",
        default="🤙AVA CORE KB MODS.docx",
        help="path to .docx or .json source with module blocks"
    )
    p.add_argument(
        "-o","--output",
        default="ava_modlist_chunks.jsonl",
        help="destination JSONL file"
    )
    p.add_argument(
        "-m","--model",
        default="all-MiniLM-L6-v2",
        help="sentence-transformers model"
    )
    p.add_argument("--pinecone-index",
                   help="name of Pinecone index to upsert into")
    p.add_argument("--create-index", action="store_true",
                   help="create the Pinecone index if it doesn't exist")
    args = p.parse_args()

    text = load_source(args.input)
    modules = parse_modules(text)
    modules = embed_modules(modules, args.model)
    write_jsonl(modules, args.output)
    print(f"Written {len(modules)} chunks to {args.output}")

    # ——— NEW: optional Pinecone upload ———
    if args.pinecone_index and pinecone is not None:
        # Load environment variables from the project root
        root_dir = Path(__file__).resolve().parent.parent
        load_dotenv(root_dir / ".env")
        api_key = os.getenv("PINECONE_API_KEY")
        env     = os.getenv("PINECONE_ENV")
        if not api_key or not env:
            raise RuntimeError("PINECONE_API_KEY and PINECONE_ENV must be set in .env")

        pinecone.init(api_key=api_key, environment=env)

        # infer dimension
        dim = len(modules[0]["embedding"])
        if args.create_index and args.pinecone_index not in pinecone.list_indexes():
            pinecone.create_index(args.pinecone_index, dimension=dim)

        idx = pinecone.Index(args.pinecone_index)
        batch, BATCH_SIZE = [], 100
        for m in modules:
            vid = m["module_id"]
            meta = {k: v for k, v in m.items() if k not in ("embedding", "raw_text_chunk")}
            batch.append((vid, m["embedding"], meta))
            if len(batch) >= BATCH_SIZE:
                idx.upsert(vectors=batch)
                batch.clear()
        if batch:
            idx.upsert(vectors=batch)

        print(f"Upserted {len(modules)} vectors into Pinecone index '{args.pinecone_index}'")

if __name__ == "__main__":
    main()

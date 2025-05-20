from pinecone import Pinecone, ServerlessSpec, PineconeApiException
import json, time

# 1) Configuration – hard‐coded for your workspace
API_KEY      = "pcsk_2wSEf9_EtrUvGV1keEeyZqhzLrYGRf8wKUueWXgDpPW29Y2jVYrqdMwwHsZTJzCGbP1bNx"
API_ENDPOINT = "https://ava-gvjj-voice-agent-k4jthun.svc.aped-4627-b74a.pinecone.io"
REGION       = "us-east-1"
INDEX_NAME   = "ava-gvjj-voice-agent"
JSONL_PATH   = r"C:\Users\drat8\OneDrive\Documents\gvjj-voice-agent_ready for embeding\ava_modlist_chunks.jsonl"

# 2) Initialize Pinecone client
pc = Pinecone(
    api_key=API_KEY,
    environment=REGION,
    api_endpoint=API_ENDPOINT
)

# 3) Create or recreate index to match your vectors’ dimension
with open(JSONL_PATH, "r", encoding="utf-8") as f:
    first = json.loads(f.readline())
dim = len(first["embedding"])

indexes = pc.list_indexes()
if INDEX_NAME in indexes:
    # fetch current index info
    info = pc.describe_index(INDEX_NAME)
    if info.dimension != dim:
        print(f"⚠️  Dimension mismatch ({info.dimension} vs {dim}), deleting index…")
        pc.delete_index(INDEX_NAME)
        # wait for deletion to propagate
        time.sleep(5)
        indexes = pc.list_indexes()

if INDEX_NAME not in indexes:
    pc.create_index(
        name=INDEX_NAME,
        dimension=dim,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=REGION)
    )

# 4) Connect to your index
index = pc.Index(INDEX_NAME)

# 5) Read & upsert in batches
BATCH_SIZE = 50
batch = []

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line)
        batch.append({
            "id":       rec["module_id"],
            "values":   rec["embedding"],
            "metadata": {k: v for k, v in rec.items() if k != "embedding"}
        })
        if len(batch) >= BATCH_SIZE:
            index.upsert(vectors=batch)
            batch.clear()

# flush remaining
if batch:
    index.upsert(vectors=batch)

print(f"✔️ Upserted all vectors into index '{INDEX_NAME}'")
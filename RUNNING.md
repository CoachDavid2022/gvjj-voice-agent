# Running the GVJJ Voice Agent

Follow these steps to generate the module embeddings and try the retrieval logic.

## 1. Install dependencies
Use Python 3.9+ in a virtual environment and install everything from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 2. Configure environment variables
Create a `.env` file in the repository root and fill in your API keys:

```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENV=your_pinecone_env
ELEVENLABS_API_KEY=your_elevenlabs_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

## 3. Generate module embeddings
Run the chunker to convert the module document into JSONL with embeddings:

```bash
python "gvjj-voice-agent_ready for embeding/ava_mods_chunker.py"
```

This reads `🤙AVA CORE KB MODS.docx` and writes `ava_modlist_chunks.jsonl` in the same folder.

## 4. Test module retrieval
Use the generated file with `module_manager.py` to retrieve a module for a sample phrase:

```bash
python "gvjj-voice-agent_ready for embeding/module_manager.py" -i "Hello"
```

The `--modules` argument defaults to
`gvjj-voice-agent_ready for embeding/ava_modlist_chunks.jsonl`.

You should see a selected module printed to the console.

### Example conversation
```
User: Hello, I'm interested in trying a class.
AVA: "I’m the booking assistant at Good Vibes Jiu-Jitsu and Fitness. I help Coach Jess and Coach David set up intro classes."
```

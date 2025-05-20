# GVJJ Voice Agent (AVA)

**Repository:** `gvjj-voice-agent`
**Status:** Pre-Alpha / Prototyping
**Organization:** Good Vibez Jiu-Jitsu & Fitness (GVJJ)
**Creator:** David G. Ratliff (@CoachDavid2022)

AVA (Automated Voice Assistant) is a voice-first AI designed to welcome new leads at Good Vibez Jiu-Jitsu & Fitness. The project focuses on creating a realistic, emotionally aware phone assistant that can schedule introductory classes and handle common questions with a human touch.

## Key Features
- **Immediate lead response** to new inquiries.
- **Consent-based booking flow** that gently guides users toward an intro class.
- **Tone and emotion calibration** via a prosody engine.
- **Modular behavior engine** driven by a tagged knowledge base.
- **Vector search** using Pinecone for retrieving relevant response modules.
- **TTS/STT integration** with ElevenLabs and Whisper/Deepgram.
- **Planned integrations** for Google Calendar, Twilio, and workflow automation tools.

## Architecture Overview
1. **Speech-to-Text** converts caller audio to text.
2. **Knowledge Base Retrieval** searches Pinecone for the best response modules from `ava_modlist_chunks.jsonl`.
3. **LLM Core** (GPT-4) generates the next line based on context and conversation state.
4. **Text-to-Speech** produces natural speech via ElevenLabs.
5. **Telephony** (Twilio) delivers calls and SMS.

The knowledge base originates from `🤙AVA CORE KB MODS.docx` and is processed into JSON lines by the `ava_mods_chunker` module. The orchestration logic in `module_manager` selects modules according to tags and conversation phase.

## Getting Started
1. **Clone the repository**
   ```bash
   git clone https://github.com/CoachDavid2022/gvjj-voice-agent.git
   cd gvjj-voice-agent
   ```
2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure API keys** by creating a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENV=your_pinecone_env
   ELEVENLABS_API_KEY=your_elevenlabs_key
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   ```
5. **Generate knowledge base embeddings**
   ```bash
   python -m ava.ava_mods_chunker
   ```
6. **Test module retrieval**
    ```bash
    python -m ava.module_manager -i "Hello"
    ```
    The `--modules` argument defaults to
    `gvjj-voice-agent_ready for embeding/ava_modlist_chunks.jsonl`.

## Running Tests
Run the unit tests to validate module data:
```bash
python -m unittest
```

## Additional Documentation
- `# AVA System Setup Guide` – developer reference.
- `AVA-Whitepaper-and-Implementation-Guide.md` – design background.
- `RUNNING.md` – concise running instructions.

## Contributing
Pull requests are welcome. Please open an issue first for major changes. All contributions are reviewed for fit with the project roadmap.

## License
This project is released under the [MIT License](LICENSE).

## Contact
For questions about AVA or GVJJ, contact **CoachDavid2022** through GitHub or visit [Good Vibez Jiu-Jitsu & Fitness](https://goodvibezjiujitsu.com).

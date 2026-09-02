# NOVA — Premium AI Voice Assistant

A commercial-grade, voice-first AI assistant built with **FastAPI**, **SQLite**, **OpenAI**, and **modern Web Audio APIs**.

---

## Key Features

- **Futuristic Visual Identity & 3D AI Core**:
  - Central animated AI Core / Orb reflecting 8 explicit states: `IDLE`, `LISTENING`, `PROCESSING`, `THINKING`, `TOOL_USE`, `SPEAKING`, `PAUSED`, `ERROR`.
  - Real Web Audio API waveform visualizer reacting dynamically to speech and microphone frequency data.
- **Voice-First Engine**:
  - Speech-to-Text via OpenAI Whisper (`whisper-1`) with fallback.
  - Text-to-Speech via OpenAI TTS (`tts-1`) with speed and voice selection (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`).
  - Instant speech interruption (Stop button, new speech, or `Esc`).
  - Hands-Free continuous conversation mode.
  - Pluggable `WakeWordService` abstraction hook.
- **Streaming Tokens**:
  - Server-Sent Events (SSE) `/api/chat/stream` for progressive token rendering.
  - Markdown formatting with code block copy buttons.
- **Persistent Conversations**:
  - SQLite WAL-mode database.
  - Chat history sidebar with live search, renaming, export to JSON, and message clearing.
- **Selective Memory System**:
  - Retains user preferences and instructions across conversations.
  - Memory toggle and management panel.
- **Modular Tool Calling**:
  - **Calculator**: Safe AST-based math evaluation.
  - **Time**: Global time and timezone clock.
  - **Weather**: Forecast and conditions reporter.
  - **Web Search**: Real-time web intelligence.
  - **Notes & Reminders**: Native task and thought tracking.
  - **Knowledge Search**: Query user-uploaded documents.
- **RAG / Knowledge Base**:
  - Upload PDF, TXT, and Markdown files.
  - Text extraction, chunking with overlap, and keyword similarity search.
- **Personality & Multi-Language**:
  - Personality presets: `Futuristic`, `Professional`, `Friendly`, `Concise`, `Tutor`, `Coding Assistant`, or Custom instructions.
  - Multi-language support: English, Hindi, Tamil, Spanish, French, German.
- **Power User Controls**:
  - Command Palette (`Ctrl+K`).
  - Global shortcuts (`Ctrl+N` new chat, `Ctrl+/` chat focus, `Esc` stop speech).
  - Dark / Light / System theme toggle.

---

## Quick Start

### 1. Install Dependencies
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

---

## Operating Modes: Simulation Mode vs. Live OpenAI Mode

> [!IMPORTANT]
> **Live OpenAI Functionality Requires an API Key:**
> Live Speech-to-Text (`whisper-1`), remote GPT-4o completions, and remote OpenAI voice synthesis (`tts-1`) require a valid `OPENAI_API_KEY` in `.env`.

> [!NOTE]
> **Current Build Operates in Simulation Mode (Zero Cost, No Key Required):**
> If `OPENAI_API_KEY` is left blank or as a placeholder (`your_api_key_here`), NOVA automatically boots into **Simulation Mode**.
> In Simulation Mode:
> - **Browser-Native Speech Recognition**: In Google Chrome and Microsoft Edge, spoken input is transcribed locally in real-time via the Web Speech API (`webkitSpeechRecognition`) with live interim feedback in the UI before executing.
> - **Unified Command & Conversation Pipeline**: Both voice transcripts and typed inputs pass through the exact same conversation, intent-matching, and tool-execution pipeline.
> - **Zero Cost & Offline-Ready**: All arithmetic computations, worldwide time conversions, weather diagnostics, note organization, reminder management, and document RAG queries run locally.
> - **Local Voice Synthesis**: Speaks responses out loud in natural local voice via browser speech synthesis (`window.speechSynthesis`) or harmonic PCM chords.
> - **Visual AI Core & State Machine**: Full reactive visualizer, interactive Orb, Command Palette (`Ctrl+K`), and conversation history work smoothly.
> - **Transparent Fallback**: Never fakes microphone transcripts. If run in a browser lacking SpeechRecognition without an OpenAI key, an informative notification clearly guides the user to use Chrome/Edge or type.

### 3. Run Locally
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Running Tests
Run the comprehensive automated pytest suite (unit, integration, and live Google Chrome Playwright E2E tests):
```bash
python -m pytest tests/ -v
```
*(All 28 tests passing with 100% pass rate)*

---

## Architecture Overview
```
app/
├── main.py                     # FastAPI application & router mounting
├── config.py                   # Environment configuration & directories
├── logging_config.py           # Structured application logging
├── api/                        # Thin API endpoints (chat, voice, conversations, etc.)
├── database/                   # SQLite session & repository pattern
│   ├── session.py
│   └── repositories/
├── services/                   # Business logic, tool registry, RAG, speech, LLM
│   ├── conversation_service.py
│   ├── personality.py
│   ├── llm/
│   ├── speech/
│   ├── tools/
│   ├── search/
│   └── rag/
├── schemas/                    # Pydantic validation schemas
└── static/                     # Premium glassmorphic SPA frontend
    ├── index.html
    ├── css/
    └── js/
```

---

## API Summary
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Application status & mode |
| `POST` | `/api/chat` | Standard chat completion |
| `POST` | `/api/chat/stream` | SSE progressive token stream |
| `POST` | `/api/voice/transcribe`| Audio file speech-to-text |
| `POST` | `/api/voice/synthesize`| Text-to-speech generation |
| `GET` | `/api/conversations` | List persistent conversations |
| `POST` | `/api/conversations` | Create new conversation |
| `GET` | `/api/conversations/{id}`| Get conversation details & messages |
| `PATCH`| `/api/conversations/{id}`| Rename conversation |
| `DELETE`| `/api/conversations/{id}`| Delete conversation |
| `GET` | `/api/conversations/{id}/export`| Export conversation to JSON |
| `GET` | `/api/settings` | Get user settings |
| `PATCH`| `/api/settings` | Update settings |
| `GET` | `/api/memories` | List stored memories |
| `POST` | `/api/knowledge/upload`| Upload PDF/TXT/MD document |
| `GET` | `/api/knowledge/documents`| List uploaded documents |
| `POST` | `/api/knowledge/query` | Test knowledge base retrieval |
| `GET` | `/api/tools` | List registered assistant tools |
| `POST` | `/api/tools/execute` | Execute tool directly |
| `POST` | `/api/text` | Backward-compatible text pipeline |
| `POST` | `/api/voice` | Backward-compatible voice pipeline |
| `GET` | `/api/audio/{filename}`| Secure audio playback stream |

---

## License
MIT

# NOVA AI Voice Assistant

NOVA is a voice-first AI assistant with a futuristic web interface, a FastAPI backend, SQLite persistence, browser audio APIs, and optional OpenAI integration. It is designed to remain useful locally, even when no API key is configured.

## Features

- Futuristic voice-first UI with an animated AI core/orb and visible states for listening, processing, thinking, tool use, speaking, paused, and error conditions.
- Voice input through OpenAI Whisper when configured, with browser Speech Recognition fallback in Chrome and Microsoft Edge.
- Text chat with streaming responses, Markdown rendering, and code-block copy controls.
- Persistent conversation history with search, rename, export, and clear-message actions.
- Selective memory for user preferences and instructions, with controls to review stored memories.
- Built-in calculator, time, weather, web search, notes, reminders, and knowledge search tools.
- Notes and reminders managed through the assistant and dedicated API endpoints.
- Knowledge base/RAG support for PDF, TXT, and Markdown uploads, chunking, and local similarity search.
- Personality presets including Futuristic, Professional, Friendly, Concise, Tutor, and Coding Assistant, plus custom instructions.
- Language and theme settings with dark, light, and system modes.
- Command palette with `Ctrl+K`, new conversation with `Ctrl+N`, chat focus with `Ctrl+/`, and speech stop with `Esc`.

## Live Application

- **GitHub Repository URL**: [https://github.com/dhilipdinesh100-del/ai-voice](https://github.com/dhilipdinesh100-del/ai-voice) shows the complete project source code, tests, and configuration.
- **Deployed Application URL**: Visiting the deployed URL (e.g. on Render) directly opens the interactive NOVA web application at `/`, not a static README or repository page.
- **FastAPI Backend**: The backend is built with **FastAPI**, serving the responsive UI from `app/static/index.html` at `/`, static assets from `/static/...`, health checks at `/health`, interactive OpenAPI docs at `/docs`, and backend intelligence at `/api/...`.
- **Simulation Mode (No Key Required)**: Fully functional without an API key. Local AST arithmetic, worldwide time zones, weather reports, note organization, reminder management, document RAG queries, browser Speech Recognition, and local Web Speech synthesis work out of the box.
- **OpenAI Functionality (User Key Required)**: Cloud-based GPT-4o reasoning, OpenAI Whisper STT, and OpenAI voice synthesis require the user's own `OPENAI_API_KEY`.
- **Security Rule**: **Do NOT put an API key in GitHub**. The `.env` file is excluded in `.gitignore`. For production deployments, supply `OPENAI_API_KEY` through the host's secret environment variables dashboard.

## Operating Modes

### Simulation Mode

NOVA runs in Simulation Mode when `OPENAI_API_KEY` is blank or set to the safe placeholder in `.env.example`. No OpenAI account or API key is required. Local tools, SQLite persistence, document retrieval, browser Speech Recognition, and browser speech synthesis remain available. In browsers without Speech Recognition, type messages instead.

### Live OpenAI Mode

Configure your own OpenAI API key in the local `.env` file to enable remote GPT responses, Whisper transcription, and OpenAI text-to-speech. Never commit `.env` or share your key. The repository contains only safe placeholder values in `.env.example`.

## Installation

Requirements: Python 3.11 or newer and a modern browser. On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Environment Configuration

Copy the safe template and edit the local copy:

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env`. Leave `OPENAI_API_KEY` blank or unchanged to use Simulation Mode. To use live OpenAI services, replace it with your own key in `.env`; do not add that file to Git.

## Run Locally

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000> in your browser. If port 8000 is unavailable, choose another local port such as 8001.

## Production Deployment

GitHub Pages cannot run NOVA. GitHub is the source repository only; it does not provide a Python runtime for the FastAPI backend. Deploy the repository to a Python/FastAPI hosting service, then open that service's URL in the browser:

```text
GitHub source repository -> Python/FastAPI host -> browser -> NOVA frontend and /api routes
```

### Recommended Host: Render

Render is the recommended starting point because it supports Python web services, reads the included `render.yaml` blueprint, and provides the `PORT` environment variable required by the production command. The included `Procfile` is also compatible with hosts that use Procfile-based deployment.

1. Push this repository to GitHub, keeping `.env` local and uncommitted.
2. In Render, choose **New > Blueprint** and select the GitHub repository.
3. Render detects `render.yaml`, installs `requirements.txt`, and runs `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. In the Render service environment settings, add your own `OPENAI_API_KEY` only if live OpenAI features are needed. Leave it unset for Simulation Mode.
5. Deploy, then open the assigned Render URL. The NOVA interface is served at `/`, assets at `/static/...`, health at `/health`, and backend APIs at `/api/...`.
6. Verify the deployment at `https://YOUR-RENDER-URL.onrender.com/health` before using the UI.

The production service must bind to `0.0.0.0` and use the host-provided `$PORT`; do not use the local development command with `--reload` in production. The included [render.yaml](render.yaml) and [Procfile](Procfile) keep the deployment command in source control.

Render's free service may sleep when idle. The local SQLite database and uploaded audio/documents use the service filesystem, so they are appropriate for development or a single-instance deployment and may be lost during redeploys or instance replacement. Use a managed database and persistent object storage before treating the service as production data storage.

## Testing

Run the unit, integration, and browser tests with:

```bash
python -m pytest tests/ -v
```

The browser test requires a supported local browser and its Playwright setup. Tests use isolated local data; runtime databases, audio, uploads, and test artifacts are ignored by Git.

## Known Limitations

- Browser Speech Recognition support varies by browser and may require Chrome or Microsoft Edge.
- Live transcription, remote chat completions, and OpenAI voice synthesis require the user's own API key and network access.
- Weather and web search depend on their external services and may be unavailable offline.
- SQLite and the local upload directory are intended for a single local instance, not multi-user production deployment.
- Wake-word support is an extension point; continuous conversation still depends on browser microphone permissions and supported audio APIs.

## Project Layout

```text
app/       FastAPI application, API routers, services, schemas, and static UI
tests/     Unit, integration, and browser tests
data/      Local runtime database, audio, and uploaded documents (ignored)
```

## API

The backend provides health, chat and streaming chat, voice transcription and synthesis, conversations, settings, memories, knowledge upload/query, tools, notes, reminders, and backward-compatible text/voice endpoints. Interactive API documentation is available at `/docs` while the server is running.

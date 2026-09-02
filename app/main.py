from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import logger
from app.database.session import init_db

# Import API routers
from app.api.chat import router as chat_router
from app.api.voice import router as voice_router
from app.api.conversations import router as conversations_router
from app.api.settings import router as settings_router
from app.api.memories import router as memories_router
from app.api.knowledge import router as knowledge_router
from app.api.tools import router as tools_router
from app.api.notes import router as notes_router
from app.api.reminders import router as reminders_router

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize folders and database
    settings.init_directories()
    init_db()
    logger.info("NOVA AI Assistant backend started successfully.")
    yield
    logger.info("NOVA AI Assistant backend shutting down.")

app = FastAPI(
    title="NOVA — Premium AI Voice Assistant",
    description="Futuristic, voice-first AI assistant with persistent memory, tool-calling, RAG, and real-time audio pipeline.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe error handling per SPECS.md Section 36 & 37
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception at %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal assistant error occurred. The system recovered safely."}
    )

# Static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Core routes: serve NOVA single-page web application at root
@app.get("/", include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / "static" / "index.html", media_type="text/html")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "assistant": settings.ASSISTANT_NAME,
        "mode": "openai" if settings.has_real_openai_key else "simulation"
    }

# Register modular routers
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(conversations_router)
app.include_router(settings_router)
app.include_router(memories_router)
app.include_router(knowledge_router)
app.include_router(tools_router)
app.include_router(notes_router)
app.include_router(reminders_router)

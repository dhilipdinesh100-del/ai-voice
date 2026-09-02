import uuid
import re
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.config import settings
from app.services.speech.stt_provider import get_stt_provider
from app.services.speech.tts_provider import get_tts_provider
from app.services.conversation_service import conversation_service
from app.schemas.voice import SynthesizeRequest, SynthesizeResponse, TranscribeResponse
from app.logging_config import logger

router = APIRouter(tags=["Voice"])

class LegacyTextRequest(BaseModel):
    text: str

# Sanitize filename helper to prevent path traversal
SAFE_FILENAME_RE = re.compile(r'^[a-zA-Z0-9_\-\.]+$')

@router.post("/api/voice/transcribe", response_model=TranscribeResponse)
async def transcribe_audio_endpoint(audio: UploadFile = File(...)):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="Audio file is required.")
        
    ext = Path(audio.filename).suffix.lower() or ".webm"
    if ext not in [".webm", ".wav", ".mp3", ".m4a", ".ogg"]:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {ext}")

    temp_path = settings.DATA_DIR / f"temp_{uuid.uuid4().hex}{ext}"
    try:
        content = await audio.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file exceeds size limit.")
            
        temp_path.write_bytes(content)
        stt = get_stt_provider()
        try:
            text = stt.transcribe(temp_path)
            return {"text": text}
        except RuntimeError as err:
            logger.info("STT unavailable: %s", err)
            raise HTTPException(
                status_code=501,
                detail=str(err)
            )
    finally:
        temp_path.unlink(missing_ok=True)

@router.post("/api/voice/synthesize", response_model=SynthesizeResponse)
def synthesize_speech_endpoint(request: SynthesizeRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        tts = get_tts_provider()
        output_file = tts.synthesize(text=text, voice=request.voice, speed=request.speed or 1.0)
        return {"audio_url": f"/api/audio/{output_file.name}"}
    except Exception as e:
        logger.error("Synthesis error: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to synthesize speech: {str(e)}")

@router.get("/api/audio/{filename}")
def stream_audio(filename: str):
    # Path traversal check
    if not SAFE_FILENAME_RE.match(filename) or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename format.")
        
    path = settings.AUDIO_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found.")
        
    media_type = "audio/wav" if filename.endswith(".wav") else "audio/mpeg"
    return FileResponse(path, media_type=media_type, filename=filename)

# ----------------- Backward Compatibility Routes -----------------

@router.post("/api/text")
def legacy_text_pipeline(request: LegacyTextRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Please enter some text.")
    res = conversation_service.process_chat(
        conversation_id=None,
        user_text=text,
        generate_audio=True
    )
    return {
        "transcript": text,
        "answer": res["answer"],
        "audio_url": res["audio_url"] or ""
    }

@router.post("/api/voice")
async def legacy_voice_pipeline(audio: UploadFile = File(...)):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="Audio file is required.")
        
    ext = Path(audio.filename).suffix.lower() or ".webm"
    temp_path = settings.DATA_DIR / f"temp_{uuid.uuid4().hex}{ext}"
    try:
        content = await audio.read()
        temp_path.write_bytes(content)
        stt = get_stt_provider()
        try:
            transcript = stt.transcribe(temp_path)
        except RuntimeError as err:
            logger.info("STT unavailable in legacy endpoint: %s", err)
            raise HTTPException(status_code=501, detail=str(err))
        
        res = conversation_service.process_chat(
            conversation_id=None,
            user_text=transcript,
            generate_audio=True
        )
        return {
            "transcript": transcript,
            "answer": res["answer"],
            "audio_url": res["audio_url"] or ""
        }
    finally:
        temp_path.unlink(missing_ok=True)

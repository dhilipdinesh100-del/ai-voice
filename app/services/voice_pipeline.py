from pathlib import Path
from app.config import settings
from app.services.speech.stt_provider import get_stt_provider
from app.services.speech.tts_provider import get_tts_provider
from app.services.conversation_service import conversation_service

def transcribe_audio(audio_path: Path) -> str:
    stt = get_stt_provider()
    return stt.transcribe(audio_path)

def answer_from_text(user_text: str) -> str:
    res = conversation_service.process_chat(
        conversation_id=None,
        user_text=user_text,
        generate_audio=False
    )
    return res["answer"]

def generate_speech(text: str) -> Path:
    tts = get_tts_provider()
    return tts.synthesize(text)

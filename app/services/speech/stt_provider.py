from pathlib import Path
from typing import Optional
from app.config import settings
from app.logging_config import logger

class SpeechToTextProvider:
    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> str:
        raise NotImplementedError

class OpenAIWhisperProvider(SpeechToTextProvider):
    def __init__(self, api_key: str, model: str = "whisper-1"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> str:
        with audio_path.open("rb") as f:
            kwargs = {"model": self.model, "file": f}
            if language and language != "auto":
                kwargs["language"] = language
            result = self.client.audio.transcriptions.create(**kwargs)
            return result.text.strip()

class FallbackSTTProvider(SpeechToTextProvider):
    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> str:
        logger.warning("FallbackSTTProvider invoked for %s, but OpenAI API key is not configured.", audio_path.name)
        raise RuntimeError(
            "Server-side Whisper speech recognition is unavailable because OPENAI_API_KEY is not configured in .env. "
            "In Simulation Mode, please use browser-native Web Speech Recognition (Google Chrome / Edge) or type your query."
        )

def get_stt_provider() -> SpeechToTextProvider:
    if settings.has_real_openai_key:
        try:
            return OpenAIWhisperProvider(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_TRANSCRIPTION_MODEL
            )
        except Exception as e:
            logger.error("Failed to initialize OpenAI Whisper provider: %s", e)
    return FallbackSTTProvider()

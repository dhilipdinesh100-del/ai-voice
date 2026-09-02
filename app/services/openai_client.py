from app.config import settings

client = None
if settings.has_real_openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception:
        client = None

LLM_MODEL = settings.OPENAI_LLM_MODEL
TRANSCRIPTION_MODEL = settings.OPENAI_TRANSCRIPTION_MODEL
TTS_MODEL = settings.OPENAI_TTS_MODEL
TTS_VOICE = settings.OPENAI_TTS_VOICE

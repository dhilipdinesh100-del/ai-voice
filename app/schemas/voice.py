from typing import Optional
from pydantic import BaseModel

class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"
    speed: Optional[float] = 1.0

class SynthesizeResponse(BaseModel):
    audio_url: str

class TranscribeResponse(BaseModel):
    text: str

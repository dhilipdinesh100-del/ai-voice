from typing import Optional
from pydantic import BaseModel

class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    assistant_name: Optional[str] = None
    personality: Optional[str] = None
    custom_prompt: Optional[str] = None
    voice: Optional[str] = None
    voice_speed: Optional[float] = None
    language: Optional[str] = None
    auto_play: Optional[bool] = None
    hands_free: Optional[bool] = None
    memory_enabled: Optional[bool] = None
    save_conversations: Optional[bool] = None
    save_audio: Optional[bool] = None
    response_length: Optional[str] = None

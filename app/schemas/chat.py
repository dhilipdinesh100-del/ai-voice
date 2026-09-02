from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
    stream: bool = False
    generate_audio: bool = True

class ChatResponse(BaseModel):
    conversation_id: str
    transcript: str
    answer: str
    audio_url: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    user_message: Dict[str, Any]
    assistant_message: Dict[str, Any]

from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ConversationUpdate(BaseModel):
    title: str

class MessageSchema(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str
    audio_reference: Optional[str] = None
    tool_metadata: Optional[Dict[str, Any]] = None

class ConversationDetail(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]
    messages: Optional[List[MessageSchema]] = None

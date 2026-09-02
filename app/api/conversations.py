from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationDetail
from app.database.repositories.conversation_repo import ConversationRepository
from app.database.repositories.message_repo import MessageRepository

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

@router.get("", response_model=List[Dict[str, Any]])
def list_conversations(q: Optional[str] = Query(None, description="Search query")):
    return ConversationRepository.list_all(query=q)

@router.post("", response_model=Dict[str, Any])
def create_conversation(payload: Optional[ConversationCreate] = None):
    title = (payload.title if payload and payload.title else "New Conversation").strip()
    return ConversationRepository.create(title=title)

@router.get("/{conv_id}", response_model=Dict[str, Any])
def get_conversation(conv_id: str):
    conv = ConversationRepository.get_by_id(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    messages = MessageRepository.get_by_conversation(conv_id)
    conv["messages"] = messages
    return conv

@router.patch("/{conv_id}")
def update_conversation(conv_id: str, payload: ConversationUpdate):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    success = ConversationRepository.update_title(conv_id, title)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"status": "success", "title": title}

@router.delete("/{conv_id}")
def delete_conversation(conv_id: str):
    success = ConversationRepository.delete(conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"status": "deleted", "id": conv_id}

@router.get("/{conv_id}/export")
def export_conversation(conv_id: str):
    data = ConversationRepository.export(conv_id)
    if not data:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return data

@router.delete("/{conv_id}/messages")
def clear_conversation_messages(conv_id: str):
    conv = ConversationRepository.get_by_id(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    count = MessageRepository.clear_by_conversation(conv_id)
    return {"status": "cleared", "messages_deleted": count}

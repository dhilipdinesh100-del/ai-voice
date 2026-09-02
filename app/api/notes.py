from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from app.schemas.notes_reminders import NoteCreate, NoteUpdate
from app.database.repositories.notes_repo import NoteRepository

router = APIRouter(prefix="/api/notes", tags=["Notes"])

@router.get("", response_model=List[Dict[str, Any]])
def list_notes():
    return NoteRepository.list_all()

@router.post("", response_model=Dict[str, Any])
def create_note(payload: NoteCreate):
    return NoteRepository.create(payload.title, payload.content)

@router.patch("/{note_id}", response_model=Dict[str, Any])
def update_note(note_id: str, payload: NoteUpdate):
    updated = NoteRepository.update(note_id, payload.title, payload.content)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found.")
    return updated

@router.delete("/{note_id}")
def delete_note(note_id: str):
    success = NoteRepository.delete(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found.")
    return {"status": "deleted", "id": note_id}

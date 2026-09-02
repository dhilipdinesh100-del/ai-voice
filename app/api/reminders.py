from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.schemas.notes_reminders import ReminderCreate
from app.database.repositories.reminders_repo import ReminderRepository

router = APIRouter(prefix="/api/reminders", tags=["Reminders"])

@router.get("", response_model=List[Dict[str, Any]])
def list_reminders():
    return ReminderRepository.list_all()

@router.post("", response_model=Dict[str, Any])
def create_reminder(payload: ReminderCreate):
    return ReminderRepository.create(payload.text, payload.due_at)

@router.patch("/{rem_id}/toggle", response_model=Dict[str, Any])
def toggle_reminder(rem_id: str):
    updated = ReminderRepository.toggle_completed(rem_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Reminder not found.")
    return updated

@router.delete("/{rem_id}")
def delete_reminder(rem_id: str):
    success = ReminderRepository.delete(rem_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found.")
    return {"status": "deleted", "id": rem_id}

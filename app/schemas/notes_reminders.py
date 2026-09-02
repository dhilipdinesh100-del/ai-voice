from typing import Optional
from pydantic import BaseModel

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class ReminderCreate(BaseModel):
    text: str
    due_at: Optional[str] = None

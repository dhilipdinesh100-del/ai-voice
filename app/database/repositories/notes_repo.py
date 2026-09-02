import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.database.session import get_db_connection

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class NoteRepository:
    @staticmethod
    def create(title: str, content: str) -> Dict[str, Any]:
        note_id = str(uuid.uuid4())
        now = utc_now_iso()
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO notes (id, title, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (note_id, title.strip(), content.strip(), now, now)
            )
        return {
            "id": note_id,
            "title": title.strip(),
            "content": content.strip(),
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(note_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update(note_id: str, title: Optional[str] = None, content: Optional[str] = None) -> Optional[Dict[str, Any]]:
        existing = NoteRepository.get_by_id(note_id)
        if not existing:
            return None
        new_title = title.strip() if title is not None else existing["title"]
        new_content = content.strip() if content is not None else existing["content"]
        now = utc_now_iso()
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
                (new_title, new_content, now, note_id)
            )
        return NoteRepository.get_by_id(note_id)

    @staticmethod
    def delete(note_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return cursor.rowcount > 0

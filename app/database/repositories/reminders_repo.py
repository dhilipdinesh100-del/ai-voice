import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.database.session import get_db_connection

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class ReminderRepository:
    @staticmethod
    def create(text: str, due_at: Optional[str] = None) -> Dict[str, Any]:
        rem_id = str(uuid.uuid4())
        now = utc_now_iso()
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO reminders (id, text, due_at, is_completed, created_at) VALUES (?, ?, ?, 0, ?)",
                (rem_id, text.strip(), due_at, now)
            )
        return {
            "id": rem_id,
            "text": text.strip(),
            "due_at": due_at,
            "is_completed": False,
            "created_at": now
        }

    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM reminders ORDER BY created_at DESC")
            return [
                {
                    "id": r["id"],
                    "text": r["text"],
                    "due_at": r["due_at"],
                    "is_completed": bool(r["is_completed"]),
                    "created_at": r["created_at"]
                }
                for r in cursor.fetchall()
            ]

    @staticmethod
    def toggle_completed(rem_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT is_completed FROM reminders WHERE id = ?", (rem_id,))
            row = cursor.fetchone()
            if not row:
                return None
            new_val = 0 if row["is_completed"] else 1
            conn.execute("UPDATE reminders SET is_completed = ? WHERE id = ?", (new_val, rem_id))
        
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM reminders WHERE id = ?", (rem_id,))
            r = cursor.fetchone()
            return {
                "id": r["id"],
                "text": r["text"],
                "due_at": r["due_at"],
                "is_completed": bool(r["is_completed"]),
                "created_at": r["created_at"]
            }

    @staticmethod
    def delete(rem_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM reminders WHERE id = ?", (rem_id,))
            return cursor.rowcount > 0

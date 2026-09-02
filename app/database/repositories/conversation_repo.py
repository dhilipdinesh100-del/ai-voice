import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.database.session import get_db_connection

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class ConversationRepository:
    @staticmethod
    def create(title: str = "New Conversation", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        conv_id = str(uuid.uuid4())
        meta_str = json.dumps(metadata or {})
        now = utc_now_iso()
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?)",
                (conv_id, title, now, now, meta_str)
            )
        return {
            "id": conv_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "metadata": metadata or {}
        }

    @staticmethod
    def list_all(query: Optional[str] = None) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            if query:
                cursor = conn.execute(
                    "SELECT * FROM conversations WHERE title LIKE ? ORDER BY updated_at DESC",
                    (f"%{query}%",)
                )
            else:
                cursor = conn.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "metadata": json.loads(row["metadata"] or "{}")
                }
                for row in rows
            ]

    @staticmethod
    def get_by_id(conv_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"] or "{}")
            }

    @staticmethod
    def update_title(conv_id: str, title: str) -> bool:
        now = utc_now_iso()
        with get_db_connection() as conn:
            cursor = conn.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, conv_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def touch(conv_id: str) -> None:
        now = utc_now_iso()
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conv_id)
            )

    @staticmethod
    def delete(conv_id: str) -> bool:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
            cursor = conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
            return cursor.rowcount > 0

    @staticmethod
    def export(conv_id: str) -> Optional[Dict[str, Any]]:
        conv = ConversationRepository.get_by_id(conv_id)
        if not conv:
            return None
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
                (conv_id,)
            )
            messages = [
                {
                    "id": r["id"],
                    "role": r["role"],
                    "content": r["content"],
                    "created_at": r["created_at"],
                    "audio_reference": r["audio_reference"],
                    "tool_metadata": json.loads(r["tool_metadata"]) if r["tool_metadata"] else None
                }
                for r in cursor.fetchall()
            ]
        conv["messages"] = messages
        return conv

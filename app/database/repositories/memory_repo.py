import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.database.session import get_db_connection

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class MemoryRepository:
    @staticmethod
    def add(content: str, category: str = "general") -> Dict[str, Any]:
        mem_id = str(uuid.uuid4())
        now = utc_now_iso()
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO memories (id, content, category, created_at) VALUES (?, ?, ?, ?)",
                (mem_id, content.strip(), category, now)
            )
        return {
            "id": mem_id,
            "content": content.strip(),
            "category": category,
            "created_at": now
        }

    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM memories ORDER BY created_at DESC")
            return [
                {
                    "id": row["id"],
                    "content": row["content"],
                    "category": row["category"],
                    "created_at": row["created_at"]
                }
                for row in cursor.fetchall()
            ]

    @staticmethod
    def delete(mem_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
            return cursor.rowcount > 0

    @staticmethod
    def clear_all() -> int:
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM memories")
            return cursor.rowcount

import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.database.session import get_db_connection
from app.database.repositories.conversation_repo import ConversationRepository

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class MessageRepository:
    @staticmethod
    def add_message(
        conversation_id: str,
        role: str,
        content: str,
        audio_reference: Optional[str] = None,
        tool_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        msg_id = str(uuid.uuid4())
        now = utc_now_iso()
        tool_meta_str = json.dumps(tool_metadata) if tool_metadata else None
        
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO messages 
                   (id, conversation_id, role, content, created_at, audio_reference, tool_metadata) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (msg_id, conversation_id, role, content, now, audio_reference, tool_meta_str)
            )
        
        ConversationRepository.touch(conversation_id)
        
        return {
            "id": msg_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": now,
            "audio_reference": audio_reference,
            "tool_metadata": tool_metadata
        }

    @staticmethod
    def get_by_conversation(conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT ?",
                (conversation_id, limit)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "conversation_id": row["conversation_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "created_at": row["created_at"],
                    "audio_reference": row["audio_reference"],
                    "tool_metadata": json.loads(row["tool_metadata"]) if row["tool_metadata"] else None
                }
                for row in rows
            ]

    @staticmethod
    def clear_by_conversation(conversation_id: str) -> int:
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            return cursor.rowcount

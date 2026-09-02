import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.database.session import get_db_connection

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class DocumentRepository:
    @staticmethod
    def create_document(
        filename: str,
        file_path: str,
        file_size: int,
        file_type: str,
        status: str = "processing"
    ) -> Dict[str, Any]:
        doc_id = str(uuid.uuid4())
        now = utc_now_iso()
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO documents (id, filename, file_path, file_size, file_type, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (doc_id, filename, file_path, file_size, file_type, status, now)
            )
        return {
            "id": doc_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_type": file_type,
            "status": status,
            "created_at": now
        }

    @staticmethod
    def update_status(doc_id: str, status: str, error_message: Optional[str] = None):
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE documents SET status = ?, error_message = ? WHERE id = ?",
                (status, error_message, doc_id)
            )

    @staticmethod
    def list_documents() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM documents ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def delete_document(doc_id: str) -> bool:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM document_chunks WHERE document_id = ?", (doc_id,))
            cursor = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            return cursor.rowcount > 0

    @staticmethod
    def add_chunks(doc_id: str, chunks: List[str]):
        with get_db_connection() as conn:
            for idx, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO document_chunks (id, document_id, chunk_index, content) VALUES (?, ?, ?, ?)",
                    (chunk_id, doc_id, idx, chunk)
                )

    @staticmethod
    def search_chunks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        keywords = [w.strip() for w in query.lower().split() if len(w.strip()) > 2]
        if not keywords:
            return []
        
        with get_db_connection() as conn:
            cursor = conn.execute(
                """SELECT c.id, c.document_id, c.content, d.filename 
                   FROM document_chunks c 
                   JOIN documents d ON c.document_id = d.id 
                   WHERE d.status = 'ready'"""
            )
            scored_results = []
            for row in cursor.fetchall():
                content_lower = row["content"].lower()
                score = sum(content_lower.count(kw) for kw in keywords)
                if score > 0:
                    scored_results.append({
                        "id": row["id"],
                        "document_id": row["document_id"],
                        "filename": row["filename"],
                        "content": row["content"],
                        "score": score
                    })
            
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            return scored_results[:limit]

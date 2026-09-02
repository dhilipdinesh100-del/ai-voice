from typing import Optional
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    file_type: str
    status: str
    error_message: Optional[str] = None
    created_at: str

class KnowledgeQueryRequest(BaseModel):
    query: str

from typing import Optional
from pydantic import BaseModel

class MemoryCreate(BaseModel):
    content: str
    category: Optional[str] = "general"

class MemoryResponse(BaseModel):
    id: str
    content: str
    category: str
    created_at: str

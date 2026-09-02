from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.schemas.memory import MemoryCreate, MemoryResponse
from app.database.repositories.memory_repo import MemoryRepository

router = APIRouter(prefix="/api/memories", tags=["Memories"])

@router.get("", response_model=List[MemoryResponse])
def list_memories():
    return MemoryRepository.list_all()

@router.post("", response_model=MemoryResponse)
def add_memory(payload: MemoryCreate):
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Memory content cannot be empty.")
    return MemoryRepository.add(content=content, category=payload.category or "general")

@router.delete("/{mem_id}")
def delete_memory(mem_id: str):
    success = MemoryRepository.delete(mem_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return {"status": "deleted", "id": mem_id}

@router.delete("")
def clear_all_memories():
    count = MemoryRepository.clear_all()
    return {"status": "cleared", "count": count}

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.tools.registry import tool_registry

router = APIRouter(prefix="/api/tools", tags=["Tools"])

class ToolExecuteRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

@router.get("", response_model=List[Dict[str, Any]])
def list_available_tools():
    return tool_registry.list_tools()

@router.post("/execute")
def execute_tool_endpoint(payload: ToolExecuteRequest):
    result = tool_registry.execute(payload.name, payload.arguments)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

from typing import Callable, Dict, Any, List, Optional
from pydantic import BaseModel
from app.logging_config import logger

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "func": func
        }
        logger.debug("Registered tool: %s", name)

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"]
            }
            for t in self._tools.values()
        ]

    def to_openai_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"]
                }
            }
            for t in self._tools.values()
        ]

    def execute(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        tool = self._tools.get(name)
        if not tool:
            return {"status": "error", "error": f"Unknown tool: {name}"}
        try:
            result = tool["func"](**args)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error("Error executing tool %s with args %s: %s", name, args, e)
            return {"status": "error", "error": str(e)}

tool_registry = ToolRegistry()

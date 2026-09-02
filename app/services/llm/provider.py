from typing import List, Dict, Any, Generator, Optional

class LLMProvider:
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Returns a dict:
        {
            "content": str,
            "tool_calls": Optional[List[Dict[str, Any]]],
            "raw": Any
        }
        """
        raise NotImplementedError

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[str, None, None]:
        """
        Yields chunk tokens as strings.
        """
        raise NotImplementedError

import json
from typing import List, Dict, Any, Generator, Optional
from app.services.llm.provider import LLMProvider
from app.logging_config import logger

class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _prepare_messages(self, messages: List[Dict[str, str]], system_prompt: str) -> List[Dict[str, str]]:
        out = [{"role": "system", "content": system_prompt}]
        for m in messages:
            out.append({"role": m["role"], "content": m["content"]})
        return out

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": self._prepare_messages(messages, system_prompt),
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**payload)
        choice = response.choices[0]
        msg = choice.message
        
        tool_calls_data = None
        if msg.tool_calls:
            tool_calls_data = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments) if tc.function.arguments else {}
                }
                for tc in msg.tool_calls
            ]

        return {
            "content": msg.content or "",
            "tool_calls": tool_calls_data,
            "raw": response
        }

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[str, None, None]:
        payload = {
            "model": self.model,
            "messages": self._prepare_messages(messages, system_prompt),
            "stream": True
        }
        response = self.client.chat.completions.create(**payload)
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

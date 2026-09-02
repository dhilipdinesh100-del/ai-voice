import re
from typing import List, Dict, Any, Generator, Optional
from app.services.llm.provider import LLMProvider
from app.logging_config import logger

class MockLLMProvider(LLMProvider):
    """
    Intelligent simulated assistant provider.
    Enables complete system verification, offline demonstrations, and automated testing
    even when an external paid API key is not configured.
    """
    def _inspect_intent(self, user_text: str) -> Optional[Dict[str, Any]]:
        text = user_text.lower().strip()
        
        # 1. Calculator intent (supporting spoken variations: "times", "divided by", "plus", "minus", "square root of")
        spoken_math = text
        spoken_math = re.sub(r'\btimes\b|\bmultiplied by\b', '*', spoken_math)
        spoken_math = re.sub(r'\bdivided by\b|\bover\b', '/', spoken_math)
        spoken_math = re.sub(r'\bplus\b', '+', spoken_math)
        spoken_math = re.sub(r'\bminus\b', '-', spoken_math)
        spoken_math = re.sub(r'\bsquare root of\s*(\d+)', r'sqrt(\1)', spoken_math)

        # Check for percentage e.g. "15% of 200" or "15 percent of 200"
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|percent)\s*of\s*(\d+(?:\.\d+)?)', spoken_math)
        if pct_match:
            pct = float(pct_match.group(1)) / 100.0
            base = pct_match.group(2)
            return {
                "id": "mock_call_calc",
                "name": "calculator",
                "arguments": {"expression": f"{base} * {pct}"}
            }

        if any(w in spoken_math for w in ["calculate", "compute", "what is", "evaluate", "solve", "sqrt"]) or (
            any(op in spoken_math for op in ["+", "-", "*", "/", "^"]) and any(char.isdigit() for char in spoken_math)
        ):
            # Extract clean mathematical expression
            clean_expr = re.sub(r'^(?:please\s+)?(?:calculate|compute|what is|evaluate|solve)\s*', '', spoken_math).strip()
            clean_expr = clean_expr.rstrip("?").strip()
            math_chars = re.findall(r'[0-9\+\-\*\/\^\(\)\.\s]|sqrt|abs|round', clean_expr)
            candidate = "".join(math_chars).strip()
            if candidate and any(char.isdigit() for char in candidate):
                return {
                    "id": "mock_call_calc",
                    "name": "calculator",
                    "arguments": {"expression": candidate}
                }

        # 2. Time intent (e.g. "What time is it?", "Can you tell me the time?", "What time is it right now?", "Current time in Tokyo")
        if any(w in text for w in ["time", "clock"]) or re.search(r'\bwhat(?:\'s| is) the time\b|\btell me the time\b', text):
            city = "local"
            for c in ["tokyo", "london", "new york", "paris", "san francisco", "sydney", "delhi", "mumbai", "dubai", "berlin", "chennai", "singapore", "los angeles"]:
                if c in text:
                    city = c
                    break
            return {
                "id": "mock_call_time",
                "name": "time",
                "arguments": {"city_or_location": city}
            }

        # 3. Weather intent (e.g. "What's the weather?", "How is the weather in London?", "Is it raining in San Francisco?")
        if any(w in text for w in ["weather", "temperature", "forecast", "raining", "rain in", "sunny in"]):
            city = "San Francisco"
            in_match = re.search(r'\b(?:in|for)\s+([a-zA-Z\s]+?)(?:\?|$|\.|\,)', text)
            if in_match:
                extracted = in_match.group(1).strip()
                if extracted:
                    city = extracted
            return {
                "id": "mock_call_weather",
                "name": "weather",
                "arguments": {"city": city}
            }

        # 4. Notes creation and listing (e.g. "Create a note saying study Python", "Make a note that I need to study Python")
        if any(phrase in text for phrase in [
            "take a note", "create a note", "make a note", "write down", "new note", "note:"
        ]):
            content = re.sub(
                r'^(?:please\s+)?(?:take a note|create a note|make a note|write down|new note|note:)\s*(?:saying|that|to|:)?\s*',
                '',
                text,
                flags=re.IGNORECASE
            ).strip()
            if not content:
                content = user_text
            title = content[:30].capitalize()
            return {
                "id": "mock_call_notes_create",
                "name": "notes",
                "arguments": {"action": "create", "title": title, "content": content}
            }
        elif "notes" in text and any(w in text for w in ["list", "show", "get", "my", "read"]):
            return {
                "id": "mock_call_notes_list",
                "name": "notes",
                "arguments": {"action": "list"}
            }

        # 5. Reminders creation and listing (e.g. "Remind me to study tomorrow", "Set a reminder for me to study")
        if any(phrase in text for phrase in [
            "remind me", "set a reminder", "create reminder", "make a reminder", "new reminder"
        ]):
            rem_match = re.search(
                r'(?:remind me to|set a reminder (?:for me )?to|create reminder to|make a reminder to)\s+(.+?)(?:\s+(?:at|on|for)\s+(.+))?$',
                text,
                flags=re.IGNORECASE
            )
            if rem_match:
                task = rem_match.group(1).strip()
                due = rem_match.group(2).strip() if rem_match.group(2) else "Tomorrow"
            else:
                task = re.sub(r'^(?:remind me|set a reminder (?:for me)?|create reminder|new reminder)\s*(?:to|that)?\s*', '', text, flags=re.IGNORECASE).strip()
                due = "Tomorrow"
            return {
                "id": "mock_call_reminders_create",
                "name": "reminders",
                "arguments": {"action": "create", "text": task.capitalize() or "Task", "due_at": due}
            }
        elif "reminder" in text and any(w in text for w in ["list", "show", "get", "my", "read", "pending"]):
            return {
                "id": "mock_call_reminders_list",
                "name": "reminders",
                "arguments": {"action": "list"}
            }

        # 6. Knowledge / Document intent
        if any(w in text for w in ["search document", "search docs", "in my documents", "knowledge base search", "what does the doc", "what does the document"]):
            query = re.sub(r'^(?:search document for|search docs for|in my documents|knowledge base search:?)\s*', '', text).strip()
            return {
                "id": "mock_call_knowledge",
                "name": "knowledge_search",
                "arguments": {"query": query or text}
            }

        # 7. Web Search intent
        if any(w in text for w in ["search for", "google", "look up", "news today", "latest on"]):
            query = re.sub(r'^(?:search for|google|look up)\s*', '', text).strip()
            return {
                "id": "mock_call_search",
                "name": "web_search",
                "arguments": {"query": query or text}
            }

        return None

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        last_user_msg = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        last_lower = last_user_msg.lower().strip()
        
        # Check personality hints from system_prompt
        is_concise = "concise" in system_prompt.lower()
        is_futuristic = "futuristic" in system_prompt.lower()
        is_empathetic = "empathetic" in system_prompt.lower()

        # Check if this is a follow-up after a tool call execution
        tool_results = [m for m in messages if m.get("role") == "tool"]
        if tool_results:
            latest_result = tool_results[-1]["content"]
            if is_concise:
                content = f"Result: {latest_result}"
            elif is_futuristic:
                content = f"Subroutine completed. Telemetry data: {latest_result}"
            elif is_empathetic:
                content = f"I took care of that for you! Here are the details: {latest_result}"
            else:
                content = f"Here is the result: {latest_result}"
            return {"content": content, "tool_calls": None, "raw": None}

        # Check for tool intent if tools are enabled
        if tools:
            tool_call = self._inspect_intent(last_user_msg)
            if tool_call:
                return {
                    "content": "",
                    "tool_calls": [tool_call],
                    "raw": None
                }

        # Rich simulated conversational responses for demo realism
        if any(w in last_lower for w in ["who are you", "what is your name", "introduce yourself"]):
            ans = (
                "I am NOVA, your voice-first conversational AI assistant operating in high-fidelity Simulation Mode. "
                "I can perform calculations, track worldwide time, coordinate notes & reminders, "
                "retrieve knowledge base documents, and simulate natural speech synthesis completely locally."
            )
        elif any(w in last_lower for w in ["what can you do", "help", "capabilities", "features"]):
            ans = (
                "Here are several core capabilities you can explore right now:\n"
                "• **Real-Time Math**: `Calculate (15 * 8) + sqrt(144)`\n"
                "• **Global Time**: `What time is it in Tokyo?`\n"
                "• **Live Weather**: `How is the weather in San Francisco?`\n"
                "• **Smart Notes**: `Take a note: Review quarterly architecture`\n"
                "• **Reminders**: `Remind me to sync with the team at 4 PM`\n"
                "• **RAG Knowledge**: Upload a document and query its contents\n"
                "• **Command Palette**: Press `Ctrl+K` for instant keyboard shortcuts\n"
                "• **Voice Controls**: Click the glowing Orb or tap the microphone"
            )
        elif any(w in last_lower for w in ["system status", "diagnostics", "health", "system health"]):
            ans = (
                "**NOVA System Diagnostics**:\n"
                "• **Operating Mode**: Simulation Mode (Offline/Local Engine Active)\n"
                "• **Core State Machine**: Online (Idle / Listening / Processing / Speaking)\n"
                "• **Audio Visualizer**: Web Audio API 64-band frequency analyzer active\n"
                "• **Tool Registry**: 7 built-in modules registered & ready\n"
                "• **Database Engine**: SQLite persistent storage connected\n"
                "• **External Key**: Not required for simulation mode"
            )
        elif "simulation mode" in last_lower or "demo mode" in last_lower:
            ans = (
                "NOVA's Simulation Mode provides a fully functioning, zero-cost demonstration environment. "
                "All arithmetic, time zones, weather diagnostics, note organization, reminder management, "
                "and RAG document processing run entirely on your local machine with zero external API dependencies."
            )
        elif "rag" in last_lower:
            ans = (
                "Retrieval-Augmented Generation (RAG) empowers NOVA to ingest your documents (PDFs, text, markdown), "
                "slice them into semantically coherent chunks, and query them on demand so you get factual, grounded answers."
            )
        elif any(w in last_lower for w in ["hello", "hi", "hey", "good morning", "good evening"]):
            if is_concise:
                ans = "Hello. NOVA is online and ready for input."
            elif is_futuristic:
                ans = "Greetings. NOVA core interface initialized. Awaiting your voice or text directives."
            elif is_empathetic:
                ans = "Hello! It's great to connect with you today. How can I help make your day smoother?"
            else:
                ans = "Hello! I am NOVA, your AI voice assistant. All systems and analytical pipelines are online."
        else:
            if is_concise:
                ans = f"Understood. Ready to assist with '{last_user_msg}'."
            elif is_futuristic:
                ans = f"Directive acknowledged. Processing parameter '{last_user_msg}'. All analytical pipelines are active."
            elif is_empathetic:
                ans = f"I've noted that for you! Let's explore '{last_user_msg}' together."
            else:
                ans = f"Understood. Regarding '{last_user_msg}', I am ready to assist. All systems and analytical pipelines are online."

        return {
            "content": ans,
            "tool_calls": None,
            "raw": None
        }

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[str, None, None]:
        res = self.generate_response(messages, system_prompt, tools=tools)
        text = res["content"] or "Processing completed."
        words = text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == len(words) - 1 else word + " "
            yield chunk


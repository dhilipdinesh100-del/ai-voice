import json
from typing import Dict, Any, List, Optional, Generator
from app.database.repositories.conversation_repo import ConversationRepository
from app.database.repositories.message_repo import MessageRepository
from app.database.repositories.settings_repo import SettingsRepository
from app.database.repositories.memory_repo import MemoryRepository
from app.services.personality import build_system_prompt
from app.services.llm import get_llm_provider
from app.services.speech.tts_provider import get_tts_provider
from app.services.tools.registry import tool_registry
import app.services.tools.builtins  # Ensure builtin tools are registered
from app.logging_config import logger

class ConversationService:
    @staticmethod
    def process_chat(
        conversation_id: Optional[str],
        user_text: str,
        generate_audio: bool = False
    ) -> Dict[str, Any]:
        # 1. Resolve or create conversation
        if not conversation_id:
            title = user_text[:35] + ("..." if len(user_text) > 35 else "")
            conv = ConversationRepository.create(title=title)
            conversation_id = conv["id"]
        else:
            conv = ConversationRepository.get_by_id(conversation_id)
            if not conv:
                conv = ConversationRepository.create(title=user_text[:35])
                conversation_id = conv["id"]

        # 2. Persist user message
        user_msg = MessageRepository.add_message(
            conversation_id=conversation_id,
            role="user",
            content=user_text
        )

        # 3. Retrieve settings
        user_settings = SettingsRepository.get_all()
        personality = user_settings.get("personality", "Futuristic")
        custom_prompt = user_settings.get("custom_prompt", "")
        language = user_settings.get("language", "en")
        memory_enabled = user_settings.get("memory_enabled", True)

        # 4. Fetch memories if enabled
        memories = MemoryRepository.list_all() if memory_enabled else []
        
        # 5. Build prompt & prepare message history
        sys_prompt = build_system_prompt(
            personality_name=personality,
            custom_prompt=custom_prompt,
            language=language,
            memories=memories
        )

        history = MessageRepository.get_by_conversation(conversation_id, limit=20)
        llm_messages = [{"role": m["role"], "content": m["content"]} for m in history]

        # 6. Execute with LLM & Tool loop
        llm = get_llm_provider()
        tools = tool_registry.to_openai_tools()
        
        response = llm.generate_response(llm_messages, sys_prompt, tools=tools)
        tool_calls = response.get("tool_calls")
        executed_tools_meta = []

        if tool_calls:
            for tc in tool_calls:
                name = tc["name"]
                args = tc["arguments"]
                logger.info("Executing tool call: %s with args: %s", name, args)
                res = tool_registry.execute(name, args)
                tool_output = str(res.get("result") if res.get("status") == "success" else res.get("error"))
                executed_tools_meta.append({
                    "name": name,
                    "arguments": args,
                    "result": res
                })
                # Add tool output to history
                llm_messages.append({"role": "assistant", "content": f"Invoking tool {name}"})
                llm_messages.append({"role": "tool", "content": tool_output})

            # Get final synthesized answer
            second_response = llm.generate_response(llm_messages, sys_prompt, tools=None)
            final_text = second_response.get("content", "Task completed.")
        else:
            final_text = response.get("content", "I am ready.")

        # 7. Generate Speech Audio if requested
        audio_url = None
        if generate_audio or user_settings.get("auto_play", True):
            try:
                tts = get_tts_provider()
                voice = user_settings.get("voice", "alloy")
                speed = user_settings.get("voice_speed", 1.0)
                audio_file = tts.synthesize(text=final_text, voice=voice, speed=speed)
                audio_url = f"/api/audio/{audio_file.name}"
            except Exception as e:
                logger.error("TTS generation failed: %s", e)

        # 8. Persist assistant message
        asst_msg = MessageRepository.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=final_text,
            audio_reference=audio_url,
            tool_metadata={"tools": executed_tools_meta} if executed_tools_meta else None
        )

        return {
            "conversation_id": conversation_id,
            "user_message": user_msg,
            "assistant_message": asst_msg,
            "answer": final_text,
            "transcript": user_text,
            "audio_url": audio_url,
            "tool_calls": executed_tools_meta
        }

    @staticmethod
    def stream_chat(
        conversation_id: Optional[str],
        user_text: str
    ) -> Generator[str, None, None]:
        """
        Server-Sent Events (SSE) generator for streaming tokens.
        Format:
        data: {"event": "start", "conversation_id": "..."}
        data: {"event": "tool", "tool": "calculator", "status": "invoking"}
        data: {"event": "chunk", "token": "..."}
        data: {"event": "done", "audio_url": "..."}
        """
        # Resolve conversation
        if not conversation_id:
            conv = ConversationRepository.create(title=user_text[:35])
            conversation_id = conv["id"]
            
        yield f"data: {json.dumps({'event': 'start', 'conversation_id': conversation_id})}\n\n"
        
        # Save user message
        MessageRepository.add_message(conversation_id=conversation_id, role="user", content=user_text)

        user_settings = SettingsRepository.get_all()
        personality = user_settings.get("personality", "Futuristic")
        custom_prompt = user_settings.get("custom_prompt", "")
        language = user_settings.get("language", "en")
        memory_enabled = user_settings.get("memory_enabled", True)

        memories = MemoryRepository.list_all() if memory_enabled else []
        sys_prompt = build_system_prompt(
            personality_name=personality,
            custom_prompt=custom_prompt,
            language=language,
            memories=memories
        )

        history = MessageRepository.get_by_conversation(conversation_id, limit=20)
        llm_messages = [{"role": m["role"], "content": m["content"]} for m in history]

        llm = get_llm_provider()
        tools = tool_registry.to_openai_tools()

        # Check if there is a tool execution needed
        first_resp = llm.generate_response(llm_messages, sys_prompt, tools=tools)
        tool_calls = first_resp.get("tool_calls")
        executed_tools = []

        if tool_calls:
            for tc in tool_calls:
                name = tc["name"]
                args = tc["arguments"]
                yield f"data: {json.dumps({'event': 'tool', 'name': name, 'status': 'running'})}\n\n"
                res = tool_registry.execute(name, args)
                tool_output = str(res.get("result") if res.get("status") == "success" else res.get("error"))
                executed_tools.append({"name": name, "arguments": args, "result": res})
                llm_messages.append({"role": "assistant", "content": f"Invoking {name}"})
                llm_messages.append({"role": "tool", "content": tool_output})

        full_accumulated = []
        for chunk in llm.generate_stream(llm_messages, sys_prompt):
            full_accumulated.append(chunk)
            yield f"data: {json.dumps({'event': 'chunk', 'token': chunk})}\n\n"

        full_text = "".join(full_accumulated).strip() or "Understood."

        # Generate audio
        audio_url = None
        if user_settings.get("auto_play", True):
            try:
                tts = get_tts_provider()
                voice = user_settings.get("voice", "alloy")
                speed = user_settings.get("voice_speed", 1.0)
                audio_file = tts.synthesize(text=full_text, voice=voice, speed=speed)
                audio_url = f"/api/audio/{audio_file.name}"
            except Exception as e:
                logger.error("Streaming TTS generation failed: %s", e)

        # Save assistant message
        MessageRepository.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_text,
            audio_reference=audio_url,
            tool_metadata={"tools": executed_tools} if executed_tools else None
        )

        yield f"data: {json.dumps({'event': 'done', 'audio_url': audio_url, 'content': full_text})}\n\n"

conversation_service = ConversationService()

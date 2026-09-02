import pytest
from app.services.tools.builtins import tool_calculator, tool_time, tool_weather, tool_web_search
from app.services.rag.chunker import chunk_text
from app.services.personality import build_system_prompt

def test_safe_calculator():
    # Standard math
    res1 = tool_calculator("234 * 72")
    assert "16848" in res1

    # Order of operations & powers
    res2 = tool_calculator("(12 + 8) * 5 - 2^3")
    assert "92" in res2

    # Math function
    res3 = tool_calculator("sqrt(144) + 8")
    assert "20" in res3

    # Malicious code injection attempt must fail safely
    malicious = tool_calculator("__import__('os').system('ls')")
    assert "Calculation error" in malicious

def test_time_tool():
    res_local = tool_time("local")
    assert "Current time" in res_local

    res_tokyo = tool_time("Tokyo")
    assert "Tokyo" in res_tokyo
    assert "UTC+9" in res_tokyo

def test_weather_tool():
    res = tool_weather("London")
    assert "Weather in London" in res
    assert "Temperature" in res

def test_web_search_tool():
    res = tool_web_search("Python programming language")
    assert len(res) > 0

def test_text_chunking():
    sample = "Word " * 600
    chunks = chunk_text(sample, chunk_size=300, overlap=50)
    assert len(chunks) >= 2
    assert all(len(c) > 0 for c in chunks)

def test_personality_system_prompt():
    prompt = build_system_prompt(
        personality_name="Concise",
        language="ta",
        memories=[{"content": "User is a senior engineer"}]
    )
    assert "NOVA" in prompt
    assert "Tamil" in prompt
    assert "senior engineer" in prompt

def test_mock_llm_enhanced_simulation():
    from app.services.llm.mock_llm import MockLLMProvider
    provider = MockLLMProvider()

    # 1. Math intent
    calc_intent = provider._inspect_intent("Calculate (15 * 8) + sqrt(144)")
    assert calc_intent is not None
    assert calc_intent["name"] == "calculator"
    assert "15" in calc_intent["arguments"]["expression"]

    # 2. Time intent
    time_intent = provider._inspect_intent("What time is it in Tokyo?")
    assert time_intent is not None
    assert time_intent["name"] == "time"
    assert time_intent["arguments"]["city_or_location"] == "tokyo"

    # 3. Note intent
    note_intent = provider._inspect_intent("Take a note: Review Q3 architecture")
    assert note_intent is not None
    assert note_intent["name"] == "notes"
    assert note_intent["arguments"]["action"] == "create"
    assert "architecture" in note_intent["arguments"]["content"].lower()

    # 4. Reminder intent
    rem_intent = provider._inspect_intent("Remind me to sync with the team at 4 PM")
    assert rem_intent is not None
    assert rem_intent["name"] == "reminders"
    assert rem_intent["arguments"]["action"] == "create"

    # 5. System status response
    status_resp = provider.generate_response(
        messages=[{"role": "user", "content": "Check system status"}],
        system_prompt="You are NOVA."
    )
    assert "NOVA System Diagnostics" in status_resp["content"]
    assert "Simulation Mode" in status_resp["content"]


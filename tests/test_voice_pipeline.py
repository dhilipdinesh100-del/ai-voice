import io
import pytest

def test_voice_transcript_to_normal_response(client):
    # Simulated voice transcript routed into unified pipeline
    payload = {
        "text": "Hello NOVA, who are you and what are your capabilities?",
        "generate_audio": False
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 10
    assert "NOVA" in data["answer"]

def test_voice_transcript_to_calculator(client):
    # 1. Spoken multiplication variation ("times")
    payload1 = {
        "text": "Calculate 25 times 4",
        "generate_audio": False
    }
    res1 = client.post("/api/chat", json=payload1)
    assert res1.status_code == 200
    assert "100" in res1.json()["answer"]

    # 2. Spoken division variation ("divided by")
    payload2 = {
        "text": "Please calculate 100 divided by 4",
        "generate_audio": False
    }
    res2 = client.post("/api/chat", json=payload2)
    assert res2.status_code == 200
    assert "25" in res2.json()["answer"]

    # 3. Spoken addition ("plus")
    payload3 = {
        "text": "What is 15 plus 80?",
        "generate_audio": False
    }
    res3 = client.post("/api/chat", json=payload3)
    assert res3.status_code == 200
    assert "95" in res3.json()["answer"]

def test_voice_transcript_to_time(client):
    # 1. Spoken city time
    payload1 = {
        "text": "What time is it in Tokyo right now?",
        "generate_audio": False
    }
    res1 = client.post("/api/chat", json=payload1)
    assert res1.status_code == 200
    ans1 = res1.json()["answer"]
    assert "Tokyo" in ans1
    assert "UTC+9" in ans1

    # 2. Spoken general time inquiry
    payload2 = {
        "text": "Can you tell me the time?",
        "generate_audio": False
    }
    res2 = client.post("/api/chat", json=payload2)
    assert res2.status_code == 200
    assert "Current time" in res2.json()["answer"]

def test_voice_transcript_to_weather(client):
    # 1. Spoken weather for city
    payload1 = {
        "text": "What's the weather in London?",
        "generate_audio": False
    }
    res1 = client.post("/api/chat", json=payload1)
    assert res1.status_code == 200
    ans1 = res1.json()["answer"]
    assert "London" in ans1
    assert "Temperature" in ans1

    # 2. Spoken weather variation
    payload2 = {
        "text": "How is the weather in San Francisco?",
        "generate_audio": False
    }
    res2 = client.post("/api/chat", json=payload2)
    assert res2.status_code == 200
    ans2 = res2.json()["answer"]
    assert "San Francisco" in ans2

def test_voice_transcript_to_note(client):
    # 1. Spoken note creation variation 1
    payload1 = {
        "text": "Create a note saying study Python",
        "generate_audio": False
    }
    res1 = client.post("/api/chat", json=payload1)
    assert res1.status_code == 200
    assert "Note created" in res1.json()["answer"] or "Study python" in res1.json()["answer"]

    # 2. Spoken note creation variation 2
    payload2 = {
        "text": "Make a note that I need to review the architecture",
        "generate_audio": False
    }
    res2 = client.post("/api/chat", json=payload2)
    assert res2.status_code == 200
    assert "Note created" in res2.json()["answer"] or "architecture" in res2.json()["answer"]

def test_voice_transcript_to_reminder(client):
    # 1. Spoken reminder variation 1
    payload1 = {
        "text": "Remind me to study tomorrow",
        "generate_audio": False
    }
    res1 = client.post("/api/chat", json=payload1)
    assert res1.status_code == 200
    assert "Reminder set" in res1.json()["answer"] or "Study tomorrow" in res1.json()["answer"]

    # 2. Spoken reminder variation 2
    payload2 = {
        "text": "Set a reminder for me to deploy at 5 PM",
        "generate_audio": False
    }
    res2 = client.post("/api/chat", json=payload2)
    assert res2.status_code == 200
    assert "Reminder set" in res2.json()["answer"] or "deploy" in res2.json()["answer"].lower()

def test_empty_transcript_handling(client):
    # Empty transcript must be rejected with validation error (400 or 422)
    res1 = client.post("/api/chat", json={"text": ""})
    assert res1.status_code in [400, 422]

    res2 = client.post("/api/chat", json={"text": "     "})
    assert res2.status_code in [400, 422]

def test_stt_unavailable_honest_response(client):
    # When no OpenAI key is provided, audio upload to /api/voice/transcribe
    # must return HTTP 501 instead of a fake dummy transcript
    fake_audio_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    files = {"audio": ("sample.wav", io.BytesIO(fake_audio_bytes), "audio/wav")}
    response = client.post("/api/voice/transcribe", files=files)
    
    # Must report 501 (Not Implemented / Unavailable without OpenAI key)
    assert response.status_code == 501
    detail = response.json().get("detail", "")
    assert "OPENAI_API_KEY" in detail
    assert "Simulation Mode" in detail

def test_simulation_mode_status(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mode"] == "simulation"

import io

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["assistant"] == "NOVA"
    assert "mode" in data

def test_root_serves_frontend_html(client):
    """Verify / serves the live NOVA application, not README or raw markdown."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    html = response.text
    assert "<!doctype html>" in html.lower()
    assert "NOVA — Premium Voice AI Assistant" in html
    assert "id=\"aiOrbCore\"" in html
    assert "id=\"chatTextInput\"" in html
    assert "/static/css/main.css" in html
    assert "/static/js/app.js" in html
    # Verify it does NOT return markdown or README
    assert not html.strip().startswith("#")
    assert "```bash" not in html

    # Also verify /index.html
    res_index = client.get("/index.html")
    assert res_index.status_code == 200
    assert "id=\"aiOrbCore\"" in res_index.text

def test_static_assets_and_docs(client):
    """Verify static CSS, JS, and FastAPI interactive docs are served correctly."""
    # CSS
    css_res = client.get("/static/css/main.css")
    assert css_res.status_code == 200
    assert "text/css" in css_res.headers.get("content-type", "")

    # JS
    js_res = client.get("/static/js/app.js")
    assert js_res.status_code == 200
    assert "javascript" in js_res.headers.get("content-type", "")

    # Docs
    docs_res = client.get("/docs")
    assert docs_res.status_code == 200
    assert "text/html" in docs_res.headers.get("content-type", "")

def test_chat_endpoint(client):
    payload = {
        "text": "Hello NOVA, how are you?",
        "generate_audio": False
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "answer" in data
    assert len(data["answer"]) > 0

def test_chat_validation(client):
    response = client.post("/api/chat", json={"text": "   "})
    assert response.status_code == 400

def test_conversations_crud(client):
    # 1. Create conversation
    create_res = client.post("/api/conversations", json={"title": "Test AI Chat"})
    assert create_res.status_code == 200
    conv = create_res.json()
    conv_id = conv["id"]
    assert conv["title"] == "Test AI Chat"

    # 2. List conversations
    list_res = client.get("/api/conversations")
    assert list_res.status_code == 200
    convs = list_res.json()
    assert any(c["id"] == conv_id for c in convs)

    # 3. Rename conversation
    patch_res = client.patch(f"/api/conversations/{conv_id}", json={"title": "Updated Chat Title"})
    assert patch_res.status_code == 200

    # 4. Get conversation detail
    detail_res = client.get(f"/api/conversations/{conv_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == "Updated Chat Title"

    # 5. Export conversation
    export_res = client.get(f"/api/conversations/{conv_id}/export")
    assert export_res.status_code == 200
    assert "messages" in export_res.json()

    # 6. Delete conversation
    del_res = client.delete(f"/api/conversations/{conv_id}")
    assert del_res.status_code == 200

    # Verify 404 on deleted conversation
    get_del = client.get(f"/api/conversations/{conv_id}")
    assert get_del.status_code == 404

def test_settings_endpoints(client):
    # Fetch settings
    res = client.get("/api/settings")
    assert res.status_code == 200
    settings = res.json()
    assert "personality" in settings

    # Update settings
    patch_res = client.patch("/api/settings", json={"personality": "Concise", "voice_speed": 1.2})
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["personality"] == "Concise"
    assert updated["voice_speed"] == 1.2

def test_memories_crud(client):
    # Add memory
    add_res = client.post("/api/memories", json={"content": "User prefers concise answers in Python", "category": "preference"})
    assert add_res.status_code == 200
    mem = add_res.json()
    mem_id = mem["id"]

    # List memories
    list_res = client.get("/api/memories")
    assert list_res.status_code == 200
    mems = list_res.json()
    assert any(m["id"] == mem_id for m in mems)

    # Delete memory
    del_res = client.delete(f"/api/memories/{mem_id}")
    assert del_res.status_code == 200

def test_tools_endpoint(client):
    # List tools
    res = client.get("/api/tools")
    assert res.status_code == 200
    tools = res.json()
    tool_names = [t["name"] for t in tools]
    assert "calculator" in tool_names
    assert "time" in tool_names
    assert "weather" in tool_names
    assert "web_search" in tool_names

    # Execute tool directly
    calc_res = client.post("/api/tools/execute", json={
        "name": "calculator",
        "arguments": {"expression": "15 * 6"}
    })
    assert calc_res.status_code == 200
    assert "90" in calc_res.json()["result"]

def test_notes_and_reminders(client):
    # Note
    note_res = client.post("/api/notes", json={"title": "Test Meeting", "content": "Review voice architecture."})
    assert note_res.status_code == 200
    note_id = note_res.json()["id"]

    notes_list = client.get("/api/notes")
    assert notes_list.status_code == 200
    assert any(n["id"] == note_id for n in notes_list.json())

    # Reminder
    rem_res = client.post("/api/reminders", json={"text": "Deploy to server", "due_at": "Tomorrow 10 AM"})
    assert rem_res.status_code == 200
    rem_id = rem_res.json()["id"]

    toggle_res = client.patch(f"/api/reminders/{rem_id}/toggle")
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_completed"] is True

def test_knowledge_upload_and_query(client):
    content = b"Artificial Intelligence Voice Systems provide conversational speech processing."
    file = io.BytesIO(content)
    upload_res = client.post(
        "/api/knowledge/upload",
        files={"file": ("test_doc.txt", file, "text/plain")}
    )
    assert upload_res.status_code == 200
    doc = upload_res.json()
    assert doc["filename"] == "test_doc.txt"
    assert doc["status"] == "ready"

    # Query knowledge
    query_res = client.post("/api/knowledge/query", json={"query": "conversational speech"})
    assert query_res.status_code == 200
    assert "test_doc.txt" in query_res.json()["context"]

    # Delete doc
    del_res = client.delete(f"/api/knowledge/documents/{doc['id']}")
    assert del_res.status_code == 200

def test_legacy_backward_compatibility(client):
    # /api/text
    res = client.post("/api/text", json={"text": "What is AI?"})
    assert res.status_code == 200
    assert "transcript" in res.json()
    assert "answer" in res.json()

    # Audio endpoint path traversal security test
    bad_audio_res = client.get("/api/audio/../../etc/passwd")
    assert bad_audio_res.status_code in (400, 404)

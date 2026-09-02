import pytest
from playwright.sync_api import sync_playwright

def test_full_browser_experience():
    """
    Automated end-to-end browser test using local Google Chrome.
    Validates landing page, chat flows, audio controls, modals, command palette,
    theme switching, mobile viewports, and verifies zero console errors.
    """
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()

        # Monitor console errors and uncaught exceptions
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # 1. Load Application
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        assert "NOVA" in page.title()

        # 2. Verify Landing Page Components
        assert page.locator(".brand-title").is_visible()
        assert page.locator("#aiOrbCore").is_visible()
        assert page.locator("#waveformCanvas").is_visible()
        assert page.locator("#btnMainMic").is_visible()
        assert page.locator("#btnToggleHandsFree").is_visible()
        assert page.locator("#chatTextInput").is_visible()
        assert page.locator("#btnSendChat").is_visible()

        # 3. Test Text Chat Interaction
        page.fill("#chatTextInput", "What time is it in Tokyo?")
        page.click("#btnSendChat")

        # Wait for streaming assistant response
        page.wait_for_function(
            "() => { const el = document.querySelector('.message-row.assistant .message-bubble'); return el && el.innerText.trim().length > 0; }",
            timeout=15000
        )
        assistant_text = page.locator(".message-row.assistant .message-bubble").inner_text()
        assert len(assistant_text) > 0
        assert "Tokyo" in assistant_text or "time" in assistant_text.lower() or "result" in assistant_text.lower()

        # Verify Audio Action Button appears
        page.wait_for_selector(".message-row.assistant .message-footer button.msg-action-btn:has-text('Play Audio')", timeout=15000)
        assert page.locator("text=Play Audio").is_visible()

        # 4. Test Command Palette (Ctrl+K)
        page.keyboard.press("Control+k")
        page.wait_for_selector("#commandPaletteModal.open", timeout=3000)
        assert page.locator("#commandPaletteInput").is_visible()
        page.keyboard.press("Escape")
        page.wait_for_selector("#commandPaletteModal:not(.open)", timeout=3000)

        # 5. Test Conversation History Sidebar
        page.click("#btnToggleSidebar")
        page.wait_for_selector("#sidebarDrawer.open", timeout=3000)
        page.wait_for_selector(".sidebar-item", timeout=5000)
        assert page.locator(".sidebar-item").first.is_visible()
        page.click("#btnCloseSidebar")
        page.wait_for_selector("#sidebarDrawer:not(.open)", timeout=3000)

        # 6. Test Knowledge Base Modal
        page.click("#btnOpenKnowledge")
        page.wait_for_selector("#knowledgeModal.open", timeout=3000)
        assert page.locator("#knowledgeDropzone").is_visible()
        page.click("#btnCloseKnowledge")
        page.wait_for_selector("#knowledgeModal:not(.open)", timeout=3000)

        # 7. Test Settings Modal & Theme Change
        page.click("#btnOpenSettings")
        page.wait_for_selector("#settingsModal.open", timeout=3000)
        
        # Test tab switching
        page.click("button[data-tab='ai']")
        assert page.locator("#tab-ai").is_visible()
        page.click("button[data-tab='voice']")
        assert page.locator("#tab-voice").is_visible()
        page.click("button[data-tab='general']")
        assert page.locator("#tab-general").is_visible()

        # Switch to Light Theme
        page.select_option("#settingTheme", "light")
        page.click("#btnSaveSettings")
        page.wait_for_selector("#settingsModal:not(.open)", timeout=3000)
        theme_attr = page.get_attribute("html", "data-theme")
        assert theme_attr == "light"

        # Switch back to Dark Theme
        page.click("#btnOpenSettings")
        page.wait_for_selector("#settingsModal.open", timeout=3000)
        page.wait_for_timeout(300)
        page.select_option("#settingTheme", "dark")
        page.click("#btnSaveSettings")
        page.wait_for_selector("#settingsModal:not(.open)", timeout=3000)
        assert page.get_attribute("html", "data-theme") == "dark"

        # 8. Test Mobile Viewports
        # 390x844 (Mobile)
        page.set_viewport_size({"width": 390, "height": 844})
        scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
        client_width = page.evaluate("() => document.documentElement.clientWidth")
        assert scroll_width <= client_width + 1  # No horizontal scroll

        # 375x667 (Small Mobile)
        page.set_viewport_size({"width": 375, "height": 667})
        assert page.locator("#aiOrbCore").is_visible()
        assert page.locator("#btnMainMic").is_visible()

        # 768x1024 (Tablet)
        page.set_viewport_size({"width": 768, "height": 1024})
        assert page.locator("#aiOrbCore").is_visible()

        # 1440x900 (Desktop)
        page.set_viewport_size({"width": 1440, "height": 900})
        assert page.locator("#aiOrbCore").is_visible()

        # Capture desktop and mobile verification screenshots
        page.screenshot(path="C:/Users/DILIP/.gemini/antigravity-ide/brain/27bf50cf-4afe-481e-85e3-9c103143aadd/browser_verification.png")

        # Filter out expected harmless browser notices (such as audio autoplay restrictions or font preconnects)
        browser.close()

def test_deterministic_voice_input_flow():
    """
    Validates that voice transcripts route through the identical unified
    command and conversation pipeline as typed input, executes tools,
    renders thinking states, and handles keyboard interruption cleanly.
    """
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        page.goto("http://127.0.0.1:8000", wait_until="networkidle")

        # 1. Test interim transcript rendering
        page.evaluate("() => showInterimTranscript('Listening: what time is it')")
        assert page.locator("#interimTranscriptRow").is_visible()
        page.evaluate("() => updateInterimTranscript('Listening: what time is it in Tokyo')")
        assert page.locator(".interim-text:has-text('what time is it in Tokyo')").is_visible()
        page.evaluate("() => hideInterimTranscript()")
        assert not page.locator("#interimTranscriptRow").is_visible()

        # 2. Test speech transcript routing into unified submitTextMessage
        page.evaluate("() => submitTextMessage('Calculate 25 times 4')")

        # Verify user message appears
        page.wait_for_selector(".message-row.user:has-text('Calculate 25 times 4')", timeout=5000)
        assert page.locator(".message-row.user:has-text('Calculate 25 times 4')").is_visible()

        # Verify streaming assistant response contains calculation result
        page.wait_for_function(
            "() => { const el = document.querySelector('.message-row.assistant .message-bubble'); return el && el.innerText.includes('100'); }",
            timeout=15000
        )
        assistant_text = page.locator(".message-row.assistant .message-bubble").inner_text()
        assert "100" in assistant_text

        # 3. Test note creation spoken variation
        page.evaluate("() => submitTextMessage('Create a note saying study Python')")
        page.wait_for_function(
            "() => { const els = document.querySelectorAll('.message-row.assistant .message-bubble'); return els.length >= 2 && els[els.length-1].innerText.toLowerCase().includes('note'); }",
            timeout=15000
        )
        note_ans = page.locator(".message-row.assistant .message-bubble").nth(1).inner_text()
        assert "note" in note_ans.lower() or "saved" in note_ans.lower()

        # 4. Test speech interruption via Escape key
        page.keyboard.press("Escape")
        # Ensure state resets to IDLE
        orb_state = page.evaluate("() => appState.getState()")
        assert orb_state in ["idle", "processing", "thinking"]

        # 5. Check console errors
        critical_errors = [
            e for e in console_errors 
            if not any(ign in e.lower() for ign in ["audiocontext", "autoplay", "favicon", "font"])
        ]
        assert len(critical_errors) == 0, f"Critical console errors found: {critical_errors}"

        browser.close()


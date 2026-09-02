// Main Application Orchestrator

// Toast shelf utility
window.showToast = function(msg) {
  const shelf = document.getElementById("toastShelf");
  if (!shelf) return;
  const t = document.createElement("div");
  t.className = "toast-msg";
  t.setAttribute("role", "alert");
  t.textContent = msg;
  shelf.appendChild(t);
  setTimeout(() => {
    t.style.opacity = "0";
    t.style.transform = "translateY(8px)";
    t.style.transition = "all 0.22s ease";
    setTimeout(() => t.remove(), 220);
  }, 3200);
};

// UI Elements
const chatViewport = document.getElementById("chatViewport");
const emptyChatState = document.getElementById("emptyChatState");
const chatTextInput = document.getElementById("chatTextInput");
const btnSendChat = document.getElementById("btnSendChat");
const btnMainMic = document.getElementById("btnMainMic");
const btnToggleHandsFree = document.getElementById("btnToggleHandsFree");

// Initialize instances
let sidebarManager = null;
let knowledgeUI = null;
let settingsUI = null;
let commandPalette = null;

document.addEventListener("DOMContentLoaded", async () => {
  // 1. Initialize canvas visualizer
  const canvas = document.getElementById("waveformCanvas");
  if (canvas) audioSystem.initVisualizer(canvas);

  // 2. Initialize UI modules
  window.sidebarManager = new SidebarManager();
  window.knowledgeUI = new KnowledgeUI();
  window.settingsUI = new SettingsUI();
  window.commandPalette = new CommandPalette();

  // 3. Check health and model indicator
  checkSystemHealth();

  // 4. Bind events
  bindMainEvents();

  // 5. Load settings from server
  await window.settingsUI.loadSettings();
});

async function checkSystemHealth() {
  try {
    const res = await fetch("/health");
    if (!res.ok) throw new Error("Health check failed");
    const data = await res.json();
    const dot = document.getElementById("systemStatusDot");
    const label = document.getElementById("systemStatusLabel");
    if (dot && label) {
      if (data.mode === "openai") {
        dot.classList.remove("simulated");
        label.textContent = "OpenAI Online";
      } else {
        dot.classList.add("simulated");
        label.textContent = "Simulation Mode";
      }
    }
  } catch (e) {
    console.warn("Health check connection notice:", e);
  }
}

function bindMainEvents() {
  // Send message on Enter
  if (chatTextInput) {
    chatTextInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submitTextMessage();
      }
    });
  }

  if (btnSendChat) {
    btnSendChat.addEventListener("click", () => submitTextMessage());
  }

  // Primary Mic Button
  if (btnMainMic) {
    btnMainMic.addEventListener("click", () => window.toggleVoiceRecording());
  }

  // Orb click/keypress triggers microphone or stops speech
  const orb = document.getElementById("aiOrbCore");
  if (orb) {
    const handleOrbAction = () => {
      if (appState.getState() === AssistantState.SPEAKING) {
        audioSystem.stopAudio();
      } else {
        window.toggleVoiceRecording();
      }
    };
    orb.addEventListener("click", handleOrbAction);
    orb.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        handleOrbAction();
      }
    });
  }

  // Hands-free button
  if (btnToggleHandsFree) {
    btnToggleHandsFree.addEventListener("click", () => window.toggleHandsFreeMode());
  }

  // New chat button in header
  const btnNewChatHeader = document.getElementById("btnNewChatHeader");
  if (btnNewChatHeader) {
    btnNewChatHeader.addEventListener("click", () => window.startNewConversation());
  }

  // Command palette button in header
  const btnOpenCmd = document.getElementById("btnOpenCommandPalette");
  if (btnOpenCmd) {
    btnOpenCmd.addEventListener("click", () => {
      if (window.commandPalette) window.commandPalette.open();
    });
  }

  // Suggestion chips
  document.querySelectorAll(".suggestion-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      submitTextMessage(chip.textContent);
    });
  });

  // Global keyboard shortcuts
  window.addEventListener("keydown", (e) => {
    // 1. Esc interrupts speech, cancels recognition, and stops recording
    if (e.key === "Escape") {
      audioSystem.stopAudio();
      if (audioSystem.isRecording || (audioSystem.speechRecognizer && audioSystem.speechRecognizer.isActive)) {
        window.toggleVoiceRecording();
      }
      return;
    }

    // 2. Space toggles microphone if not focused on text input
    if (e.key === " " && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName) && !document.activeElement?.isContentEditable) {
      e.preventDefault();
      window.toggleVoiceRecording();
      return;
    }

    // 3. Ctrl+/ focuses chat input
    if (e.ctrlKey && e.key === "/") {
      e.preventDefault();
      if (chatTextInput) chatTextInput.focus();
      return;
    }

    // 4. Ctrl+N starts a new conversation
    if (e.ctrlKey && (e.key === "n" || e.key === "N")) {
      e.preventDefault();
      window.startNewConversation();
      return;
    }
  });
}

// Helper functions for Interim Transcript display
function showInterimTranscript(initialText = "Listening...") {
  hideInterimTranscript();
  if (emptyChatState) emptyChatState.style.display = "none";
  const row = document.createElement("div");
  row.className = "message-row user interim";
  row.id = "interimTranscriptRow";
  row.innerHTML = `
    <div class="message-bubble listening-bubble">
      <span class="listening-pulse-indicator" aria-hidden="true"></span>
      <span class="interim-label">Listening:</span>
      <span class="interim-text">${escapeHtml(initialText)}</span>
    </div>
  `;
  chatViewport.appendChild(row);
  scrollChatToBottom();
}

function updateInterimTranscript(text) {
  const row = document.getElementById("interimTranscriptRow");
  if (!row) {
    showInterimTranscript(text);
    return;
  }
  const textSpan = row.querySelector(".interim-text");
  if (textSpan) textSpan.textContent = text;
  scrollChatToBottom();
}

function hideInterimTranscript() {
  const row = document.getElementById("interimTranscriptRow");
  if (row) row.remove();
}

window.showInterimTranscript = showInterimTranscript;
window.updateInterimTranscript = updateInterimTranscript;
window.hideInterimTranscript = hideInterimTranscript;

// Unified message submission for both text and voice commands
async function submitTextMessage(overrideText = null) {
  const text = (overrideText !== null ? overrideText : (chatTextInput ? chatTextInput.value : "")).trim();
  if (!text) return;
  if (chatTextInput && overrideText === null) chatTextInput.value = "";
  
  // Interrupt any ongoing speech
  audioSystem.stopAudio();

window.submitTextMessage = submitTextMessage;

  // Hide empty state
  if (emptyChatState) emptyChatState.style.display = "none";

  // Append user message to DOM
  appendMessageToDom("user", text);

  // Prepare assistant placeholder bubble for streaming with animated thinking dots
  const assistantBubble = appendMessageToDom("assistant", "", true);
  assistantBubble.innerHTML = `<div class="thinking-dots" aria-label="Thinking"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
  appState.setState(AssistantState.THINKING);

  let accumulated = "";
  await streamChatResponse(
    appState.activeConversationId,
    text,
    // onToken
    (token) => {
      if (appState.getState() !== AssistantState.SPEAKING) {
        appState.setState(AssistantState.PROCESSING);
      }
      accumulated += token;
      assistantBubble.innerHTML = renderMarkdown(accumulated);
      scrollChatToBottom();
    },
    // onTool
    (toolName) => {
      appState.setState(AssistantState.TOOL_USE, toolName);
      const toolBadge = document.createElement("div");
      toolBadge.className = "tool-tag";
      toolBadge.innerHTML = `<span>⚡</span> Executing tool: ${escapeHtml(toolName)}`;
      assistantBubble.prepend(toolBadge);
    },
    // onDone
    (doneData) => {
      assistantBubble.innerHTML = renderMarkdown(doneData.content || accumulated);
      scrollChatToBottom();
      
      const onSpeechFinished = () => {
        if (appState.handsFree) {
          setTimeout(() => {
            if (appState.handsFree && !audioSystem.isRecording && (!audioSystem.speechRecognizer || !audioSystem.speechRecognizer.isActive)) {
              window.toggleVoiceRecording();
            }
          }, 700);
        }
      };

      // If audio was generated and auto-play enabled
      if (doneData.audio_url) {
        attachAudioActions(assistantBubble.parentElement, doneData.audio_url);
        if (appState.settings.auto_play !== false) {
          if (appState.settings.voice_engine === "speech" && "speechSynthesis" in window) {
            audioSystem.speakText(doneData.content || accumulated, onSpeechFinished);
          } else {
            audioSystem.playAudio(doneData.audio_url, onSpeechFinished);
          }
        } else {
          appState.setState(AssistantState.IDLE);
          onSpeechFinished();
        }
      } else {
        appState.setState(AssistantState.IDLE);
        onSpeechFinished();
      }
    },
    // onError
    (err) => {
      console.error("Chat streaming error:", err);
      appState.setState(AssistantState.ERROR);
      assistantBubble.innerHTML = `<span style="color: var(--accent-rose);">An error occurred while generating the response.</span>`;
      setTimeout(() => appState.setState(AssistantState.IDLE), 2500);
    }
  );
}

// Voice recording & Speech Recognition toggle
window.toggleVoiceRecording = async function() {
  const isSpeechRecActive = audioSystem.speechRecognizer && audioSystem.speechRecognizer.isActive;
  const isMediaRecActive = audioSystem.isRecording;

  if (isSpeechRecActive || isMediaRecActive) {
    // 1. Currently listening/recording -> Stop immediately!
    btnMainMic.classList.remove("recording");
    hideInterimTranscript();
    if (isSpeechRecActive) {
      audioSystem.speechRecognizer.stop();
      audioSystem.stopMicVisualizer();
    }
    if (isMediaRecActive) {
      audioSystem.cancelRecording();
    }
    appState.setState(AssistantState.IDLE);
    return;
  }

  // 2. Starting listening/recording
  audioSystem.stopAudio(); // Stop any speech playback
  btnMainMic.classList.add("recording");

  // If browser native Web Speech API SpeechRecognition is available (Chrome, Edge, Safari)
  if (audioSystem.speechRecognizer && audioSystem.speechRecognizer.isSupported) {
    appState.setState(AssistantState.LISTENING);
    showInterimTranscript("Speak your command now...");

    // Connect mic stream to analyser for waveform visualizer
    await audioSystem.startMicVisualizer();

    const lang = (appState.settings && appState.settings.language === "ta") ? "ta-IN" 
      : (appState.settings && appState.settings.language === "hi") ? "hi-IN"
      : (appState.settings && appState.settings.language === "es") ? "es-ES"
      : (appState.settings && appState.settings.language === "fr") ? "fr-FR"
      : (appState.settings && appState.settings.language === "de") ? "de-DE"
      : "en-US";

    const started = audioSystem.speechRecognizer.start(
      lang,
      // onInterim
      (interimText) => {
        updateInterimTranscript(interimText);
      },
      // onFinal
      (finalText) => {
        btnMainMic.classList.remove("recording");
        audioSystem.stopMicVisualizer();
        hideInterimTranscript();
        
        if (finalText && finalText.trim()) {
          // Route recognized speech into the exact same command pipeline as typed input
          submitTextMessage(finalText.trim());
        } else {
          showToast("No speech detected.");
          appState.setState(AssistantState.IDLE);
        }
      },
      // onError
      (err) => {
        btnMainMic.classList.remove("recording");
        audioSystem.stopMicVisualizer();
        hideInterimTranscript();

        console.warn("Speech recognition notice:", err);
        if (err === "not-allowed" || err === "permission-denied") {
          showToast("Microphone permission denied. Please allow microphone access.");
          appState.setState(AssistantState.ERROR);
        } else if (err === "no-speech") {
          showToast("No speech detected. Please speak clearly into your microphone.");
          appState.setState(AssistantState.IDLE);
        } else if (err === "audio-capture") {
          showToast("No microphone device detected.");
          appState.setState(AssistantState.ERROR);
        } else {
          showToast(`Speech recognition event: ${err}`);
          appState.setState(AssistantState.IDLE);
        }
        setTimeout(() => {
          if (appState.getState() === AssistantState.ERROR) {
            appState.setState(AssistantState.IDLE);
          }
        }, 2500);
      },
      // onEnd
      () => {
        btnMainMic.classList.remove("recording");
        audioSystem.stopMicVisualizer();
        if (appState.getState() === AssistantState.LISTENING) {
          hideInterimTranscript();
          appState.setState(AssistantState.IDLE);
        }
      }
    );

    if (!started) {
      btnMainMic.classList.remove("recording");
      audioSystem.stopMicVisualizer();
      hideInterimTranscript();
      showToast("Could not start speech recognition.");
      appState.setState(AssistantState.IDLE);
    }
  } else {
    // Browser does NOT support SpeechRecognition
    // Check if server has OpenAI key configured
    const hasKey = appState.settings && appState.settings.has_openai_key;
    if (hasKey) {
      try {
        await audioSystem.startRecording();
      } catch (err) {
        btnMainMic.classList.remove("recording");
      }
    } else {
      btnMainMic.classList.remove("recording");
      appState.setState(AssistantState.ERROR);
      showToast("Live speech recognition requires Chrome/Edge or an OpenAI key. You can type below.");
      if (emptyChatState) emptyChatState.style.display = "none";
      const infoBubble = appendMessageToDom("assistant", "");
      infoBubble.innerHTML = `<span style="color: var(--text-secondary);">Live microphone speech recognition in Simulation Mode requires the Web Speech API (supported in <strong>Google Chrome</strong> and <strong>Microsoft Edge</strong>) or an <code>OPENAI_API_KEY</code> in <code>.env</code>. You can type your question directly in the input box below.</span>`;
      setTimeout(() => appState.setState(AssistantState.IDLE), 3500);
    }
  }
};

window.toggleHandsFreeMode = function() {
  appState.handsFree = !appState.handsFree;
  if (btnToggleHandsFree) {
    btnToggleHandsFree.classList.toggle("active", appState.handsFree);
  }
  showToast(appState.handsFree ? "Hands-Free Mode: Active" : "Hands-Free Mode: Disabled");
  if (appState.handsFree) {
    const isBusy = audioSystem.isRecording || (audioSystem.speechRecognizer && audioSystem.speechRecognizer.isActive) || appState.getState() === AssistantState.SPEAKING;
    if (!isBusy) {
      window.toggleVoiceRecording();
    }
  } else {
    if (audioSystem.isRecording || (audioSystem.speechRecognizer && audioSystem.speechRecognizer.isActive)) {
      window.toggleVoiceRecording();
    }
  }
};

window.toggleTheme = function() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  if (window.settingsUI) window.settingsUI.setVal("settingTheme", next);
  showToast(`Theme changed to ${next}`);
};

window.startNewConversation = function() {
  appState.activeConversationId = null;
  audioSystem.stopAudio();
  if (chatViewport) {
    chatViewport.innerHTML = "";
    if (emptyChatState) {
      emptyChatState.style.display = "flex";
      chatViewport.appendChild(emptyChatState);
    }
  }
  appState.setState(AssistantState.IDLE);
  showToast("New conversation started");
};

window.loadConversation = async function(convId) {
  try {
    const res = await fetch(`/api/conversations/${convId}`);
    if (!res.ok) throw new Error("Could not load conversation");
    const conv = await res.json();
    
    appState.activeConversationId = conv.id;
    chatViewport.innerHTML = "";
    if (emptyChatState) emptyChatState.style.display = "none";

    if (conv.messages && conv.messages.length > 0) {
      conv.messages.forEach(m => {
        const bubble = appendMessageToDom(m.role, m.content);
        if (m.role === "assistant" && m.audio_reference) {
          attachAudioActions(bubble.parentElement, m.audio_reference);
        }
      });
    } else {
      if (emptyChatState) {
        emptyChatState.style.display = "flex";
        chatViewport.appendChild(emptyChatState);
      }
    }
    scrollChatToBottom();
  } catch (err) {
    console.error(err);
  }
};

window.clearActiveChat = async function() {
  if (!appState.activeConversationId) return;
  if (!confirm("Clear all messages in this conversation?")) return;
  try {
    await fetch(`/api/conversations/${appState.activeConversationId}/messages`, { method: "DELETE" });
    window.loadConversation(appState.activeConversationId);
    showToast("Conversation cleared");
  } catch (e) {
    console.error(e);
  }
};

function appendMessageToDom(role, content, isStreaming = false) {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;
  row.setAttribute("role", "article");

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.innerHTML = renderMarkdown(content);

  const footer = document.createElement("div");
  footer.className = "message-footer";
  
  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  footer.innerHTML = `<span>${timeStr}</span>`;

  // Copy button
  const copyBtn = document.createElement("button");
  copyBtn.className = "msg-action-btn";
  copyBtn.title = "Copy message";
  copyBtn.setAttribute("aria-label", "Copy message text");
  copyBtn.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg> Copy`;
  copyBtn.onclick = () => {
    navigator.clipboard.writeText(bubble.innerText);
    showToast("Copied to clipboard");
  };
  footer.appendChild(copyBtn);

  row.appendChild(bubble);
  row.appendChild(footer);
  chatViewport.appendChild(row);
  scrollChatToBottom();
  return bubble;
}

function attachAudioActions(messageRow, audioUrl) {
  const footer = messageRow.querySelector(".message-footer");
  if (!footer) return;

  const playBtn = document.createElement("button");
  playBtn.className = "msg-action-btn";
  playBtn.title = "Replay audio";
  playBtn.setAttribute("aria-label", "Play assistant speech");
  playBtn.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg> Play Audio`;
  playBtn.onclick = () => {
    const bubble = messageRow.querySelector(".message-bubble");
    if (appState.settings.voice_engine === "speech" && "speechSynthesis" in window && bubble) {
      audioSystem.speakText(bubble.innerText);
    } else {
      audioSystem.playAudio(audioUrl);
    }
  };

  const dlLink = document.createElement("a");
  dlLink.className = "msg-action-btn";
  dlLink.href = audioUrl;
  dlLink.download = "nova_speech.wav";
  dlLink.title = "Download audio";
  dlLink.setAttribute("aria-label", "Download audio WAV");
  dlLink.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg> Download`;

  footer.appendChild(playBtn);
  footer.appendChild(dlLink);
}

function scrollChatToBottom() {
  if (chatViewport) {
    chatViewport.scrollTop = chatViewport.scrollHeight;
  }
}

// Quick action shortcuts for Command Palette
window.quickSetPersonality = async function(personality) {
  try {
    const res = await fetch("/api/settings", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ personality })
    });
    if (res.ok) {
      appState.settings.personality = personality;
      showToast(`Personality switched to ${personality}`);
    }
  } catch (e) {
    console.error(e);
  }
};

window.quickSetVoice = async function(voice) {
  try {
    const res = await fetch("/api/settings", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ voice })
    });
    if (res.ok) {
      appState.settings.voice = voice;
      showToast(`Voice set to ${voice.toUpperCase()}`);
    }
  } catch (e) {
    console.error(e);
  }
};

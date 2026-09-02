// Command Palette & Keyboard Shortcuts

class CommandPalette {
  constructor() {
    this.modal = document.getElementById("commandPaletteModal");
    this.input = document.getElementById("commandPaletteInput");
    this.list = document.getElementById("commandPaletteList");
    this.selectedIndex = 0;

    this.commands = [
      { id: "new_chat", label: "New Conversation", shortcut: "Ctrl+N", action: () => window.startNewConversation() },
      { id: "voice_toggle", label: "Toggle Voice Recording", shortcut: "Space", action: () => window.toggleVoiceRecording() },
      { id: "hands_free", label: "Toggle Hands-Free Mode", shortcut: "", action: () => window.toggleHandsFreeMode() },
      { id: "stop_speech", label: "Stop Assistant Speaking", shortcut: "Esc", action: () => audioSystem.stopAudio() },
      { id: "focus_chat", label: "Focus Chat Input", shortcut: "Ctrl+/", action: () => { const i = document.getElementById("chatTextInput"); if (i) i.focus(); } },
      { id: "history", label: "Open Conversation History", shortcut: "Ctrl+H", action: () => window.sidebarManager.open() },
      { id: "knowledge", label: "Open Knowledge Base & Documents", shortcut: "", action: () => window.knowledgeUI.open() },
      { id: "memory", label: "Open Memory Vault", shortcut: "", action: () => { window.settingsUI.open(); const b = document.querySelector(".settings-tab-btn[data-tab='memory']"); if (b) b.click(); } },
      { id: "settings", label: "Open Settings", shortcut: "Ctrl+,", action: () => window.settingsUI.open() },
      { id: "theme", label: "Toggle Theme (Dark/Light)", shortcut: "", action: () => window.toggleTheme() },
      { id: "clear_chat", label: "Clear Active Conversation", shortcut: "", action: () => window.clearActiveChat() },
      { id: "pers_futuristic", label: "Change Personality: Futuristic AI", shortcut: "", action: () => window.quickSetPersonality("Futuristic") },
      { id: "pers_concise", label: "Change Personality: Concise & Direct", shortcut: "", action: () => window.quickSetPersonality("Concise") },
      { id: "pers_empathetic", label: "Change Personality: Empathetic & Warm", shortcut: "", action: () => window.quickSetPersonality("Empathetic") },
      { id: "pers_pro", label: "Change Personality: Professional Executive", shortcut: "", action: () => window.quickSetPersonality("Professional") },
      { id: "voice_alloy", label: "Change Voice: Alloy", shortcut: "", action: () => window.quickSetVoice("alloy") },
      { id: "voice_echo", label: "Change Voice: Echo", shortcut: "", action: () => window.quickSetVoice("echo") },
      { id: "voice_nova", label: "Change Voice: Nova", shortcut: "", action: () => window.quickSetVoice("nova") },
      { id: "voice_shimmer", label: "Change Voice: Shimmer", shortcut: "", action: () => window.quickSetVoice("shimmer") }
    ];

    this.initEvents();
  }

  initEvents() {
    window.addEventListener("keydown", (e) => {
      // Ctrl+K or Cmd+K: Command Palette
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        this.toggle();
      }
      // Ctrl+N: New Chat
      else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "n") {
        e.preventDefault();
        window.startNewConversation();
      }
      // Ctrl+/: Focus Chat Input
      else if ((e.ctrlKey || e.metaKey) && e.key === "/") {
        e.preventDefault();
        const input = document.getElementById("chatTextInput");
        if (input) input.focus();
      }
      // Esc: Stop audio / cancel recording / close modals
      else if (e.key === "Escape") {
        this.close();
        if (window.sidebarManager) window.sidebarManager.close();
        if (window.knowledgeUI) window.knowledgeUI.close();
        if (window.settingsUI) window.settingsUI.close();
        audioSystem.stopAudio();
        if (audioSystem.isRecording) audioSystem.cancelRecording();
      }
    });

    if (this.input) {
      this.input.addEventListener("input", () => {
        this.filterList(this.input.value);
      });

      this.input.addEventListener("keydown", (e) => {
        const items = this.list.querySelectorAll(".cmd-item");
        if (e.key === "ArrowDown") {
          e.preventDefault();
          this.selectedIndex = Math.min(items.length - 1, this.selectedIndex + 1);
          this.updateSelection(items);
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          this.selectedIndex = Math.max(0, this.selectedIndex - 1);
          this.updateSelection(items);
        } else if (e.key === "Enter") {
          e.preventDefault();
          if (items[this.selectedIndex]) {
            items[this.selectedIndex].click();
          }
        }
      });
    }

    if (this.modal) {
      this.modal.addEventListener("click", (e) => {
        if (e.target === this.modal) this.close();
      });
    }
  }

  toggle() {
    if (this.modal.classList.contains("open")) {
      this.close();
    } else {
      this.open();
    }
  }

  open() {
    this.modal.classList.add("open");
    this.input.value = "";
    this.selectedIndex = 0;
    this.filterList("");
    setTimeout(() => this.input.focus(), 50);
  }

  close() {
    this.modal.classList.remove("open");
  }

  filterList(query) {
    const q = (query || "").toLowerCase();
    const matched = this.commands.filter(c => c.label.toLowerCase().includes(q));
    this.renderList(matched);
  }

  renderList(cmds) {
    if (!this.list) return;
    this.list.innerHTML = "";
    this.selectedIndex = 0;

    if (cmds.length === 0) {
      this.list.innerHTML = `<div style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 0.85rem;">No matching commands found.</div>`;
      return;
    }

    cmds.forEach((c, idx) => {
      const item = document.createElement("div");
      item.className = `cmd-item ${idx === 0 ? "selected" : ""}`;
      item.innerHTML = `
        <span>${escapeHtml(c.label)}</span>
        ${c.shortcut ? `<span class="kbd">${c.shortcut}</span>` : ""}
      `;
      item.onclick = () => {
        this.close();
        c.action();
      };
      this.list.appendChild(item);
    });
  }

  updateSelection(items) {
    items.forEach((item, idx) => {
      item.classList.toggle("selected", idx === this.selectedIndex);
      if (idx === this.selectedIndex) {
        item.scrollIntoView({ block: "nearest" });
      }
    });
  }
}

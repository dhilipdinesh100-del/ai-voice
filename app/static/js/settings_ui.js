// Settings UI Management

class SettingsUI {
  constructor() {
    this.modal = document.getElementById("settingsModal");
    this.tabBtns = document.querySelectorAll(".settings-tab-btn");
    this.tabPanes = document.querySelectorAll(".settings-pane");
    this.memoryList = document.getElementById("settingsMemoryList");
    
    this.initEvents();
  }

  initEvents() {
    const openBtn = document.getElementById("btnOpenSettings");
    const closeBtn = document.getElementById("btnCloseSettings");
    const saveBtn = document.getElementById("btnSaveSettings");
    const clearMemsBtn = document.getElementById("btnClearAllMemories");

    if (openBtn) openBtn.addEventListener("click", () => this.open());
    if (closeBtn) closeBtn.addEventListener("click", () => this.close());
    if (this.modal) {
      this.modal.addEventListener("click", (e) => {
        if (e.target === this.modal) this.close();
      });
    }

    this.tabBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const targetTab = btn.dataset.tab;
        this.tabBtns.forEach(b => b.classList.toggle("active", b === btn));
        this.tabPanes.forEach(p => p.style.display = p.id === `tab-${targetTab}` ? "block" : "none");
        if (targetTab === "memory") {
          this.loadMemories();
        }
      });
    });

    if (saveBtn) saveBtn.addEventListener("click", () => this.saveSettings());
    if (clearMemsBtn) clearMemsBtn.addEventListener("click", () => this.clearAllMemories());
  }

  open() {
    this.modal.classList.add("open");
    this.loadSettings();
  }

  close() {
    this.modal.classList.remove("open");
  }

  async loadSettings() {
    try {
      const res = await fetch("/api/settings");
      if (!res.ok) throw new Error("Could not fetch settings");
      const s = await res.json();
      appState.settings = s;

      // Populate form controls
      this.setVal("settingTheme", s.theme || "dark");
      this.setVal("settingPersonality", s.personality || "Futuristic");
      this.setVal("settingCustomPrompt", s.custom_prompt || "");
      this.setVal("settingVoice", s.voice || "alloy");
      const localEngine = localStorage.getItem("nova_voice_engine") || "speech";
      this.setVal("settingVoiceEngine", localEngine);
      appState.settings.voice_engine = localEngine;
      this.setVal("settingVoiceSpeed", s.voice_speed || 1.0);
      document.getElementById("speedValueDisplay").textContent = `${s.voice_speed || 1.0}x`;
      this.setVal("settingLanguage", s.language || "en");
      this.setChecked("settingAutoPlay", s.auto_play !== false);
      this.setChecked("settingMemoryEnabled", s.memory_enabled !== false);
      this.setChecked("settingHandsFree", s.hands_free === true);

      // Apply theme
      document.documentElement.setAttribute("data-theme", s.theme || "dark");
    } catch (err) {
      console.error(err);
    }
  }

  async saveSettings() {
    const chosenEngine = this.getVal("settingVoiceEngine") || "speech";
    localStorage.setItem("nova_voice_engine", chosenEngine);
    appState.settings.voice_engine = chosenEngine;

    const payload = {
      theme: this.getVal("settingTheme"),
      personality: this.getVal("settingPersonality"),
      custom_prompt: this.getVal("settingCustomPrompt"),
      voice: this.getVal("settingVoice"),
      voice_speed: parseFloat(this.getVal("settingVoiceSpeed")),
      language: this.getVal("settingLanguage"),
      auto_play: this.isChecked("settingAutoPlay"),
      memory_enabled: this.isChecked("settingMemoryEnabled"),
      hands_free: this.isChecked("settingHandsFree")
    };

    try {
      const res = await fetch("/api/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const saved = await res.json();
        saved.voice_engine = chosenEngine;
        appState.settings = saved;
        document.documentElement.setAttribute("data-theme", payload.theme);
        appState.handsFree = payload.hands_free;
        const hfBtn = document.getElementById("btnToggleHandsFree");
        if (hfBtn) hfBtn.classList.toggle("active", payload.hands_free);
        showToast("Settings updated");
        this.close();
      }
    } catch (err) {
      console.error(err);
      showToast("Error saving settings");
    }
  }

  async loadMemories() {
    if (!this.memoryList) return;
    this.memoryList.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem;">Loading memories...</div>`;
    try {
      const res = await fetch("/api/memories");
      const mems = await res.json();
      this.memoryList.innerHTML = "";
      if (mems.length === 0) {
        this.memoryList.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 12px; text-align: center;">No stored memories yet. NOVA learns your preferences automatically.</div>`;
        return;
      }
      mems.forEach(m => {
        const item = document.createElement("div");
        item.className = "sidebar-item";
        item.style.cssText = "margin-bottom: 6px; border: 1px solid var(--border-glass);";
        item.innerHTML = `
          <span style="font-size: 0.85rem; color: var(--text-primary); flex: 1;">${escapeHtml(m.content)}</span>
          <button class="btn-icon" style="width: 26px; height: 26px; color: var(--accent-rose);" title="Delete memory">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
          </button>
        `;
        item.querySelector("button").onclick = () => this.deleteMemory(m.id);
        this.memoryList.appendChild(item);
      });
    } catch (err) {
      console.error(err);
    }
  }

  async deleteMemory(memId) {
    try {
      const res = await fetch(`/api/memories/${memId}`, { method: "DELETE" });
      if (res.ok) {
        showToast("Memory deleted");
        this.loadMemories();
      }
    } catch (e) {
      console.error(e);
    }
  }

  async clearAllMemories() {
    if (!confirm("Clear all stored user memories?")) return;
    try {
      const res = await fetch("/api/memories", { method: "DELETE" });
      if (res.ok) {
        showToast("All memories cleared");
        this.loadMemories();
      }
    } catch (e) {
      console.error(e);
    }
  }

  getVal(id) {
    const el = document.getElementById(id);
    return el ? el.value : "";
  }

  setVal(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val;
  }

  isChecked(id) {
    const el = document.getElementById(id);
    return el ? el.checked : false;
  }

  setChecked(id, val) {
    const el = document.getElementById(id);
    if (el) el.checked = !!val;
  }
}

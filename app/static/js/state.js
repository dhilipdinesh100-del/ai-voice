// Central Assistant State Machine & Event Store
const AssistantState = {
  IDLE: "idle",
  LISTENING: "listening",
  PROCESSING: "processing",
  THINKING: "thinking",
  TOOL_USE: "tool_use",
  SPEAKING: "speaking",
  PAUSED: "paused",
  ERROR: "error"
};

class StateStore {
  constructor() {
    this.currentState = AssistantState.IDLE;
    this.currentTool = null;
    this.activeConversationId = null;
    this.handsFree = false;
    this.settings = {
      theme: "dark",
      personality: "Futuristic",
      voice: "alloy",
      voice_speed: 1.0,
      auto_play: true,
      language: "en",
      memory_enabled: true
    };
    this.listeners = {};
  }

  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }

  setState(newState, meta = null) {
    if (this.currentState === newState && meta === this.currentTool) return;
    const oldState = this.currentState;
    this.currentState = newState;
    this.currentTool = meta;
    
    // Update body class for visual styling
    document.body.classList.remove(
      "state-idle", "state-listening", "state-processing", 
      "state-thinking", "state-tool_use", "state-speaking", 
      "state-paused", "state-error"
    );
    document.body.classList.add(`state-${newState}`);
    
    // Update visual badge
    const badgeText = document.getElementById("stateBadgeText");
    if (badgeText) {
      if (newState === AssistantState.TOOL_USE && meta) {
        badgeText.textContent = `Tool: ${meta}`;
      } else {
        badgeText.textContent = newState.replace("_", " ");
      }
    }
    
    this.emit("stateChange", { oldState, newState, meta });
  }

  getState() {
    return this.currentState;
  }
}

const appState = new StateStore();

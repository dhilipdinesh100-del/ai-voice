// Sidebar Conversations Management

class SidebarManager {
  constructor() {
    this.drawer = document.getElementById("sidebarDrawer");
    this.overlay = document.getElementById("sidebarOverlay");
    this.listContainer = document.getElementById("sidebarList");
    this.searchInput = document.getElementById("sidebarSearchInput");
    this.conversations = [];
    
    this.initEvents();
  }

  initEvents() {
    const toggleBtn = document.getElementById("btnToggleSidebar");
    const closeBtn = document.getElementById("btnCloseSidebar");
    const newChatBtn = document.getElementById("btnNewChatSidebar");

    if (toggleBtn) toggleBtn.addEventListener("click", () => this.open());
    if (closeBtn) closeBtn.addEventListener("click", () => this.close());
    if (this.overlay) this.overlay.addEventListener("click", () => this.close());
    if (newChatBtn) {
      newChatBtn.addEventListener("click", () => {
        this.close();
        window.startNewConversation();
      });
    }

    if (this.searchInput) {
      this.searchInput.addEventListener("input", (e) => {
        this.filterList(e.target.value);
      });
    }
  }

  open() {
    this.drawer.classList.add("open");
    this.overlay.classList.add("open");
    this.loadConversations();
  }

  close() {
    this.drawer.classList.remove("open");
    this.overlay.classList.remove("open");
  }

  async loadConversations() {
    try {
      const res = await fetch("/api/conversations");
      if (!res.ok) throw new Error("Failed to load conversations");
      this.conversations = await res.json();
      this.renderList(this.conversations);
    } catch (err) {
      console.error("Error loading conversations:", err);
    }
  }

  renderList(convs) {
    if (!this.listContainer) return;
    this.listContainer.innerHTML = "";

    if (convs.length === 0) {
      this.listContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.85rem;">No conversations yet.</div>`;
      return;
    }

    convs.forEach(c => {
      const item = document.createElement("div");
      item.className = `sidebar-item ${c.id === appState.activeConversationId ? "active" : ""}`;
      
      const titleSpan = document.createElement("span");
      titleSpan.style.cssText = "flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;";
      titleSpan.textContent = c.title || "Untitled";
      titleSpan.onclick = () => {
        window.loadConversation(c.id);
        this.close();
      };

      const actions = document.createElement("div");
      actions.className = "sidebar-item-actions";

      // Export button
      const exportBtn = document.createElement("button");
      exportBtn.className = "btn-icon";
      exportBtn.style.cssText = "width: 26px; height: 26px; padding: 0;";
      exportBtn.title = "Export JSON";
      exportBtn.innerHTML = `<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>`;
      exportBtn.onclick = (e) => {
        e.stopPropagation();
        this.exportConversation(c.id, c.title);
      };

      // Rename button
      const renameBtn = document.createElement("button");
      renameBtn.className = "btn-icon";
      renameBtn.style.cssText = "width: 26px; height: 26px; padding: 0;";
      renameBtn.title = "Rename";
      renameBtn.innerHTML = `<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>`;
      renameBtn.onclick = (e) => {
        e.stopPropagation();
        const newTitle = prompt("Enter new title:", c.title);
        if (newTitle && newTitle.trim()) {
          this.renameConversation(c.id, newTitle.trim());
        }
      };

      // Delete button
      const delBtn = document.createElement("button");
      delBtn.className = "btn-icon";
      delBtn.style.cssText = "width: 26px; height: 26px; padding: 0;";
      delBtn.title = "Delete";
      delBtn.innerHTML = `<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`;
      delBtn.onclick = (e) => {
        e.stopPropagation();
        if (confirm(`Delete conversation "${c.title}"?`)) {
          this.deleteConversation(c.id);
        }
      };

      actions.appendChild(exportBtn);
      actions.appendChild(renameBtn);
      actions.appendChild(delBtn);

      item.appendChild(titleSpan);
      item.appendChild(actions);
      this.listContainer.appendChild(item);
    });
  }

  filterList(query) {
    const q = (query || "").toLowerCase();
    const filtered = this.conversations.filter(c => (c.title || "").toLowerCase().includes(q));
    this.renderList(filtered);
  }

  async renameConversation(convId, newTitle) {
    try {
      const res = await fetch(`/api/conversations/${convId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle })
      });
      if (res.ok) {
        this.loadConversations();
        showToast("Conversation renamed");
      }
    } catch (e) {
      console.error(e);
    }
  }

  async deleteConversation(convId) {
    try {
      const res = await fetch(`/api/conversations/${convId}`, { method: "DELETE" });
      if (res.ok) {
        if (appState.activeConversationId === convId) {
          window.startNewConversation();
        }
        this.loadConversations();
        showToast("Conversation deleted");
      }
    } catch (e) {
      console.error(e);
    }
  }

  async exportConversation(convId, title) {
    try {
      const res = await fetch(`/api/conversations/${convId}/export`);
      if (!res.ok) throw new Error("Export failed");
      const data = await res.json();
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `nova_chat_${(title || "export").replace(/[^a-zA-Z0-9_-]/g, "_")}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("Chat exported to JSON");
    } catch (e) {
      console.error(e);
      showToast("Export failed");
    }
  }
}

// Knowledge Base Modal UI

class KnowledgeUI {
  constructor() {
    this.modal = document.getElementById("knowledgeModal");
    this.dropzone = document.getElementById("knowledgeDropzone");
    this.fileInput = document.getElementById("knowledgeFileInput");
    this.docList = document.getElementById("knowledgeDocList");
    this.queryInput = document.getElementById("knowledgeQueryInput");
    this.queryBtn = document.getElementById("btnKnowledgeQuery");
    this.queryResults = document.getElementById("knowledgeQueryResults");

    this.initEvents();
  }

  initEvents() {
    const openBtn = document.getElementById("btnOpenKnowledge");
    const closeBtn = document.getElementById("btnCloseKnowledge");

    if (openBtn) openBtn.addEventListener("click", () => this.open());
    if (closeBtn) closeBtn.addEventListener("click", () => this.close());
    if (this.modal) {
      this.modal.addEventListener("click", (e) => {
        if (e.target === this.modal) this.close();
      });
    }

    if (this.dropzone) {
      this.dropzone.addEventListener("click", () => this.fileInput.click());
      this.dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        this.dropzone.classList.add("dragover");
      });
      this.dropzone.addEventListener("dragleave", () => {
        this.dropzone.classList.remove("dragover");
      });
      this.dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        this.dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
          this.uploadFile(e.dataTransfer.files[0]);
        }
      });
    }

    if (this.fileInput) {
      this.fileInput.addEventListener("change", (e) => {
        if (e.target.files.length) {
          this.uploadFile(e.target.files[0]);
        }
      });
    }

    if (this.queryBtn && this.queryInput) {
      this.queryBtn.addEventListener("click", () => this.runQuery());
      this.queryInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this.runQuery();
      });
    }
  }

  open() {
    this.modal.classList.add("open");
    this.loadDocuments();
  }

  close() {
    this.modal.classList.remove("open");
  }

  async loadDocuments() {
    try {
      const res = await fetch("/api/knowledge/documents");
      if (!res.ok) throw new Error("Could not load documents");
      const docs = await res.json();
      this.renderDocs(docs);
    } catch (err) {
      console.error(err);
    }
  }

  renderDocs(docs) {
    if (!this.docList) return;
    this.docList.innerHTML = "";

    if (docs.length === 0) {
      this.docList.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 16px; font-size: 0.85rem;">No documents uploaded yet. Upload PDF, TXT, or Markdown files above.</div>`;
      return;
    }

    docs.forEach(d => {
      const row = document.createElement("div");
      row.className = "sidebar-item";
      row.style.cssText = "margin-bottom: 6px; border: 1px solid var(--border-glass);";

      const sizeKb = (d.file_size / 1024).toFixed(1);
      row.innerHTML = `
        <div style="overflow: hidden; text-overflow: ellipsis;">
          <strong style="color: var(--text-primary); font-size: 0.9rem;">${escapeHtml(d.filename)}</strong>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">
            ${d.file_type.toUpperCase()} • ${sizeKb} KB • <span style="color: ${d.status === 'ready' ? 'var(--accent-emerald)' : 'var(--accent-amber)'}">${d.status}</span>
          </div>
        </div>
        <button class="btn-icon" style="width: 28px; height: 28px; color: var(--accent-rose);" title="Delete document">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
        </button>
      `;

      row.querySelector("button").onclick = () => this.deleteDocument(d.id, d.filename);
      this.docList.appendChild(row);
    });
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    showToast(`Uploading ${file.name}...`);
    try {
      const res = await fetch("/api/knowledge/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      
      showToast(`Document ready: ${file.name}`);
      this.loadDocuments();
      if (this.fileInput) this.fileInput.value = "";
    } catch (err) {
      console.error(err);
      showToast(`Upload failed: ${err.message}`);
    }
  }

  async deleteDocument(docId, name) {
    if (!confirm(`Delete "${name}" from Knowledge Base?`)) return;
    try {
      const res = await fetch(`/api/knowledge/documents/${docId}`, { method: "DELETE" });
      if (res.ok) {
        showToast("Document deleted");
        this.loadDocuments();
      }
    } catch (err) {
      console.error(err);
    }
  }

  async runQuery() {
    const q = this.queryInput.value.trim();
    if (!q) return;

    this.queryResults.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem;">Searching knowledge chunks...</div>`;
    try {
      const res = await fetch("/api/knowledge/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q })
      });
      const data = await res.json();
      if (!data.context) {
        this.queryResults.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem;">No matching content found in knowledge base.</div>`;
      } else {
        this.queryResults.innerHTML = `<div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; font-size: 0.85rem; color: var(--text-secondary); white-space: pre-wrap;">${escapeHtml(data.context)}</div>`;
      }
    } catch (err) {
      this.queryResults.innerHTML = `<div style="color: var(--accent-rose); font-size: 0.85rem;">Search error: ${err.message}</div>`;
    }
  }
}

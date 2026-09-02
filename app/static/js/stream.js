// Streaming Reader & Markdown Renderer

function escapeHtml(text) {
  if (!text) return "";
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function renderMarkdown(rawText) {
  if (!rawText) return "";
  let text = escapeHtml(rawText);

  // 1. Fenced Code blocks: ```lang ... ```
  text = text.replace(/```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang || "code";
    return `<div class="code-box"><div class="code-header"><span>${language}</span><button class="copy-code-btn" onclick="copyCode(this)" aria-label="Copy code block">Copy</button></div><pre><code>${code.trim()}</code></pre></div>`;
  });

  // 2. Inline code: `...`
  text = text.replace(/`([^`]+)`/g, "<code>$1</code>");

  // 3. Bold: **...**
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

  // 4. Italic: *...*
  text = text.replace(/\*([^*]+)\*/g, "<em>$1</em>");

  // 5. Bullet lists
  text = text.replace(/(?:^|\n)[ \t]*[-*][ \t]+([^\n]+)/g, "\n<li>$1</li>");
  text = text.replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>");

  // 6. Numbered lists
  text = text.replace(/(?:^|\n)[ \t]*\d+\.[ \t]+([^\n]+)/g, "\n<li>$1</li>");

  // 7. Line breaks to paragraphs
  const paragraphs = text.split(/\n\n+/).map(p => {
    const trimmed = p.trim();
    if (!trimmed) return "";
    if (trimmed.startsWith("<div") || trimmed.startsWith("<ul") || trimmed.startsWith("<ol")) {
      return trimmed;
    }
    return `<p>${trimmed.replace(/\n/g, "<br>")}</p>`;
  }).filter(Boolean).join("");

  return paragraphs;
}

window.copyCode = function(button) {
  const codeBox = button.closest(".code-box");
  if (!codeBox) return;
  const codeText = codeBox.querySelector("pre code").innerText;
  navigator.clipboard.writeText(codeText).then(() => {
    button.textContent = "Copied!";
    setTimeout(() => { button.textContent = "Copy"; }, 2000);
  }).catch(() => {
    button.textContent = "Failed";
  });
};

async function streamChatResponse(conversationId, promptText, onToken, onTool, onDone, onError) {
  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: promptText,
        conversation_id: conversationId,
        stream: true
      })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: "Streaming request failed." }));
      throw new Error(errData.detail || "Server error occurred");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // Keep incomplete chunk

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.event === "start") {
              if (data.conversation_id && !appState.activeConversationId) {
                appState.activeConversationId = data.conversation_id;
              }
            } else if (data.event === "tool") {
              if (onTool) onTool(data.name);
            } else if (data.event === "chunk") {
              if (onToken) onToken(data.token);
            } else if (data.event === "done") {
              if (onDone) onDone(data);
            }
          } catch (jsonErr) {
            console.warn("SSE parse error:", line, jsonErr);
          }
        }
      }
    }
  } catch (err) {
    if (onError) onError(err);
  }
}

import { useState, useRef, useEffect } from "react";

/**
 * Minimal markdown → React renderer. Handles:
 *   **bold**, *italic*, `code`, lines starting with "- " (bullets),
 *   lines starting with "_(..." (muted note), and newlines → <br>.
 * No external deps needed.
 */
function renderMarkdown(text) {
  if (!text) return null;
  const lines = text.split("\n");
  const elements = [];
  let keyIdx = 0;

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];

    // Bullet line
    if (/^\s*-\s+/.test(raw)) {
      elements.push(
        <li key={keyIdx++}>{inlineMarkdown(raw.replace(/^\s*-\s+/, ""))}</li>
      );
      continue;
    }

    // Muted note line (starts with _( or just _)
    if (/^\s*_/.test(raw)) {
      elements.push(
        <p key={keyIdx++} style={{ color: "#94a3b8", fontSize: "12px", fontStyle: "italic", margin: "4px 0 0" }}>
          {inlineMarkdown(raw.replace(/^_|_$/g, ""))}
        </p>
      );
      continue;
    }

    // Empty line → small spacer
    if (raw.trim() === "") {
      elements.push(<div key={keyIdx++} style={{ height: "6px" }} />);
      continue;
    }

    // Normal paragraph
    elements.push(<p key={keyIdx++} style={{ margin: "2px 0" }}>{inlineMarkdown(raw)}</p>);
  }

  // Wrap consecutive <li> elements in a <ul>
  const grouped = [];
  let ulBuf = [];
  let ulKey = 0;
  for (const el of elements) {
    if (el.type === "li") {
      ulBuf.push(el);
    } else {
      if (ulBuf.length) {
        grouped.push(<ul key={`ul-${ulKey++}`} style={{ margin: "4px 0", paddingLeft: "20px" }}>{ulBuf}</ul>);
        ulBuf = [];
      }
      grouped.push(el);
    }
  }
  if (ulBuf.length) {
    grouped.push(<ul key={`ul-${ulKey++}`} style={{ margin: "4px 0", paddingLeft: "20px" }}>{ulBuf}</ul>);
  }

  return <>{grouped}</>;
}

function inlineMarkdown(text) {
  // Split on **bold**, *italic*, `code` tokens
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (/^\*\*(.+)\*\*$/.test(part)) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (/^\*(.+)\*$/.test(part)) {
      return <em key={i}>{part.slice(1, -1)}</em>;
    }
    if (/^`(.+)`$/.test(part)) {
      return <code key={i} style={{ background: "#f1f5f9", padding: "1px 4px", borderRadius: "3px", fontSize: "12px" }}>{part.slice(1, -1)}</code>;
    }
    return part;
  });
}

const API_BASE = "";

const SUGGESTED_QUESTIONS = [
  "What happens if the Rotterdam strike lasts another 48 hours?",
  "Which shipments are at highest risk?",
  "Which fleet asset should we allocate to the vaccine shipment?",
];

function FactsBlock({ facts }) {
  const [open, setOpen] = useState(false);
  if (!facts || Object.keys(facts).length === 0) return null;
  return (
    <div className="assistant-facts">
      <button
        className="assistant-facts-toggle"
        onClick={() => setOpen((v) => !v)}
        type="button"
      >
        {open ? "▼" : "▶"} Structured backend data
      </button>
      {open && (
        <pre className="assistant-facts-json">
          {JSON.stringify(facts, null, 2)}
        </pre>
      )}
    </div>
  );
}

function Message({ msg }) {
  if (msg.role === "user") {
    return (
      <div className="assistant-msg assistant-msg--user">
        <span className="assistant-msg-label">You</span>
        <p>{msg.text}</p>
      </div>
    );
  }

  if (msg.role === "error") {
    return (
      <div className="assistant-msg assistant-msg--error">
        <span className="assistant-msg-label">Error</span>
        <p>{msg.text}</p>
      </div>
    );
  }

  return (
    <div className="assistant-msg assistant-msg--assistant">
      <span className="assistant-msg-label">
        Bob Assistant
        {msg.provider && msg.provider !== "FallbackProvider" && (
          <span className="assistant-provider-badge">{msg.provider}</span>
        )}
      </span>
      <div className="assistant-answer">{renderMarkdown(msg.text)}</div>
      <FactsBlock facts={msg.facts} />
    </div>
  );
}

export default function AssistantPanel() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function submit(question) {
    const q = question.trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setInput("");
    setLoading(true);

    // Build last-N history for multi-turn context (exclude the message we just added)
    const prevMessages = messages; // snapshot before the state update resolves
    const history = prevMessages
      .filter((m) => m.role === "user" || m.role === "assistant")
      .slice(-8)
      .map((m) => ({ role: m.role === "user" ? "user" : "assistant", content: m.text }));

    try {
      const res = await fetch(`${API_BASE}/assistant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, history }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || res.statusText);
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.answer, facts: data.facts, provider: data.provider },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "error", text: `Request failed: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit(input);
    }
  }

  return (
    <section className="panel assistant-panel">
      <div className="panel-header">
        <h2>Bob AI Assistant</h2>
        <span className="badge assistant-badge">POWERED BY WATSONX</span>
      </div>

      <p className="assistant-description">
        Ask questions about disruptions, shipment risk, and fleet allocation.
        All answers are grounded in live backend data — no invented values.
      </p>

      <div className="assistant-suggestions">
        {SUGGESTED_QUESTIONS.map((q) => (
          <button
            key={q}
            className="assistant-suggestion-btn"
            onClick={() => submit(q)}
            disabled={loading}
            type="button"
          >
            {q}
          </button>
        ))}
      </div>

      <div className="assistant-messages" aria-live="polite">
        {messages.length === 0 && (
          <p className="assistant-empty">
            Ask a question above or type your own below.
          </p>
        )}
        {messages.map((msg, i) => (
          // eslint-disable-next-line react/no-array-index-key
          <Message key={i} msg={msg} />
        ))}
        {loading && (
          <div className="assistant-msg assistant-msg--assistant">
            <span className="assistant-msg-label">Bob Assistant</span>
            <p className="assistant-thinking">Thinking…</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        className="assistant-form"
        onSubmit={(e) => { e.preventDefault(); submit(input); }}
      >
        <textarea
          className="assistant-input"
          placeholder="Ask about shipments, disruptions, or fleet recommendations…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          rows={2}
          disabled={loading}
        />
        <button
          type="submit"
          className="assistant-send-btn"
          disabled={loading || !input.trim()}
        >
          {loading ? "…" : "Ask"}
        </button>
      </form>
    </section>
  );
}

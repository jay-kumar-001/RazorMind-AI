import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { askCopilot } from "../api/api";
import { Send, Bot, User, Sparkles, Trash2 } from "lucide-react";

const PROMPT_SUGGESTIONS = [
  "What is the primary risk driver for this merchant?",
  "Project revenue expansion for the next quarter",
  "Explain the underwriting decision and rationale",
  "How can we reduce dispute velocity?",
  "Recommend 30-day retention optimizations",
];

export default function CopilotTab({ merchant }) {
  const mid = merchant?.merchant_id;
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: merchant
        ? `I am your **RazorMind Underwriting & Risk Advisor**. I have loaded real-time context for **${merchant.merchant_name || mid}** (${mid}).\n\n- **Health Index**: ${Number(merchant.merchant_health_score || 74).toFixed(1)} / 100\n- **Annual GMV**: ₹${Number(merchant.total_revenue || 0).toLocaleString("en-IN")}\n- **Auth Success Rate**: ${Number(merchant.success_rate || 92).toFixed(1)}%\n\nHow can I assist your portfolio review today?`
        : "Welcome to RazorMind Copilot. Select a merchant to initiate contextual underwriting advisory.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (merchant) {
      setMessages([
        {
          role: "assistant",
          content: `Context updated: **${merchant.merchant_name || mid}** (${mid}). Health score is **${Number(merchant.merchant_health_score || 74).toFixed(1)}/100** with **${merchant.risk_level || "LOW"}** risk rating. Ask me any underwriting, revenue, or dispute diagnostic question.`,
        },
      ]);
    }
  }, [mid]);

  const sendMessage = async (text) => {
    const q = (text || input).trim();
    if (!q) return;

    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setInput("");
    setLoading(true);

    try {
      const res = await askCopilot(mid || "M0001", q);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data?.answer || "No response generated." },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Underwriting advisor service timed out. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="copilot-container">
      {/* ── COPILOT HEADER ────────────────────────────────────────── */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "14px 20px", borderBottom: "1px solid var(--border)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 28, height: 28, borderRadius: "var(--radius-sm)",
            background: "var(--accent-subtle)", border: "1px solid rgba(99, 102, 241, 0.2)",
            display: "flex", alignItems: "center", justifyContent: "center", color: "var(--accent-text)"
          }}>
            <Sparkles size={14} />
          </div>
          <div>
            <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              RazorMind Advisory Copilot
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-tertiary)" }}>
              Context: <strong style={{ color: "var(--text-secondary)" }}>{merchant?.merchant_name || mid}</strong> ({mid})
            </div>
          </div>
        </div>

        <button
          className="btn btn-sm"
          onClick={() => setMessages([{ role: "assistant", content: "Conversation cleared. How can I help?" }])}
        >
          <Trash2 size={11} /> Clear Thread
        </button>
      </div>

      {/* ── MESSAGE LOG ───────────────────────────────────────────── */}
      <div className="copilot-chat-area">
        {messages.map((msg, i) => (
          <div key={i} className={`copilot-msg-row ${msg.role}`}>
            <div className="copilot-avatar">
              {msg.role === "user" ? <User size={13} color="var(--text-secondary)" /> : <Bot size={13} color="var(--accent-text)" />}
            </div>
            <div className="copilot-bubble">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p style={{ marginBottom: "6px" }}>{children}</p>,
                  strong: ({ children }) => <strong style={{ color: msg.role === "user" ? "#fff" : "var(--text-primary)" }}>{children}</strong>,
                  li: ({ children }) => <li style={{ marginLeft: "16px", marginBottom: "3px" }}>{children}</li>,
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {loading && (
          <div className="copilot-msg-row assistant">
            <div className="copilot-avatar">
              <Bot size={13} color="var(--accent-text)" />
            </div>
            <div className="copilot-bubble" style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span className="spinner" />
              <span style={{ fontSize: "11.5px", color: "var(--text-tertiary)" }}>Analyzing merchant financial data & policy models...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* ── PROMPT SUGGESTIONS ────────────────────────────────────── */}
      <div style={{
        display: "flex", gap: 6, overflowX: "auto", padding: "8px 16px",
        borderTop: "1px solid var(--border-subtle)", background: "var(--bg-app)"
      }}>
        {PROMPT_SUGGESTIONS.map((p, i) => (
          <button
            key={i}
            className="btn btn-sm"
            style={{ fontSize: "11px", whiteSpace: "nowrap", borderRadius: "var(--radius-xs)" }}
            onClick={() => sendMessage(p)}
            disabled={loading}
          >
            {p}
          </button>
        ))}
      </div>

      {/* ── INPUT BOX ─────────────────────────────────────────────── */}
      <div style={{
        display: "flex", gap: 8, padding: "12px 16px",
        borderTop: "1px solid var(--border)", background: "var(--bg-surface)"
      }}>
        <input
          style={{
            flex: 1, background: "var(--bg-input)", border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)", padding: "0 12px", color: "var(--text-primary)",
            fontSize: "12.5px", outline: "none", height: "34px", fontFamily: "var(--font-sans)"
          }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
          placeholder={`Ask advisory question about ${merchant?.merchant_name || mid}...`}
          disabled={loading}
        />
        <button
          className="btn btn-primary"
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          style={{ height: "34px" }}
        >
          <Send size={13} />
        </button>
      </div>
    </div>
  );
}

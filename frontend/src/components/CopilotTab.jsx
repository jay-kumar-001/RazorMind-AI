import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { 
  getConversations, createConversation, renameConversation, 
  deleteConversation, clearConversations, getConversationMessages, 
  stopChatGeneration, getOllamaModels, uploadFileAnalysis, getExportUrl 
} from "../api/api";
import { 
  Send, Bot, User, Sparkles, Trash2, Plus, Search, 
  StopCircle, RotateCcw, Copy, Paperclip, Mic, Download, 
  BookOpen, Briefcase, Shield, TrendingUp, Compass, Edit2
} from "lucide-react";

const PERSONALITIES = [
  { id: "general", label: "General Assistant", icon: <Compass size={12} /> },
  { id: "analyst", label: "Business Analyst", icon: <BookOpen size={12} /> },
  { id: "risk", label: "Risk Expert", icon: <Shield size={12} /> },
  { id: "underwriter", label: "Risk Underwriter", icon: <Briefcase size={12} /> },
  { id: "growth", label: "Growth Consultant", icon: <TrendingUp size={12} /> }
];

const PROMPT_SUGGESTIONS_GENERAL = [
  "Explain LangGraph orchestration",
  "Write a Python script to sort a list",
  "What is the difference between RNN and Transformer?",
  "How to prepare for a software engineer interview"
];

const PROMPT_SUGGESTIONS_MERCHANT = [
  "Why is this merchant risky?",
  "What is the churn probability for next month?",
  "Suggest ways to improve payment success rate",
  "Summarize the underwriting decision and rationale"
];

export default function CopilotTab({ merchant }) {
  // Sidebar states
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  
  // Active Conversation states
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  
  // Settings states
  const [mode, setMode] = useState("general"); // 'merchant' | 'general'
  const [personality, setPersonality] = useState("general");
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("qwen2.5:3b");
  const [ollamaStatus, setOllamaStatus] = useState("online");
  const [devMode, setDevMode] = useState(true);

  // File Upload states
  const [attachedFile, setAttachedFile] = useState(null); // { name, summary, content }
  const [uploading, setUploading] = useState(false);
  
  // Voice Input states
  const [recording, setRecording] = useState(false);

  // Streaming cancel ref
  const activeReaderRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // --- Initialize Models and Conversations ---
  useEffect(() => {
    loadModels();
    loadConversations();
  }, []);

  // --- Auto update mode when merchant context changes ---
  useEffect(() => {
    if (merchant) {
      setMode("merchant");
    }
  }, [merchant?.merchant_id]);

  // --- Refresh messages when active conversation changes ---
  useEffect(() => {
    if (activeConvId) {
      loadMessages(activeConvId);
    } else {
      setMessages([]);
    }
  }, [activeConvId]);

  // --- Scroll to bottom ---
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent, loading]);

  const loadModels = async () => {
    try {
      const res = await getOllamaModels();
      setOllamaStatus(res.data.status);
      setModels(res.data.models || []);
      if (res.data.active_default) {
        setSelectedModel(res.data.active_default);
      }
    } catch {
      setOllamaStatus("offline");
    }
  };

  const loadConversations = async (search = "") => {
    try {
      const res = await getConversations(search);
      const list = Array.isArray(res.data) ? res.data : [];
      setConversations(list);
      // Auto select first conversation if none selected
      if (list.length > 0 && !activeConvId) {
        setActiveConvId(list[0].id);
        setMode(list[0].mode);
        setPersonality(list[0].personality);
        if (list[0].model_used) setSelectedModel(list[0].model_used);
      }
    } catch {
      setConversations([]);
    }
  };

  const loadMessages = async (convId) => {
    try {
      const res = await getConversationMessages(convId);
      setMessages(Array.isArray(res.data) ? res.data : []);
    } catch {
      setMessages([]);
    }
  };

  const handleCreateChat = async () => {
    try {
      const payload = {
        title: `Conversation ${conversations.length + 1}`,
        mode: mode,
        personality: personality,
        merchant_id: mode === "merchant" ? merchant?.merchant_id : null,
        model_used: selectedModel
      };
      const res = await createConversation(payload);
      setActiveConvId(res.data.id);
      loadConversations();
    } catch (err) {
      console.error("Failed to create chat:", err);
    }
  };

  const handleRenameChat = async (id, currentTitle) => {
    const newTitle = prompt("Rename conversation thread:", currentTitle);
    if (!newTitle || !newTitle.trim()) return;
    try {
      await renameConversation(id, newTitle.trim());
      loadConversations(searchQuery);
    } catch (err) {
      console.error("Failed to rename chat:", err);
    }
  };

  const handleDeleteChat = async (e, id) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this chat thread?")) return;
    try {
      await deleteConversation(id);
      if (activeConvId === id) {
        setActiveConvId(null);
      }
      loadConversations(searchQuery);
    } catch (err) {
      console.error("Failed to delete chat:", err);
    }
  };

  const handleClearHistory = async () => {
    if (!confirm("Delete all persistent chat histories from database? This cannot be undone.")) return;
    try {
      await clearConversations();
      setActiveConvId(null);
      setConversations([]);
      setMessages([]);
    } catch (err) {
      console.error("Failed to clear history:", err);
    }
  };

  // --- SSE Chat Streaming & Stop Trigger ---

  const handleSendMessage = async (textToSend = null) => {
    let q = (textToSend || input).trim();
    if (!q) return;

    // Check if conversation exists, if not, create one first
    let currentConvId = activeConvId;
    if (!currentConvId) {
      try {
        const payload = {
          title: q.slice(0, 20) + (q.length > 20 ? "..." : ""),
          mode: mode,
          personality: personality,
          merchant_id: mode === "merchant" ? merchant?.merchant_id : null,
          model_used: selectedModel
        };
        const res = await createConversation(payload);
        currentConvId = res.data.id;
        setActiveConvId(currentConvId);
      } catch (err) {
        console.error("Failed to auto-create conversation:", err);
        return;
      }
    }

    // Attach uploaded file context if present
    if (attachedFile) {
      q = `[File Uploaded: ${attachedFile.name}]\nFile Summary:\n${attachedFile.summary}\n\nUser Question:\n${q}`;
    }

    setInput("");
    setAttachedFile(null);
    setLoading(true);
    setStreamingContent("");
    
    // Add user message to UI state instantly (optimistic update)
    setMessages((prev) => [
      ...prev,
      { id: "temp-user", role: "user", content: textToSend || input, model_used: selectedModel }
    ]);

    try {
      const response = await fetch("http://127.0.0.1:8000/copilot/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: currentConvId,
          question: q,
          model_name: selectedModel
        })
      });

      if (!response.ok) {
        throw new Error("HTTP error " + response.status);
      }

      const reader = response.body.getReader();
      activeReaderRef.current = reader;
      const decoder = new TextDecoder();
      let buffer = "";
      let fullContent = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // Hold remaining partial line

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;

            try {
              const payload = jsonParse(dataStr);
              if (payload.token) {
                fullContent += payload.token;
                setStreamingContent(fullContent);
              }
              if (payload.event === "done" || payload.event === "stop") {
                // Done event contains observability meta
                break;
              }
            } catch (e) {
              // Ignore parse errors on partial streams
            }
          }
        }
      }
    } catch (err) {
      console.error("Fetch stream error:", err);
      setMessages((prev) => [
        ...prev,
        { 
          id: "temp-err", 
          role: "assistant", 
          content: "⚠️ Underwriting advisor service timed out or offline. Ensure Ollama is running (`ollama run qwen2.5:3b`) and try again." 
        }
      ]);
    } finally {
      activeReaderRef.current = null;
      setStreamingContent("");
      setLoading(false);
      // Reload final persistent conversation ledger & message list
      loadConversations(searchQuery);
      loadMessages(currentConvId);
    }
  };

  const jsonParse = (str) => {
    try {
      return JSON.parse(str);
    } catch {
      return {};
    }
  };

  const handleStopGenerating = async () => {
    if (activeReaderRef.current) {
      await activeReaderRef.current.cancel();
    }
    try {
      await stopChatGeneration(activeConvId, "Cancel Request", selectedModel);
    } catch (err) {
      console.error("Stop generation call failed:", err);
    }
    setLoading(false);
  };

  const handleRegenerate = async (lastUserMessage) => {
    if (!lastUserMessage) return;
    handleSendMessage(lastUserMessage);
  };

  const handleDeleteMessage = async (msgId) => {
    // Note: We can implement a message delete endpoint if needed, or simply delete locally.
    // For local database simplicity, we can let user delete from UI or clear convo.
    setMessages((prev) => prev.filter(m => m.id !== msgId));
  };

  // --- Voice Input (Web Speech API) ---
  const handleToggleVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice input Speech Recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    if (recording) {
      setRecording(false);
      return;
    }

    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = "en-IN"; // English/Hindi combined detection

    rec.onstart = () => {
      setRecording(true);
    };

    rec.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => prev + (prev ? " " : "") + transcript);
    };

    rec.onerror = (e) => {
      console.error("Speech Recognition Error:", e);
      setRecording(false);
    };

    rec.onend = () => {
      setRecording(false);
    };

    rec.start();
  };

  // --- File Upload Handler ---
  const handleTriggerUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const res = await uploadFileAnalysis(file);
      if (res.data.status === "success") {
        setAttachedFile({
          name: file.name,
          summary: res.data.parsed_summary,
          content: res.data.text_content
        });
      }
    } catch (err) {
      alert("Failed to process file: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // --- Helper to render custom markdown items ---
  const markdownRenderComponents = {
    p: ({ children }) => <p style={{ marginBottom: "8px", lineHeight: "1.6" }}>{children}</p>,
    strong: ({ children }) => <strong style={{ color: "var(--text-primary)", fontWeight: 600 }}>{children}</strong>,
    li: ({ children }) => <li style={{ marginLeft: "18px", marginBottom: "4px", listStyleType: "disc" }}>{children}</li>,
    h1: ({ children }) => <h1 style={{ fontSize: "16px", fontWeight: 700, margin: "16px 0 8px", color: "var(--text-primary)" }}>{children}</h1>,
    h2: ({ children }) => <h2 style={{ fontSize: "14px", fontWeight: 600, margin: "12px 0 6px", color: "var(--text-primary)" }}>{children}</h2>,
    h3: ({ children }) => <h3 style={{ fontSize: "13px", fontWeight: 600, margin: "10px 0 4px", color: "var(--text-primary)" }}>{children}</h3>,
    table: ({ children }) => (
      <div style={{ overflowX: "auto", margin: "12px 0" }}>
        <table className="data-table" style={{ width: "100%", fontSize: "12px" }}>{children}</table>
      </div>
    ),
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline ? (
        <div style={{ margin: "12px 0", background: "#0b0d14", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", overflow: "hidden" }}>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "6px 12px", background: "var(--bg-subtle)", borderBottom: "1px solid var(--border-subtle)", fontSize: "11px", color: "var(--text-tertiary)", fontFamily: "var(--font-sans)" }}>
            <span>{match ? match[1].toUpperCase() : 'CODE'}</span>
            <button 
              onClick={() => {
                navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
                alert("Code copied to clipboard!");
              }} 
              style={{ background: "transparent", border: "none", color: "var(--text-secondary)", cursor: "pointer", display: "flex", alignItems: "center", gap: 4, fontSize: "11px" }}
            >
              <Copy size={11} /> Copy
            </button>
          </div>
          <pre style={{ padding: "12px", overflowX: "auto", margin: 0, fontFamily: "var(--font-mono)", fontSize: "12px", color: "#a6accd", lineHeight: "1.5" }}>
            <code>{children}</code>
          </pre>
        </div>
      ) : (
        <code className={className} style={{ background: "var(--bg-subtle)", padding: "2px 4px", borderRadius: "3px", fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--accent-text)" }} {...props}>
          {children}
        </code>
      );
    }
  };

  const getActiveSuggestions = () => {
    return mode === "merchant" ? PROMPT_SUGGESTIONS_MERCHANT : PROMPT_SUGGESTIONS_GENERAL;
  };

  const getLastUserMessage = () => {
    const userMsgs = messages.filter(m => m.role === "user");
    return userMsgs.length > 0 ? userMsgs[userMsgs.length - 1].content : null;
  };

  return (
    <div className="copilot-layout">
      {/* ─── SIDEBAR: CONVERSATION LEDGER ──────────────────────────── */}
      <aside className="copilot-sidebar">
        <div className="sidebar-header">
          <span style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-secondary)" }}>
            Conversations
          </span>
          <button className="btn btn-sm btn-primary" onClick={handleCreateChat} style={{ padding: "3px 8px", borderRadius: "var(--radius-xs)" }}>
            <Plus size={12} /> New Chat
          </button>
        </div>

        <div className="sidebar-search">
          <div className="sidebar-search-box">
            <Search size={11} style={{ color: "var(--text-tertiary)" }} />
            <input 
              placeholder="Search chat..." 
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                loadConversations(e.target.value);
              }}
            />
          </div>
        </div>

        <div className="sidebar-list">
          {conversations.map((c) => (
            <div 
              key={c.id} 
              className={`sidebar-item${c.id === activeConvId ? " active" : ""}`}
              onClick={() => {
                setActiveConvId(c.id);
                setMode(c.mode);
                setPersonality(c.personality);
                if (c.model_used) setSelectedModel(c.model_used);
              }}
            >
              <div className="sidebar-item-title">{c.title}</div>
              <div className="sidebar-item-meta">
                <span>{c.mode === "merchant" ? "Merchant" : "General"}</span>
                <span>{new Date(c.updated_at).toLocaleDateString()}</span>
              </div>
              <div className="sidebar-item-actions">
                <button className="sidebar-item-btn" title="Rename" onClick={() => handleRenameChat(c.id, c.title)}>
                  <Edit2 size={11} />
                </button>
                <button className="sidebar-item-btn" title="Delete" onClick={(e) => handleDeleteChat(e, c.id)}>
                  <Trash2 size={11} />
                </button>
              </div>
            </div>
          ))}
          {conversations.length === 0 && (
            <div style={{ textAlign: "center", color: "var(--text-tertiary)", fontSize: "11.5px", padding: "20px 10px" }}>
              No previous threads found. Click New Chat.
            </div>
          )}
        </div>

        {conversations.length > 0 && (
          <div style={{ padding: 10, borderTop: "1px solid var(--border-subtle)", textAlign: "center" }}>
            <button className="message-action-btn" onClick={handleClearHistory} style={{ margin: "0 auto", color: "var(--rose-text)" }}>
              <Trash2 size={11} /> Clear Thread History
            </button>
          </div>
        )}
      </aside>

      {/* ─── MAIN WORKSPACE: CHAT PLATFORM ────────────────────────── */}
      <main className="copilot-workspace">
        {/* Workspace Controls Header */}
        <div className="workspace-header">
          <div className="workspace-controls">
            {/* Mode Switcher */}
            <div className="control-toggle-wrap">
              <button 
                className={`control-toggle-btn${mode === "merchant" ? " active" : ""}`}
                onClick={() => {
                  if (mode !== "merchant" && !merchant) {
                    alert("Please select a merchant first from the top search bar to use Merchant Mode.");
                    return;
                  }
                  setMode("merchant");
                }}
              >
                Merchant Intelligence
              </button>
              <button 
                className={`control-toggle-btn${mode === "general" ? " active" : ""}`}
                onClick={() => setMode("general")}
              >
                General AI
              </button>
            </div>

            {/* Personality Selector */}
            <select 
              className="control-select"
              value={personality}
              onChange={async (e) => {
                const val = e.target.value;
                setPersonality(val);
                if (activeConvId) {
                  // Auto create a new thread or update active convo settings in future endpoints
                }
              }}
            >
              {PERSONALITIES.map(p => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
          </div>

          <div className="workspace-controls">
            {/* Model Dropdown */}
            <select 
              className="control-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              title={`Ollama server: ${ollamaStatus}`}
              style={{ borderColor: ollamaStatus === "offline" ? "var(--rose-border)" : "var(--border)" }}
            >
              {models.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
              {models.length === 0 && (
                <option value="qwen2.5:3b">qwen2.5:3b (Offline)</option>
              )}
            </select>

            {/* Export options */}
            {activeConvId && messages.length > 0 && (
              <div style={{ display: "flex", gap: 4 }}>
                <a className="btn btn-sm" href={getExportUrl(activeConvId, "md")} target="_blank" rel="noreferrer" title="Export Markdown">
                  <Download size={11} /> MD
                </a>
                <a className="btn btn-sm" href={getExportUrl(activeConvId, "pdf")} target="_blank" rel="noreferrer" title="Export PDF">
                  PDF
                </a>
              </div>
            )}
            
            {/* Developer Mode checkbox */}
            <label style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "11px", color: "var(--text-tertiary)", cursor: "pointer" }}>
              <input type="checkbox" checked={devMode} onChange={(e) => setDevMode(e.target.checked)} />
              Dev Metrics
            </label>
          </div>
        </div>

        {/* Conversation Logs */}
        <div className="copilot-chat-area">
          {/* Active Context Banner */}
          {mode === "merchant" && merchant && (
            <div style={{ display: "flex", alignItems: "center", gap: 10, background: "var(--accent-subtle)", border: "1px solid rgba(99, 102, 241, 0.15)", borderRadius: "var(--radius)", padding: "10px 14px", fontSize: "12px", color: "var(--text-primary)" }}>
              <Sparkles size={14} color="var(--accent-text)" />
              <div>
                Grounded in active merchant: <strong style={{ color: "var(--accent-text)" }}>{merchant.merchant_name || merchant.merchant_id}</strong> ({merchant.merchant_id}). 
                Risk Score: <strong>{riskScore.toFixed(1)}</strong> | Success Rate: <strong>{Number(merchant.success_rate).toFixed(1)}%</strong>.
              </div>
            </div>
          )}

          {/* Render Messages */}
          {messages.map((msg) => {
            const isUser = msg.role === "user";
            return (
              <div key={msg.id} className={`copilot-msg-row ${msg.role}`}>
                <div className="copilot-avatar">
                  {isUser ? <User size={13} color="var(--text-secondary)" /> : <Bot size={13} color="var(--accent-text)" />}
                </div>
                <div style={{ display: "flex", flexDirection: "column", maxWidth: "90%" }}>
                  <div className="copilot-bubble">
                    <ReactMarkdown components={markdownRenderComponents}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                  
                  {/* Actions & Observability Row for Assistant */}
                  {!isUser && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                      <div className="message-actions-row">
                        <button 
                          className="message-action-btn" 
                          onClick={() => {
                            navigator.clipboard.writeText(msg.content);
                            alert("Response text copied!");
                          }}
                        >
                          <Copy size={10} /> Copy
                        </button>
                        <button 
                          className="message-action-btn" 
                          onClick={() => handleRegenerate(getLastUserMessage())}
                          disabled={loading}
                        >
                          <RotateCcw size={10} /> Regenerate
                        </button>
                        <button 
                          className="message-action-btn" 
                          onClick={() => handleDeleteMessage(msg.id)}
                          style={{ color: "var(--rose-text)" }}
                        >
                          <Trash2 size={10} /> Delete
                        </button>
                      </div>

                      {/* Agent Visibility Panel */}
                      {msg.agents_consulted && msg.agents_consulted.length > 0 && (
                        <div className="agent-visibility-panel">
                          {msg.agents_consulted.map(agent => (
                            <span key={agent} className="agent-visibility-tag">✓ {agent} consulted</span>
                          ))}
                        </div>
                      )}

                      {/* Observability Badge */}
                      {devMode && msg.tokens && (
                        <span className="observability-badge">
                          Latency: {Number(msg.latency || 0).toFixed(2)}s | Generated Tokens: {msg.tokens} | Model: {msg.model_used || selectedModel} | Speed: {((msg.tokens) / max1(msg.latency)).toFixed(1)} tokens/sec
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Render Streaming response chunk */}
          {streamingContent && (
            <div className="copilot-msg-row assistant">
              <div className="copilot-avatar">
                <Bot size={13} color="var(--accent-text)" />
              </div>
              <div className="copilot-bubble" style={{ maxWidth: "90%" }}>
                <ReactMarkdown components={markdownRenderComponents}>
                  {streamingContent}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {/* Loader */}
          {loading && !streamingContent && (
            <div className="copilot-msg-row assistant">
              <div className="copilot-avatar">
                <Bot size={13} color="var(--accent-text)" />
              </div>
              <div className="copilot-bubble" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="spinner" />
                <span style={{ fontSize: "11.5px", color: "var(--text-tertiary)" }}>
                  Advisor AI resolving diagnostics & model reasoning...
                </span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestion Chips */}
        {!loading && messages.length > 0 && (
          <div style={{ display: "flex", gap: 6, overflowX: "auto", padding: "8px 16px", background: "var(--bg-app)", borderTop: "1px solid var(--border-subtle)" }}>
            {getActiveSuggestions().map((p, i) => (
              <button
                key={i}
                className="btn btn-sm"
                style={{ fontSize: "11px", whiteSpace: "nowrap", borderRadius: "var(--radius-xs)" }}
                onClick={() => handleSendMessage(p)}
              >
                {p}
              </button>
            ))}
          </div>
        )}

        {/* Upload & Voice Input Panel */}
        <div style={{ display: "flex", flexDirection: "column", borderTop: "1px solid var(--border)", background: "var(--bg-surface)", padding: "10px 16px" }}>
          
          {/* File Attachment Status Bar */}
          {attachedFile && (
            <div style={{ marginBottom: 8 }} className="file-attachment-chip">
              <span>📁 {attachedFile.name} (Ready)</span>
              <button className="file-attachment-close" onClick={() => setAttachedFile(null)}>×</button>
            </div>
          )}

          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            {/* Attachment Button */}
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              style={{ display: "none" }}
              accept=".txt,.pdf,.csv,.xlsx"
            />
            <button 
              className="btn" 
              onClick={handleTriggerUpload}
              disabled={loading || uploading}
              style={{ height: "34px", width: "34px", padding: 0 }}
              title="Attach File (TXT, PDF, CSV, XLSX)"
            >
              {uploading ? <span className="spinner" style={{ width: 12, height: 12 }} /> : <Paperclip size={13} />}
            </button>

            {/* Voice Input Button */}
            <button 
              className="btn"
              onClick={handleToggleVoice}
              disabled={loading}
              style={{ 
                height: "34px", width: "34px", padding: 0,
                color: recording ? "var(--rose-text)" : "var(--text-primary)",
                borderColor: recording ? "var(--rose-border)" : "var(--border)",
                background: recording ? "var(--rose-subtle)" : "var(--bg-elevated)"
              }}
              title={recording ? "Recording... Click to stop" : "Voice Input (Speech-to-Text)"}
            >
              <Mic size={13} className={recording ? "pulse" : ""} />
            </button>

            {/* Main Text Input */}
            <input
              style={{
                flex: 1, background: "var(--bg-input)", border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)", padding: "0 12px", color: "var(--text-primary)",
                fontSize: "12.5px", outline: "none", height: "34px", fontFamily: "var(--font-sans)"
              }}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSendMessage()}
              placeholder={mode === "merchant" && merchant 
                ? `Ask underwriting advisor about ${merchant.merchant_name || merchant.merchant_id}...` 
                : "Ask general AI questions (coding, machine learning, business)..."}
              disabled={loading}
            />

            {/* Send / Stop Buttons */}
            {loading ? (
              <button 
                className="btn btn-primary"
                onClick={handleStopGenerating}
                style={{ height: "34px", background: "var(--rose)", borderColor: "var(--rose)" }}
                title="Stop Generating"
              >
                <StopCircle size={13} /> Stop
              </button>
            ) : (
              <button 
                className="btn btn-primary"
                onClick={() => handleSendMessage()}
                disabled={!input.trim() && !attachedFile}
                style={{ height: "34px" }}
              >
                <Send size={13} />
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

// Simple safely bounded max helpers to avoid Math errors in render
const max1 = (v) => Math.max(0.01, Number(v || 0.01));

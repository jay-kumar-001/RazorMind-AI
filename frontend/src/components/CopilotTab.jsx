import React, { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import {
  getConversations,
  createConversation,
  renameConversation,
  deleteConversation,
  clearConversations,
  getConversationMessages,
  deleteMessage,
  editMessage,
  getMessageVersions,
  setMessageVersion,
  stopChatGeneration,
  getOllamaModels,
  uploadFileAnalysis,
  getExportUrl,
} from "../api/api";
import {
  Send,
  Bot,
  User,
  Sparkles,
  Trash2,
  Plus,
  Search,
  StopCircle,
  RotateCcw,
  Copy,
  Check,
  Paperclip,
  Mic,
  Download,
  BookOpen,
  Briefcase,
  Shield,
  TrendingUp,
  Compass,
  Edit2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Cpu,
  Layers,
  HelpCircle,
  Code2,
  CornerDownLeft,
} from "lucide-react";

const PERSONALITIES = [
  { id: "general", label: "General Assistant", icon: Compass },
  { id: "analyst", label: "Business Analyst", icon: BookOpen },
  { id: "risk", label: "Risk Expert", icon: Shield },
  { id: "underwriter", label: "Risk Underwriter", icon: Briefcase },
  { id: "growth", label: "Growth Consultant", icon: TrendingUp },
];

const STARTER_CATEGORIES = [
  {
    category: "Merchant Intelligence",
    icon: Shield,
    color: "var(--accent)",
    prompts: [
      "What is happening with this merchant?",
      "Why is churn risk elevated?",
      "Explain the revenue forecast and confidence bounds",
      "Summarize the underwriting decision and 30-day playbook",
    ],
  },
  {
    category: "RazorMind Architecture",
    icon: Layers,
    color: "var(--emerald-text)",
    prompts: [
      "What does the RazorMind platform do?",
      "Explain the LangGraph 10-agent orchestration workflow",
      "How is the composite risk score calculated?",
      "What does the Digital Twin simulation engine do?",
    ],
  },
  {
    category: "General Tech & AI",
    icon: Cpu,
    color: "var(--amber-text)",
    prompts: [
      "Explain Transformer self-attention architecture",
      "How does UPI payment authorization flow work?",
      "Write a Python function for weighted moving average",
      "Explain the difference between FastAPI and Flask",
    ],
  },
];

export default function CopilotTab({ merchant }) {
  const riskScore = merchant?.risk_score || 0.0;

  // Sidebar & Layout states
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [editingConvId, setEditingConvId] = useState(null);
  const [editingConvTitle, setEditingConvTitle] = useState("");

  // Active Conversation states
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [editingMsgId, setEditingMsgId] = useState(null);
  const [editMsgContent, setEditMsgContent] = useState("");

  // Settings states
  const [mode, setMode] = useState("merchant"); // 'merchant' | 'general'
  const [personality, setPersonality] = useState("general");
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("qwen3:8b");
  const [ollamaStatus, setOllamaStatus] = useState("online");
  const [devMode, setDevMode] = useState(false);

  // Copied states (for tooltip/icon feedback)
  const [copiedMsgId, setCopiedMsgId] = useState(null);
  const [copiedCodeKey, setCopiedCodeKey] = useState(null);

  // File Upload states
  const [attachedFile, setAttachedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Voice Input states
  const [recording, setRecording] = useState(false);

  // Smart Scrolling states & refs
  const [isNearBottom, setIsNearBottom] = useState(true);
  const [showScrollBottomBtn, setShowScrollBottomBtn] = useState(false);
  const chatAreaRef = useRef(null);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const activeReaderRef = useRef(null);
  const fileInputRef = useRef(null);

  // --- Initialize Models and Conversations ---
  useEffect(() => {
    loadModels();
    loadConversations();
  }, []);

  // --- Auto-switch to merchant mode when merchant context arrives ---
  useEffect(() => {
    if (merchant?.merchant_id) {
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

  // --- Smart Scroll Management ---
  const handleChatScroll = useCallback(() => {
    if (!chatAreaRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = chatAreaRef.current;
    const distanceToBottom = scrollHeight - scrollTop - clientHeight;
    const near = distanceToBottom < 90;
    setIsNearBottom(near);
    setShowScrollBottomBtn(!near && scrollHeight > clientHeight + 120);
  }, []);

  const scrollToBottom = (behavior = "smooth") => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior });
    }
  };

  useEffect(() => {
    if (isNearBottom) {
      scrollToBottom("auto");
    }
  }, [messages, streamingContent, loading, isNearBottom]);

  // --- Auto resize textarea ---
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  // --- API Handlers ---
  const loadModels = async (sync = false) => {
    try {
      const res = await getOllamaModels(sync);
      setOllamaStatus(res.data.status || "online");
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
      if (list.length > 0 && !activeConvId) {
        setActiveConvId(list[0].id);
        setMode(list[0].mode || "general");
        setPersonality(list[0].personality || "general");
        if (list[0].model_used) setSelectedModel(list[0].model_used);
      }
    } catch {
      setConversations([]);
    }
  };

  const loadMessages = async (convId) => {
    try {
      const res = await getConversationMessages(convId);
      const data = res.data;
      setMessages(Array.isArray(data) ? data : data.messages || []);
      setTimeout(() => scrollToBottom("auto"), 50);
    } catch {
      setMessages([]);
    }
  };

  const handleCreateChat = async () => {
    try {
      const payload = {
        title: "New Conversation",
        mode: mode,
        personality: personality,
        merchant_id: mode === "merchant" ? merchant?.merchant_id : null,
        model_used: selectedModel,
      };
      const res = await createConversation(payload);
      setActiveConvId(res.data.id);
      loadConversations();
      setInput("");
      setAttachedFile(null);
      if (textareaRef.current) textareaRef.current.focus();
    } catch (err) {
      console.error("Failed to create chat:", err);
    }
  };

  const handleSaveRename = async (id) => {
    if (!editingConvTitle.trim()) {
      setEditingConvId(null);
      return;
    }
    try {
      await renameConversation(id, editingConvTitle.trim());
      setEditingConvId(null);
      loadConversations(searchQuery);
    } catch (err) {
      console.error("Failed to rename conversation:", err);
    }
  };

  const handleDeleteChat = async (e, id) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      if (activeConvId === id) {
        const remaining = conversations.filter((c) => c.id !== id);
        setActiveConvId(remaining.length > 0 ? remaining[0].id : null);
      }
      loadConversations(searchQuery);
    } catch (err) {
      console.error("Failed to delete chat:", err);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm("Delete all conversations and persistent chat history?")) return;
    try {
      await clearConversations();
      setActiveConvId(null);
      setConversations([]);
      setMessages([]);
    } catch (err) {
      console.error("Failed to clear history:", err);
    }
  };

  // --- Message Delete & Edit Handlers ---
  const handleDeleteMessage = async (msgId) => {
    if (!activeConvId) return;
    try {
      await deleteMessage(msgId, activeConvId);
      setMessages((prev) => prev.filter((m) => m.id !== msgId));
    } catch (err) {
      console.error("Failed to delete message:", err);
    }
  };

  const handleStartEditMessage = (msg) => {
    setEditingMsgId(msg.id);
    setEditMsgContent(msg.content);
  };

  const handleSaveEditAndResend = async (msgId) => {
    if (!editMsgContent.trim()) return;
    setEditingMsgId(null);
    handleSendMessage(editMsgContent.trim(), { edit_message_id: msgId });
  };

  // --- Version Switcher for Regenerated Messages ---
  const handleSwitchVersion = async (parentMsgId, direction) => {
    if (!activeConvId) return;
    try {
      const res = await getMessageVersions(parentMsgId, activeConvId);
      const versions = res.data || [];
      if (versions.length <= 1) return;

      const currentIdx = versions.findIndex((v) => v.is_current === 1);
      let targetIdx = direction === "next" ? currentIdx + 1 : currentIdx - 1;
      if (targetIdx < 0) targetIdx = versions.length - 1;
      if (targetIdx >= versions.length) targetIdx = 0;

      const targetMsg = versions[targetIdx];
      await setMessageVersion(activeConvId, targetMsg.id);
      loadMessages(activeConvId);
    } catch (err) {
      console.error("Failed to switch version:", err);
    }
  };

  // --- SSE Chat Streaming & Stop Handling ---
  const handleSendMessage = async (textToSend = null, options = {}) => {
    let q = (textToSend !== null ? textToSend : input).trim();
    if (!q && !options.regenerate) return;

    let currentConvId = activeConvId;
    if (!currentConvId) {
      try {
        const payload = {
          title: q.slice(0, 28) + (q.length > 28 ? "..." : ""),
          mode: mode,
          personality: personality,
          merchant_id: mode === "merchant" ? merchant?.merchant_id : null,
          model_used: selectedModel,
        };
        const res = await createConversation(payload);
        currentConvId = res.data.id;
        setActiveConvId(currentConvId);
      } catch (err) {
        console.error("Failed to auto-create conversation:", err);
        return;
      }
    }

    if (attachedFile && !options.regenerate) {
      q = `[File Uploaded: ${attachedFile.name}]\nSummary:\n${attachedFile.summary}\n\nUser Question:\n${q}`;
    }

    setInput("");
    setAttachedFile(null);
    setLoading(true);
    setStreamingContent("");
    setIsNearBottom(true);

    if (!options.regenerate && !options.edit_message_id) {
      setMessages((prev) => [
        ...prev,
        {
          id: `temp-${Date.now()}`,
          role: "user",
          content: textToSend !== null ? textToSend : input,
          timestamp: new Date().toISOString(),
          model_used: selectedModel,
        },
      ]);
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/copilot/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: currentConvId,
          question: q,
          model_name: selectedModel,
          personality: personality,
          mode: mode,
          merchant_id: mode === "merchant" ? merchant?.merchant_id : null,
          regenerate: options.regenerate || false,
          parent_message_id: options.parent_message_id || null,
          edit_message_id: options.edit_message_id || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
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
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;
            try {
              const payload = JSON.parse(dataStr);
              if (payload.token) {
                fullContent += payload.token;
                setStreamingContent(fullContent);
              }
              if (payload.event === "done" || payload.event === "stop") {
                break;
              }
            } catch {
              // Ignore partial JSON parse errors
            }
          }
        }
      }
    } catch (err) {
      console.error("Stream error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "⚠️ Advisor AI could not connect to Ollama. Verify that Ollama daemon is running (`ollama serve`) and try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      activeReaderRef.current = null;
      setStreamingContent("");
      setLoading(false);
      loadConversations(searchQuery);
      loadMessages(currentConvId);
    }
  };

  const handleStopGenerating = async () => {
    if (activeReaderRef.current) {
      await activeReaderRef.current.cancel();
    }
    if (activeConvId) {
      try {
        await stopChatGeneration(activeConvId, "", selectedModel);
      } catch (err) {
        console.error("Stop generation call failed:", err);
      }
    }
    setLoading(false);
  };

  const handleRegenerate = async (lastUserMsg) => {
    if (!lastUserMsg) return;
    handleSendMessage(lastUserMsg.content, {
      regenerate: true,
      parent_message_id: lastUserMsg.id,
    });
  };

  // --- Copy Feedback Helpers ---
  const handleCopyText = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(id);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const handleCopyCode = (key, code) => {
    navigator.clipboard.writeText(code);
    setCopiedCodeKey(key);
    setTimeout(() => setCopiedCodeKey(null), 2000);
  };

  // --- Voice Input (Speech Recognition) ---
  const handleToggleVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Use Chrome, Edge, or Safari.");
      return;
    }

    if (recording) {
      setRecording(false);
      return;
    }

    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = "en-US";

    rec.onstart = () => setRecording(true);
    rec.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => prev + (prev ? " " : "") + transcript);
    };
    rec.onerror = () => setRecording(false);
    rec.onend = () => setRecording(false);
    rec.start();
  };

  // --- File Upload ---
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
          content: res.data.text_content,
        });
      }
    } catch (err) {
      alert("Failed to parse file: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // --- Markdown Custom Renderers ---
  const markdownRenderComponents = {
    p: ({ children }) => <p className="chat-md-p">{children}</p>,
    strong: ({ children }) => <strong className="chat-md-strong">{children}</strong>,
    li: ({ children }) => <li className="chat-md-li">{children}</li>,
    h1: ({ children }) => <h1 className="chat-md-h1">{children}</h1>,
    h2: ({ children }) => <h2 className="chat-md-h2">{children}</h2>,
    h3: ({ children }) => <h3 className="chat-md-h3">{children}</h3>,
    table: ({ children }) => (
      <div className="chat-md-table-wrap">
        <table className="data-table" style={{ width: "100%", fontSize: "12px" }}>
          {children}
        </table>
      </div>
    ),
    code({ inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || "");
      const lang = match ? match[1].toLowerCase() : "code";
      const codeString = String(children).replace(/\n$/, "");
      const codeKey = `${lang}-${codeString.slice(0, 20)}`;

      return !inline ? (
        <div className="chat-code-block">
          <div className="chat-code-header">
            <span className="chat-code-lang">{lang.toUpperCase()}</span>
            <button
              className="chat-code-copy-btn"
              onClick={() => handleCopyCode(codeKey, codeString)}
              title="Copy code"
            >
              {copiedCodeKey === codeKey ? (
                <>
                  <Check size={11} color="var(--emerald-text)" />
                  <span style={{ color: "var(--emerald-text)" }}>Copied!</span>
                </>
              ) : (
                <>
                  <Copy size={11} />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
          <pre className="chat-code-pre">
            <code>{children}</code>
          </pre>
        </div>
      ) : (
        <code className="chat-inline-code" {...props}>
          {children}
        </code>
      );
    },
  };

  const getLastUserMessage = () => {
    const userMsgs = messages.filter((m) => m.role === "user");
    return userMsgs.length > 0 ? userMsgs[userMsgs.length - 1] : null;
  };

  const formatTimestamp = (ts) => {
    if (!ts) return "";
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  };

  return (
    <div className={`chatgpt-container ${sidebarOpen ? "sidebar-expanded" : "sidebar-collapsed"}`}>
      {/* ─── SIDEBAR: PERSISTENT CONVERSATION LEDGER ──────────────── */}
      <aside className="chatgpt-sidebar">
        <div className="sidebar-top">
          <button className="chatgpt-new-chat-btn" onClick={handleCreateChat}>
            <Plus size={14} />
            <span>New Chat</span>
          </button>
          <button
            className="sidebar-toggle-btn"
            onClick={() => setSidebarOpen(false)}
            title="Collapse sidebar"
          >
            <ChevronLeft size={16} />
          </button>
        </div>

        {/* Search Box */}
        <div className="sidebar-search-container">
          <div className="sidebar-search-box">
            <Search size={12} style={{ color: "var(--text-tertiary)" }} />
            <input
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                loadConversations(e.target.value);
              }}
            />
            {searchQuery && (
              <button
                className="search-clear-btn"
                onClick={() => {
                  setSearchQuery("");
                  loadConversations("");
                }}
              >
                <X size={11} />
              </button>
            )}
          </div>
        </div>

        {/* Conversation List */}
        <div className="sidebar-thread-list">
          {conversations.map((c) => {
            const isActive = c.id === activeConvId;
            const isEditing = c.id === editingConvId;

            return (
              <div
                key={c.id}
                className={`sidebar-thread-item ${isActive ? "active" : ""}`}
                onClick={() => {
                  if (!isEditing) {
                    setActiveConvId(c.id);
                    setMode(c.mode || "general");
                    setPersonality(c.personality || "general");
                    if (c.model_used) setSelectedModel(c.model_used);
                  }
                }}
              >
                {isEditing ? (
                  <div className="thread-inline-edit" onClick={(e) => e.stopPropagation()}>
                    <input
                      autoFocus
                      value={editingConvTitle}
                      onChange={(e) => setEditingConvTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleSaveRename(c.id);
                        if (e.key === "Escape") setEditingConvId(null);
                      }}
                    />
                    <button
                      className="inline-save-btn"
                      onClick={() => handleSaveRename(c.id)}
                      title="Save"
                    >
                      <Check size={12} />
                    </button>
                    <button
                      className="inline-cancel-btn"
                      onClick={() => setEditingConvId(null)}
                      title="Cancel"
                    >
                      <X size={12} />
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="thread-title-area">
                      <span className="thread-title">{c.title || "Untitled Conversation"}</span>
                      <div className="thread-meta">
                        <span className="thread-tag">{c.mode === "merchant" ? "Merchant" : "General"}</span>
                        <span>{new Date(c.updated_at).toLocaleDateString([], { month: "short", day: "numeric" })}</span>
                      </div>
                    </div>
                    <div className="thread-actions">
                      <button
                        className="thread-action-btn"
                        title="Rename"
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingConvId(c.id);
                          setEditingConvTitle(c.title);
                        }}
                      >
                        <Edit2 size={11} />
                      </button>
                      <button
                        className="thread-action-btn delete"
                        title="Delete"
                        onClick={(e) => handleDeleteChat(e, c.id)}
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            );
          })}

          {conversations.length === 0 && (
            <div className="sidebar-empty">
              <Sparkles size={20} style={{ opacity: 0.4, marginBottom: 8 }} />
              <p>No chat history</p>
              <span>Click New Chat to begin</span>
            </div>
          )}
        </div>

        {/* Sidebar Footer */}
        {conversations.length > 0 && (
          <div className="sidebar-footer">
            <button className="sidebar-clear-btn" onClick={handleClearHistory}>
              <Trash2 size={12} /> Clear all history
            </button>
          </div>
        )}
      </aside>

      {/* ─── MAIN WORKSPACE ────────────────────────────────────────── */}
      <main className="chatgpt-main">
        {/* Workspace Top Navigation / Controls */}
        <header className="chatgpt-header">
          <div className="header-left">
            {!sidebarOpen && (
              <button
                className="header-icon-btn"
                onClick={() => setSidebarOpen(true)}
                title="Expand sidebar"
              >
                <Menu size={16} />
              </button>
            )}

            {/* Mode Switcher Pills */}
            <div className="mode-pill-toggle">
              <button
                className={`mode-pill ${mode === "merchant" ? "active" : ""}`}
                onClick={() => {
                  if (mode !== "merchant" && !merchant) {
                    alert("Please select a merchant from the top search bar first.");
                    return;
                  }
                  setMode("merchant");
                }}
              >
                <Shield size={12} /> Merchant Intelligence
              </button>
              <button
                className={`mode-pill ${mode === "general" ? "active" : ""}`}
                onClick={() => setMode("general")}
              >
                <Compass size={12} /> General AI
              </button>
            </div>

            {/* Personality Selector */}
            <select
              className="chat-select"
              value={personality}
              onChange={(e) => setPersonality(e.target.value)}
              title="Advisor Persona"
            >
              {PERSONALITIES.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          <div className="header-right">
            {/* Model Selector & Status Badge */}
            <div className="model-selector-wrap">
              <span
                className={`status-dot ${ollamaStatus === "online" ? "online" : "offline"}`}
                title={`Ollama: ${ollamaStatus}`}
              />
              <select
                className="chat-select model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                title="Active Local LLM"
              >
                {models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
                {models.length === 0 && (
                  <option value="qwen3:8b">qwen3:8b (Offline)</option>
                )}
              </select>
              <button
                className="header-sync-btn"
                onClick={() => loadModels(true)}
                title="Sync local models from Ollama daemon"
              >
                Sync
              </button>
            </div>

            {/* Export Dropdown */}
            {activeConvId && messages.length > 0 && (
              <div className="export-group">
                <a
                  className="header-btn"
                  href={getExportUrl(activeConvId, "md")}
                  target="_blank"
                  rel="noreferrer"
                  title="Export Markdown"
                >
                  <Download size={11} /> MD
                </a>
                <a
                  className="header-btn"
                  href={getExportUrl(activeConvId, "pdf")}
                  target="_blank"
                  rel="noreferrer"
                  title="Export PDF"
                >
                  PDF
                </a>
              </div>
            )}

            {/* Dev Metrics Toggle */}
            <label className="dev-metrics-toggle" title="Show token speeds and agent traces">
              <input
                type="checkbox"
                checked={devMode}
                onChange={(e) => setDevMode(e.target.checked)}
              />
              <span>Dev Metrics</span>
            </label>
          </div>
        </header>

        {/* Active Merchant Context Banner */}
        {mode === "merchant" && merchant && (
          <div className="merchant-context-banner">
            <div className="merchant-banner-content">
              <Sparkles size={14} className="banner-sparkle" />
              <span>
                Grounded in: <strong>{merchant.merchant_name || merchant.merchant_id}</strong> ({merchant.merchant_id}) | Risk Score:{" "}
                <strong>{riskScore.toFixed(1)}/100</strong> | Auth Rate:{" "}
                <strong>{Number(merchant.success_rate || 0).toFixed(1)}%</strong> | GMV:{" "}
                <strong>INR {Number(merchant.total_revenue || 0).toLocaleString()}</strong>
              </span>
            </div>
          </div>
        )}

        {/* ─── CHAT MESSAGES SCROLL AREA ───────────────────────────── */}
        <div
          className="chatgpt-scroll-area"
          ref={chatAreaRef}
          onScroll={handleChatScroll}
        >
          {/* Welcome Screen / Empty State */}
          {messages.length === 0 && !streamingContent && !loading && (
            <div className="chatgpt-welcome-screen">
              <div className="welcome-hero">
                <div className="welcome-avatar-glow">
                  <Bot size={28} color="var(--accent-text)" />
                </div>
                <h2>RazorMind Advisor AI</h2>
                <p>
                  Your ChatGPT-class assistant for real-time merchant analytics, risk attribution,
                  predictive forecasting, and general multi-turn reasoning.
                </p>
              </div>

              <div className="starter-grid">
                {STARTER_CATEGORIES.map((cat, idx) => (
                  <div key={idx} className="starter-category-card">
                    <div className="category-header">
                      <cat.icon size={15} style={{ color: cat.color }} />
                      <span>{cat.category}</span>
                    </div>
                    <div className="starter-prompts-list">
                      {cat.prompts.map((p, pIdx) => (
                        <button
                          key={pIdx}
                          className="starter-prompt-btn"
                          onClick={() => handleSendMessage(p)}
                        >
                          <span>{p}</span>
                          <CornerDownLeft size={11} className="prompt-arrow" />
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Rendered Messages */}
          {messages.map((msg) => {
            const isUser = msg.role === "user";
            const isEditing = editingMsgId === msg.id;

            return (
              <div key={msg.id} className={`chat-message-row ${msg.role}`}>
                <div className="chat-avatar">
                  {isUser ? (
                    <User size={14} color="var(--text-secondary)" />
                  ) : (
                    <Bot size={14} color="var(--accent-text)" />
                  )}
                </div>

                <div className="chat-bubble-container">
                  {isEditing ? (
                    <div className="inline-message-editor">
                      <textarea
                        value={editMsgContent}
                        onChange={(e) => setEditMsgContent(e.target.value)}
                        rows={3}
                      />
                      <div className="editor-action-row">
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => handleSaveEditAndResend(msg.id)}
                        >
                          Save & Submit
                        </button>
                        <button
                          className="btn btn-sm"
                          onClick={() => setEditingMsgId(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="chat-bubble">
                      <ReactMarkdown components={markdownRenderComponents}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  )}

                  {/* Actions Bar */}
                  <div className="chat-actions-bar">
                    {msg.timestamp && (
                      <span className="chat-timestamp">{formatTimestamp(msg.timestamp)}</span>
                    )}

                    {isUser && !isEditing && (
                      <button
                        className="chat-action-icon-btn"
                        onClick={() => handleStartEditMessage(msg)}
                        title="Edit message"
                      >
                        <Edit2 size={11} />
                        <span>Edit</span>
                      </button>
                    )}

                    {!isUser && (
                      <>
                        <button
                          className="chat-action-icon-btn"
                          onClick={() => handleCopyText(msg.id, msg.content)}
                          title="Copy message"
                        >
                          {copiedMsgId === msg.id ? (
                            <>
                              <Check size={11} color="var(--emerald-text)" />
                              <span style={{ color: "var(--emerald-text)" }}>Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy size={11} />
                              <span>Copy</span>
                            </>
                          )}
                        </button>

                        <button
                          className="chat-action-icon-btn"
                          onClick={() => handleRegenerate(getLastUserMessage())}
                          disabled={loading}
                          title="Regenerate reply"
                        >
                          <RotateCcw size={11} />
                          <span>Regenerate</span>
                        </button>

                        {/* Version switcher if multi-version assistant replies exist */}
                        {msg.version && msg.version > 1 && (
                          <div className="version-switcher">
                            <button
                              onClick={() => handleSwitchVersion(msg.parent_id || msg.id, "prev")}
                              title="Previous version"
                            >
                              <ChevronLeft size={11} />
                            </button>
                            <span>v{msg.version}</span>
                            <button
                              onClick={() => handleSwitchVersion(msg.parent_id || msg.id, "next")}
                              title="Next version"
                            >
                              <ChevronRight size={11} />
                            </button>
                          </div>
                        )}
                      </>
                    )}

                    <button
                      className="chat-action-icon-btn delete-btn"
                      onClick={() => handleDeleteMessage(msg.id)}
                      title="Delete message"
                    >
                      <Trash2 size={11} />
                    </button>
                  </div>

                  {/* Multi-Agent Consultation Tags */}
                  {!isUser && msg.agents_consulted && msg.agents_consulted.length > 0 && (
                    <div className="agent-consulted-tags">
                      {msg.agents_consulted.map((agent, aIdx) => (
                        <span key={aIdx} className="agent-tag">
                          ✓ {agent}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Dev Metrics Badge */}
                  {!isUser && devMode && msg.tokens && (
                    <div className="chat-dev-badge">
                      <span>Latency: {Number(msg.latency || 0).toFixed(2)}s</span>
                      <span>•</span>
                      <span>Tokens: {msg.tokens}</span>
                      <span>•</span>
                      <span>Model: {msg.model_used || selectedModel}</span>
                      <span>•</span>
                      <span>
                        Speed: {(msg.tokens / Math.max(0.01, Number(msg.latency || 0.01))).toFixed(1)} t/s
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Active Token Stream Chunk */}
          {streamingContent && (
            <div className="chat-message-row assistant streaming">
              <div className="chat-avatar">
                <Bot size={14} color="var(--accent-text)" />
              </div>
              <div className="chat-bubble-container">
                <div className="chat-bubble">
                  <ReactMarkdown components={markdownRenderComponents}>
                    {streamingContent}
                  </ReactMarkdown>
                  <span className="streaming-cursor">▊</span>
                </div>
              </div>
            </div>
          )}

          {/* Typing Wave / Reasoning Indicator */}
          {loading && !streamingContent && (
            <div className="chat-message-row assistant">
              <div className="chat-avatar">
                <Bot size={14} color="var(--accent-text)" />
              </div>
              <div className="chat-bubble-container">
                <div className="typing-indicator-bubble">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-text">Advisor AI is reasoning...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Floating Scroll to Bottom Button */}
        {showScrollBottomBtn && (
          <button
            className="floating-scroll-bottom-btn"
            onClick={() => scrollToBottom("smooth")}
            title="Scroll to bottom"
          >
            <ChevronDown size={15} />
          </button>
        )}

        {/* ─── CHAT COMPOSER / INPUT AREA ──────────────────────────── */}
        <div className="chatgpt-composer-container">
          {/* File Attachment Chip */}
          {attachedFile && (
            <div className="composer-file-chip">
              <Paperclip size={12} />
              <span className="file-name">{attachedFile.name}</span>
              <button
                className="file-remove-btn"
                onClick={() => setAttachedFile(null)}
                title="Remove attached file"
              >
                <X size={12} />
              </button>
            </div>
          )}

          {/* Composer Input Box */}
          <div className="composer-box">
            {/* File upload hidden input */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              style={{ display: "none" }}
              accept=".txt,.pdf,.csv,.xlsx"
            />

            {/* Left Action Buttons */}
            <div className="composer-left-actions">
              <button
                className="composer-icon-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading || uploading}
                title="Attach Document (TXT, PDF, CSV, XLSX)"
              >
                {uploading ? <span className="spinner" style={{ width: 12, height: 12 }} /> : <Paperclip size={15} />}
              </button>

              <button
                className={`composer-icon-btn ${recording ? "recording" : ""}`}
                onClick={handleToggleVoice}
                disabled={loading}
                title={recording ? "Recording... Click to stop" : "Voice Input (Speech-to-Text)"}
              >
                <Mic size={15} className={recording ? "pulse" : ""} />
              </button>
            </div>

            {/* Auto-growing Textarea */}
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (!loading && (input.trim() || attachedFile)) {
                    handleSendMessage();
                  }
                }
              }}
              placeholder={
                mode === "merchant" && merchant
                  ? `Ask about ${merchant.merchant_name || merchant.merchant_id} (risk, churn, revenue, forecast)...`
                  : "Message Advisor AI (coding, architecture, questions)..."
              }
              disabled={loading}
            />

            {/* Send / Stop Buttons */}
            <div className="composer-right-actions">
              {loading ? (
                <button
                  className="composer-stop-btn"
                  onClick={handleStopGenerating}
                  title="Stop generating"
                >
                  <StopCircle size={15} />
                  <span>Stop</span>
                </button>
              ) : (
                <button
                  className={`composer-send-btn ${input.trim() || attachedFile ? "ready" : ""}`}
                  onClick={() => handleSendMessage()}
                  disabled={!input.trim() && !attachedFile}
                  title="Send message (Enter)"
                >
                  <Send size={14} />
                </button>
              )}
            </div>
          </div>

          <div className="composer-disclaimer">
            Advisor AI is powered by local LLMs and RazorMind multi-agent telemetry. Shift+Enter for new line.
          </div>
        </div>
      </main>
    </div>
  );
}

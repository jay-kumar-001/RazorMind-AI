import { useCallback, useEffect, useRef, useState } from "react";
import { Search, ShieldAlert, Sparkles, TrendingUp, Cpu, ClipboardList, Activity, MessageSquare, LayoutGrid } from "lucide-react";
import { getMerchant, getMerchants } from "./api/api";

import OverviewTab from "./components/OverviewTab";
import RiskTab from "./components/RiskTab";
import ForecastTab from "./components/ForecastTab";
import DigitalTwinTab from "./components/DigitalTwinTab";
import ActionPlanTab from "./components/ActionPlanTab";
import ExecutiveTab from "./components/ExecutiveTab";
import ObservabilityTab from "./components/ObservabilityTab";
import CopilotTab from "./components/CopilotTab";

import "./App.css";

const TABS = [
  { id: "overview", label: "Overview", icon: <LayoutGrid size={13} /> },
  { id: "risk", label: "Risk & Attribution", icon: <ShieldAlert size={13} /> },
  { id: "forecast", label: "Revenue Lab", icon: <TrendingUp size={13} /> },
  { id: "twin", label: "Digital Twin", icon: <Cpu size={13} /> },
  { id: "action", label: "Action Roadmap", icon: <ClipboardList size={13} /> },
  { id: "executive", label: "Executive Brief", icon: <Sparkles size={13} /> },
  { id: "observability", label: "Telemetry & Traces", icon: <Activity size={13} /> },
  { id: "copilot", label: "Advisor", icon: <MessageSquare size={13} />, isAi: true },
];

export default function App() {
  const [tab, setTab] = useState("overview");
  const [merchant, setMerchant] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("M0001");
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggest, setShowSuggest] = useState(false);
  const [suggestIdx, setSuggestIdx] = useState(-1);
  const suggestRef = useRef(null);
  const searchRef = useRef(null);
  const debounceTimer = useRef(null);

  const loadMerchant = useCallback(async (id) => {
    if (!id?.trim()) return;
    setLoading(true);
    setShowSuggest(false);
    setSuggestions([]);
    try {
      const res = await getMerchant(id.trim().toUpperCase());
      if (res.data && !res.data.error) {
        setMerchant(res.data);
        setSearchQuery(res.data.merchant_id);
      } else {
        setMerchant(null);
      }
    } catch {
      setMerchant(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSearchInput = (value) => {
    setSearchQuery(value);
    clearTimeout(debounceTimer.current);
    if (value.length < 1) {
      setSuggestions([]);
      setShowSuggest(false);
      return;
    }
    debounceTimer.current = setTimeout(async () => {
      try {
        const res = await getMerchants(value, 1, 8);
        const list = Array.isArray(res.data?.merchants) ? res.data.merchants : Array.isArray(res.data) ? res.data : [];
        setSuggestions(list.slice(0, 8));
        setShowSuggest(list.length > 0);
      } catch {
        setSuggestions([]);
        setShowSuggest(false);
      }
    }, 180);
  };

  const selectSuggestion = (m) => {
    setSearchQuery(m.merchant_id);
    setShowSuggest(false);
    setSuggestions([]);
    loadMerchant(m.merchant_id);
  };

  const handleKeyDown = (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSuggestIdx((i) => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSuggestIdx((i) => Math.max(i - 1, -1));
    } else if (e.key === "Enter") {
      if (suggestIdx >= 0 && suggestions[suggestIdx]) selectSuggestion(suggestions[suggestIdx]);
      else loadMerchant(searchQuery);
      setShowSuggest(false);
    } else if (e.key === "Escape") {
      setShowSuggest(false);
    }
  };

  useEffect(() => {
    const handler = (e) => {
      if (suggestRef.current && !suggestRef.current.contains(e.target)) setShowSuggest(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Global keydown for search shortcut ⌘K / Ctrl+K
  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        searchRef.current?.focus();
        searchRef.current?.select();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    loadMerchant("M0001");
  }, [loadMerchant]);

  const riskScore = Number(merchant?.risk_score || 0);
  const riskTier = riskScore < 30 ? "LOW" : riskScore < 60 ? "MEDIUM" : riskScore < 80 ? "HIGH" : "CRITICAL";
  const healthScore = Number(merchant?.merchant_health_score || 0);

  return (
    <div className="app-shell">
      {/* ── TOP NAVIGATION ────────────────────────────────────────── */}
      <header className="topbar">
        <div className="topbar-brand">
          <div className="brand-icon">R</div>
          <span className="brand-title">RazorMind</span>
          <span className="topbar-badge">v2.0</span>
        </div>

        <div className="topbar-divider" />

        {/* Search */}
        <div className="merchant-search-wrap" ref={suggestRef}>
          <div className="merchant-search-box">
            <Search size={13} />
            <input
              ref={searchRef}
              value={searchQuery}
              onChange={(e) => handleSearchInput(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => suggestions.length > 0 && setShowSuggest(true)}
              placeholder="Search merchant ID or brand..."
              aria-label="Merchant search"
            />
            {loading ? (
              <span className="spinner" />
            ) : (
              <span className="kbd-shortcut">⌘K</span>
            )}
          </div>

          {showSuggest && suggestions.length > 0 && (
            <div className="search-autocomplete">
              {suggestions.map((s, i) => (
                <div
                  key={s.merchant_id || `sugg-${i}`}
                  className={`autocomplete-item${i === suggestIdx ? " selected" : ""}`}
                  onClick={() => selectSuggestion(s)}
                  onMouseEnter={() => setSuggestIdx(i)}
                >
                  <span className="ac-id">{s.merchant_id}</span>
                  <span className="ac-name">{s.merchant_name || "—"}</span>
                  <span className={`tag tag-${(s.risk_level || "low").toLowerCase()}`}>
                    {s.risk_level || "LOW"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Topbar telemetry items */}
        <div className="topbar-right">
          <div className="status-indicator">
            <span className="status-dot" />
            <span>Operational</span>
          </div>
          <span className="pill-metric">14 Agents</span>
          <span className="pill-metric">500 Merchants</span>
        </div>
      </header>

      {/* ── SECONDARY SUB-NAV ─────────────────────────────────────── */}
      <nav className="nav-tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`nav-tab${tab === t.id ? " active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            <span className="tab-icon">{t.icon}</span>
            <span>{t.label}</span>
            {t.isAi && <span className="tab-badge-ai">AI</span>}
          </button>
        ))}
      </nav>

      {/* ── MERCHANT CONTEXT STRIP ────────────────────────────────── */}
      {merchant && (
        <section className="merchant-strip">
          <div className="merchant-strip-inner">
            <div className="merchant-primary">
              <div className="merchant-avatar-box">
                {merchant.merchant_name?.[0] || merchant.merchant_id?.[0] || "M"}
              </div>
              <div className="merchant-headings">
                <h1>
                  {merchant.merchant_name || merchant.merchant_id}
                  <span className={`tag tag-${riskTier.toLowerCase()}`}>{riskTier} RISK</span>
                </h1>
                <div className="merchant-meta">
                  <span className="mono-id">{merchant.merchant_id}</span>
                  <span>·</span>
                  <span>{merchant.category || "E-Commerce"}</span>
                  <span>·</span>
                  <span>{merchant.industry || "Retail"}</span>
                  <span>·</span>
                  <span style={{ color: "var(--emerald-text)" }}>{merchant.merchant_status || "ACTIVE"}</span>
                </div>
              </div>
            </div>

            <div className="merchant-kpi-group">
              <div className="kpi-cell">
                <div className="kpi-label">Health Index</div>
                <div className="kpi-val" style={{ color: healthScore >= 70 ? "var(--emerald-text)" : healthScore >= 50 ? "var(--amber-text)" : "var(--rose-text)" }}>
                  {healthScore.toFixed(1)} <span style={{ fontSize: 11, color: "var(--text-tertiary)" }}>/ 100</span>
                </div>
              </div>
              <div className="kpi-cell">
                <div className="kpi-label">Risk Score</div>
                <div className="kpi-val" style={{ color: riskScore < 35 ? "var(--emerald-text)" : riskScore < 65 ? "var(--amber-text)" : "var(--rose-text)" }}>
                  {riskScore.toFixed(1)}
                </div>
              </div>
              <div className="kpi-cell">
                <div className="kpi-label">Gross Revenue</div>
                <div className="kpi-val">
                  ₹{Number(merchant.total_revenue || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                </div>
              </div>
              <div className="kpi-cell">
                <div className="kpi-label">Auth Rate</div>
                <div className="kpi-val">
                  {Number(merchant.success_rate || 90).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ── MAIN CONTENT ──────────────────────────────────────────── */}
      <main className="page-content">
        {loading && (
          <div className="grid-4" style={{ marginBottom: 20 }}>
            {[...Array(4)].map((_, i) => (
              <div key={i} className="kpi-card skeleton" style={{ height: 100 }} />
            ))}
          </div>
        )}

        {!loading && (
          <>
            {tab === "overview" && <OverviewTab merchant={merchant} />}
            {tab === "risk" && <RiskTab merchant={merchant} />}
            {tab === "forecast" && <ForecastTab merchant={merchant} />}
            {tab === "twin" && <DigitalTwinTab merchant={merchant} />}
            {tab === "action" && <ActionPlanTab merchant={merchant} />}
            {tab === "executive" && <ExecutiveTab merchant={merchant} />}
            {tab === "observability" && <ObservabilityTab merchant={merchant} />}
            {tab === "copilot" && <CopilotTab merchant={merchant} />}
          </>
        )}
      </main>
    </div>
  );
}

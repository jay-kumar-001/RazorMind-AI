import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 120000,
});

// ─── Merchant Intelligence ────────────────────────────────────────────────────
export const getMerchants = (search = "", page = 1, limit = 20) =>
  API.get("/merchants", { params: { search, page, limit } });

export const getMerchant = (id) => API.get(`/merchant/${id}`);
export const getForecast = (id) => API.get(`/merchant/${id}/forecast`);
export const getChurn = (id) => API.get(`/merchant/${id}/churn`);
export const getRootCause = (id) => API.get(`/merchant/${id}/root-cause`);
export const getMerchantTrend = (id) => API.get(`/merchant-trend/${id}`);
export const getMerchantHistory = (id) => API.get(`/merchant-history/${id}`);

// ─── Portfolio Dashboard ──────────────────────────────────────────────────────
export const getDashboard = () => API.get("/dashboard");
export const getRecentAnalyses = () => API.get("/recent-analyses");

// ─── AI Agent Outputs ─────────────────────────────────────────────────────────
export const getActionPlan = (id) => API.get(`/action-plan/${id}`);
export const getDecision = (id) => API.get(`/decision/${id}`);
export const getExecutiveReport = (id) => API.get(`/executive-report/${id}`);
export const getAnalysis = (id) => API.get(`/analysis/${id}`);

// ─── Copilot ──────────────────────────────────────────────────────────────────
export const askCopilot = (id, question) =>
  API.get(`/copilot/${id}`, { params: { question } });

export const postCopilot = (payload) => API.post("/copilot/ask", payload);

// ─── Digital Twin Simulation ──────────────────────────────────────────────────
export const runSimulation = (payload) => API.post("/simulate", payload);

// ─── Observability ────────────────────────────────────────────────────────────
export const getTraces = (id) => API.get(`/agent-traces/${id}`);
export const getTracesSummary = () => API.get("/traces/summary");

// ─── PDF Download ─────────────────────────────────────────────────────────────
export const getPdfUrl = (id) => `http://127.0.0.1:8000/download-report/${id}`;

// ─── Trigger Analysis ─────────────────────────────────────────────────────────
export const triggerAnalysis = (id) => API.post(`/analyze/${id}`);

export default API;
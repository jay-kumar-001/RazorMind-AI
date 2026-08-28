# RazorMind AI ⚡🧠

### *Enterprise Autonomous Merchant Intelligence, Risk Underwriting & Digital Twin Simulation Platform*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2.8-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00.svg?style=flat&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-4169E1.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🌟 Executive Summary

**RazorMind AI** is a production-grade, enterprise-ready **AI Merchant Intelligence & Underwriting Engine** designed for payment gateways, fintech platforms, neobanks, and merchant aggregators (comparable to *Stripe Radar*, *Shopify Analytics*, and *Razorpay Risk Intelligence*).

Powered by a **14-agent LangGraph orchestration pipeline**, **statistical & ML forecasting models**, a **real-time Digital Twin simulation sandbox**, and an **investor-ready PDF export engine**, RazorMind AI transforms raw transaction and behavioral logs into actionable risk decisions, revenue projections, and operational roadmaps.

---

## 🚀 Key Features

### 1. 🤖 14-Agent LangGraph Autonomous Workflow
- **Graph Orchestration**: Agents execute sequentially with structured state-passing:
  $$\text{Revenue} \rightarrow \text{Forecast} \rightarrow \text{Risk} \rightarrow \text{Churn} \rightarrow \text{KPI} \rightarrow \text{Root Cause} \rightarrow \text{Recommendation} \rightarrow \text{Decision} \rightarrow \text{Action Plan} \rightarrow \text{Executive Report}$$
- **Multi-Tier Resilient LLM Engine**: Zero downtime guarantee with intelligent fallback:
  1. Local Ollama (`qwen2.5:3b` / `llama3.2:3b`)
  2. Cloud LLMs (OpenAI / Gemini)
  3. Deterministic High-Fidelity Heuristic Synthesis

### 2. 🔮 Digital Twin Simulation Sandbox
- Interactive **"What-If" parameter modeling**:
  - Adjust Success Rate ($\Delta\%$), Refund Rate ($\Delta\%$), Churn Reduction ($\Delta\%$), Retention Boost ($\Delta\%$), and Volume Growth ($\Delta\%$).
- Real-time recalculation of **Merchant Health Score (0–100)**, projected cash flows, revenue lift, and risk migration.

### 3. 📈 Statistical & ML Forecasting Lab
- Multi-horizon forecasting (30, 60, 90, 180 days) using exponential trend smoothing and seasonal adjustments.
- Computes **95% confidence intervals** (Low, Mid, High bounds) with trend direction and volatility metrics.

### 4. 🛡️ Multi-Factor Risk & Root Cause Engine
- Deep risk scoring factoring in:
  - Transaction failure velocity & refund ratios
  - Customer churn propensity and retention degradation
  - Revenue volatility and customer concentration risk
- Automated **Root Cause Pinpointing** with severity tagging (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and exact bottleneck evidence.

### 5. 📋 Dynamic 30-Day Tactical Action Plan
- Generates week-by-week prioritized mitigation playbooks.
- Tracks estimated ROI, operational checkpoints, and automated task verification.

### 6. 📑 Investor-Grade Executive Reports & PDF Export
- Generates structured executive briefings with health badges, risk factor radar breakdowns, and governance decisions.
- **One-Click Dynamic PDF Export** generated server-side via ReportLab.

### 7. 🔬 Full Observability & Trace Telemetry
- Real-time agent execution telemetry, execution latencies (ms), input/output payloads, and interactive LangGraph state visualizer.

### 8. 💬 Merchant Copilot
- Context-aware AI assistant grounded in the active merchant's real-time financial telemetry, KYC history, and risk profile.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[FastAPI Gateway / REST API] --> B[Multi-Agent LangGraph Engine]
    A --> C[Merchant & Portfolio Services]
    A --> D[Digital Twin Simulation Engine]
    A --> E[Observability & Trace Telemetry]
    A --> F[Dynamic PDF Report Generator]

    subgraph "Agent Orchestration (LangGraph)"
        B --> B1[Revenue Agent]
        B1 --> B2[Forecast Agent - Trend + Confidence]
        B2 --> B3[Risk Agent - Multi-Factor Engine]
        B3 --> B4[Churn Agent - Probability & Decay]
        B4 --> B5[KPI & Benchmark Agent]
        B5 --> B6[Root Cause Agent - Anomaly Diagnostics]
        B6 --> B7[Recommendation Agent - ROI Playbooks]
        B7 --> B8[Decision Agent - Governance & Thresholds]
        B8 --> B9[Action Plan Agent - 30-Day Roadmap]
        B9 --> B10[Executive Report Agent - Investor Brief]
    end

    subgraph "Core Data & AI Layer"
        D --> D1[Dynamic Parameter Recalculator]
        C --> DB[(PostgreSQL / SQLite Storage)]
        LLM[Resilient Multi-Tier LLM Service] --> B10
        LLM --> Copilot[Merchant Copilot Assistant]
    end

    subgraph "Frontend UI (React 19 + Vite)"
        UI[Glassmorphism Dark Dashboard] --> A
    end
```

---

## 🤖 The 14 Specialized Agents

| # | Agent Name | Responsibility | Primary Output |
|---|---|---|---|
| 1 | **Revenue Agent** | Aggregates volume, velocity, AOV, and growth metrics | Financial Summary & Trajectory |
| 2 | **Forecast Agent** | Runs trend smoothing with 95% confidence intervals | 30/60/90-Day Revenue Projection |
| 3 | **Risk Agent** | Evaluates multi-factor risk scores and risk categories | Risk Scorecard (0–100) & Status |
| 4 | **Churn Agent** | Analyzes merchant churn propensity and retention curves | Churn Probability & Warning Level |
| 5 | **KPI Agent** | Benchmarks performance against industry cohorts | Percentile Rank & Health Index |
| 6 | **Root Cause Agent** | Isolates anomalies in payment gateways, refunds, or KYC | Primary Bottleneck & Evidence |
| 7 | **Recommendation Agent** | Prescribes targeted high-ROI operational interventions | Prioritized Recommendations |
| 8 | **Decision Agent** | Executes governance policy (`APPROVE`, `MONITOR`, `REJECT`) | Underwriting Decision & Rationale |
| 9 | **Action Plan Agent** | Builds a tactical 4-week execution roadmap | 30-Day Milestones & Deliverables |
| 10 | **Executive Report Agent** | Synthesizes an investor-ready executive briefing | Full Executive Intelligence Brief |
| 11 | **Digital Twin Agent** | Simulates hypothetical business parameter adjustments | Simulated Health, Rev & Churn |
| 12 | **Copilot Agent** | Grounded Q&A assistant for interactive merchant querying | Contextual Natural Language Answers |
| 13 | **Final Report Agent** | Consolidates end-to-end multi-agent payloads | Master Audit Payload |
| 14 | **Simulation Agent** | Scenario modeling wrapper for portfolio stress testing | Stress Test Matrix |

---

## 💻 Tech Stack

### **Frontend**
- **Framework**: React 19 + Vite (Ultra-fast HMR)
- **Styling**: Custom Modern Glassmorphic Dark CSS (Stripe Radar / Linear aesthetic)
- **Data Visualizations**: Recharts (Area charts, Bar charts, Responsive containers)
- **Animations**: Framer Motion (Smooth layout transitions, staggered tabs)
- **Icons**: Lucide React
- **Markdown Rendering**: React Markdown

### **Backend & API**
- **Framework**: FastAPI (High performance asynchronous ASGI)
- **Validation**: Pydantic v2
- **Document Generation**: ReportLab (Vector PDF synthesis)
- **Server**: Uvicorn

### **Data & Multi-Agent Layer**
- **Workflow Engine**: LangGraph & LangChain Core
- **Database / ORM**: PostgreSQL & SQLite via SQLAlchemy 2.0
- **Analytics & ML**: NumPy, Pandas, Scikit-Learn
- **LLM Support**: Ollama (Local), OpenAI / Gemini (Cloud), Heuristic Fallback Engine

---

## 📁 Repository Directory Structure

```text
razormind-ai/
├── agents/                      # 14 Autonomous AI Agent Definitions
│   ├── action_plan_agent.py
│   ├── churn_agent.py
│   ├── copilot_agent.py
│   ├── decision_agent.py
│   ├── digital_twin_agent.py
│   ├── executive_report_agent.py
│   ├── final_report_agent.py
│   ├── forecast_agent.py
│   ├── kpi_agent.py
│   ├── recommendation_agent.py
│   ├── revenue_agent.py
│   ├── risk_agent.py
│   ├── rootcause_agent.py
│   └── simulation_agent.py
├── backend/                     # FastAPI Application & Business Logic
│   ├── app.py                   # Main FastAPI Entry Point
│   ├── database.py              # SQLAlchemy Engine & Session
│   ├── models.py                # Database Models (Merchants, Traces, Logs)
│   ├── routes/                  # Modular Route Controllers (20+ Endpoints)
│   │   ├── action_plan.py
│   │   ├── copilot.py
│   │   ├── dashboard.py
│   │   ├── decision.py
│   │   ├── forecast.py
│   │   ├── merchant.py
│   │   ├── pdf_report.py
│   │   ├── rootcause.py
│   │   ├── simulate.py
│   │   └── traces.py
│   └── services/                # Core Computation Engines
│       ├── churn_service.py
│       ├── forecast_service.py
│       ├── llm_service.py       # Multi-Tier Resilient LLM Engine
│       ├── risk_service.py      # Multi-Factor Risk Engine
│       └── simulation_service.py# Digital Twin Mathematical Modeler
├── database/                    # Database Migrations & Seeders
│   └── migrate_csv_to_postgres.py
├── datasets/                    # Datasets (500 synthetic merchant profiles)
│   ├── merchant_data.csv
│   └── transactions.csv
├── frontend/                    # Modern React 19 Frontend
│   ├── src/
│   │   ├── components/          # Tab Views & UI Components
│   │   │   ├── OverviewTab.jsx
│   │   │   ├── RiskTab.jsx
│   │   │   ├── ForecastTab.jsx
│   │   │   ├── DigitalTwinTab.jsx
│   │   │   ├── ActionPlanTab.jsx
│   │   │   ├── ExecutiveTab.jsx
│   │   │   ├── ObservabilityTab.jsx
│   │   │   └── CopilotTab.jsx
│   │   ├── App.jsx              # Main Dashboard Controller
│   │   └── App.css              # Custom SaaS Design System
│   └── package.json
├── graphs/                      # LangGraph Workflow Architecture
│   ├── merchant_graph.py        # StateGraph Pipeline Definition
│   ├── nodes.py                 # Graph Execution Nodes
│   └── state.py                 # Pydantic MerchantState Schema
├── generate_datasets.py         # Synthetic Enterprise Dataset Generator
├── requirements.txt             # Backend Python Dependencies
├── test_suite.py                # Comprehensive 12-Point Automated Test Suite
└── README.md
```

---

## ⚡ Quickstart Guide

### Prerequisites
- **Python**: `3.10` or higher
- **Node.js**: `18.x` or higher
- **Git**
- *(Optional)* **Ollama** installed locally if running local LLMs (`ollama run qwen2.5:3b`)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/razormind-ai.git
cd razormind-ai
```

---

### Step 2: Backend Setup

1. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Generate datasets and seed the database:
   ```bash
   # Generate 500 comprehensive merchant profiles
   python generate_datasets.py

   # Migrate data to database (SQLite / PostgreSQL)
   python database/migrate_csv_to_postgres.py
   ```

4. Start the FastAPI backend server:
   ```bash
   uvicorn backend.app:app --reload --port 8000
   ```
   > 📍 API will be running at: `http://localhost:8000`  
   > 📚 Interactive API Docs (Swagger): `http://localhost:8000/docs`

---

### Step 3: Frontend Setup

1. In a new terminal, navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   > 🌐 Dashboard will be live at: `http://localhost:5173`

---

## 🧪 Testing & Verification

RazorMind AI includes a comprehensive 12-point automated verification test suite:

```bash
python test_suite.py
```

### Verified Subsystems:
- [x] **Health Check**: Backend server & agent readiness
- [x] **Portfolio Dashboard**: Multi-merchant KPIs and status aggregates
- [x] **Merchant Intelligence**: Real-time health score calculation
- [x] **Forecast Engine**: 95% confidence interval validation
- [x] **Churn Predictor**: Machine learning churn probability scoring
- [x] **Digital Twin Sandbox**: Dynamic parameter recalibration
- [x] **Action Plan**: 4-week structured milestone generation
- [x] **Underwriting Decision**: Rule & ML policy governance
- [x] **Root Cause Diagnostics**: Primary bottleneck identification
- [x] **Observability Traces**: Agent execution latency logging
- [x] **Executive Briefing**: Investor report generation
- [x] **Copilot Assistant**: Grounded context-aware Q&A response

---

## 📡 Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status and agent readiness |
| `GET` | `/dashboard` | Portfolio-wide metrics, distribution & health summary |
| `GET` | `/merchant/{id}` | Detailed merchant financial & risk profile |
| `GET` | `/merchant/{id}/forecast` | 30/60/90-day forecast with confidence intervals |
| `GET` | `/merchant/{id}/churn` | Churn probability and retention breakdown |
| `GET` | `/merchant/{id}/root-cause` | Root cause diagnostics & anomaly analysis |
| `POST` | `/simulate` | Digital twin simulation under parameter shifts |
| `GET` | `/action-plan/{id}` | 30-day tactical operational roadmap |
| `GET` | `/decision/{id}` | Automated underwriting decision & policy rationale |
| `GET` | `/executive-report/{id}` | Investor-grade structured executive brief |
| `GET` | `/merchant/{id}/pdf` | Downloads dynamic vector PDF executive report |
| `GET` | `/agent-traces/{id}` | Telemetry traces & execution latencies per agent |
| `GET` | `/copilot/{id}?question=...` | Grounded interactive merchant Q&A copilot |

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory (optional, sensible defaults provided):

```env
# Database Configuration (Defaults to local SQLite fallback if PostgreSQL is unset)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/razormind_ai

# LLM Configuration (Optional - Resilient heuristic fallback is active by default)
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# App Environment
ENVIRONMENT=production
PORT=8000
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check out the [issues page](https://github.com/your-username/razormind-ai/issues).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is distributed under the **MIT License**. See the `LICENSE` file for details.

---

<p align="center">
  <b>Built with precision for the future of Intelligent Merchant Underwriting 🚀</b>
</p>

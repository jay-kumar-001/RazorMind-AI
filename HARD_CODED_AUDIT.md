# HARD_CODED_AUDIT.md

RazorMind AI — hardcoded / fake / placeholder inventory (pre-fix scan).
Severity: **Critical** (wrong underwriting), **High** (demo fakery users will notice), **Medium** (misleading metrics), **Low** (defaults / demo seed).

| File | Line | Why it is hardcoded | Severity | Fix recommendation |
|---|---|---|---|---|
| `backend/auth.py` | 12 | JWT secret `"CHANGE_THIS_TO_LONG_RANDOM_SECRET"` | Critical | Read `SECRET_KEY` from env; fail closed in production |
| `backend/security.py` | 6 | Duplicate hardcoded JWT secret | Critical | Single env-backed secret |
| `backend/app.py` | 53–59 | Health always `"database": "connected"`, `"agents": 14` | High | Ping DB; report live agent/graph status |
| `backend/app.py` | 37–41 | CORS `allow_origins=["*"]` | High | Restrict origins via env |
| `backend/database.py` | 9 | Prints `DATABASE_URL` | High | Remove credential logging |
| `backend/routes/traces.py` | 61–67 | Empty merchant traces replaced with **other merchants** | High | Return empty list for that merchant |
| `backend/routes/traces.py` | 101, 115 | `success_rate: 100`, `avg_confidence: 96.0` | High | Compute from stored traces |
| `backend/routes/dashboard.py` | 14–18 | Fake defaults `500`, `92.4`, `74.5` when DB empty | High | Return zeros / explicit empty state |
| `database/migrate_csv_to_postgres.py` | 79 | CSV has `retention_rate` not `retention_score` → all get `25.0` | High | Map `retention_rate` → `retention_score` |
| `database/migrate_csv_to_postgres.py` | 145–164 | Same action plan / recs / root cause / 96% for sample IDs | High | Seed from live agents or omit seed prose |
| `agents/*` DefaultMerchant | e.g. `forecast_agent.py` 18–24 | Missing merchant → `120000` / `92.5` / `75` | High | Fail with 404; never invent a healthy merchant |
| `backend/services/forecast_service.py` | 16–42 | Category seasonality tables; volatility bands | Medium | Fit trend on history; label method; real residual bands |
| `backend/routes/forecast.py` | 33–35 | CI fallback `*0.94` / `*1.06`, `trend_slope or 2.1` | Medium | Compute from model or omit |
| `backend/services/risk_service.py` | 80–106 | Fixed recommendation strings by threshold | Medium | Generate from this merchant’s factor breakdown |
| `agents/decision_agent.py` | 29–50 | Fixed score bands + canned rationale; fake confidence | High | Multi-signal policy + data-completeness confidence |
| `agents/action_plan_agent.py` | 50–52, 128 | `+4.5%` revenue, `-8.5` risk points | High | Derive lift from twin / gap-to-benchmark |
| `agents/executive_report_agent.py` | 34, 55 | Hardcoded date `2026-08-27`; `±4.8%` | Medium | `datetime.utcnow`; model interval |
| `agents/rootcause_agent.py` | 85 | `confidence_score: 93.0` always | Medium | Score from evidence strength |
| `agents/kpi_agent.py` | 29–32 | “Percentile” is a linear map, not a rank | Medium | Rank vs portfolio in DB/CSV |
| `backend/services/llm_service.py` | 68–75 | Generic brief if no fallback | Medium | Merchant-specific fallback only |
| `backend/services/churn_service.py` | 80–84 | Binary playbook on `prob > 50` | Medium | Driver-specific playbook |
| `frontend/src/components/RiskTab.jsx` | 126–133 | Fixed 3DS copy, `₹1.4L`, `94.2%` | High | Use `diagnosed_issues` from API |
| `frontend/src/components/ObservabilityTab.jsx` | 54, 65, 75, 167–174 | Fake latency `38`, count `25`, `100%`, placeholder spans | High | Render real traces or empty state |
| `frontend/src/components/OverviewTab.jsx` | 76–79, 89, 116, 135–145 | Fake GMV crore, `↑ 12.4%`, `500`, watchlist `94`, legend `%` | High | Bind dashboard payload only |
| `frontend/src/components/ActionPlanTab.jsx` | 42–47, 68, 79 | Static 4-week cards; `₹1,45,000`; `LOW RISK` | High | Parse agent plan / expected impact / current risk |
| `frontend/src/components/ExecutiveTab.jsx` | 87–114 | Default memo uses `1025350` / `+6.8%` | High | Wait for API; no M0001-shaped defaults |
| `frontend/src/components/DigitalTwinTab.jsx` | 67–68, 202–215 | Local fake health/risk formulas before/without API | High | Show only `result.simulated` after run; debounce live run |
| `frontend/src/components/LangGraphVisualization.jsx` | 3–10 | Static 6 node names | Medium | Drive from execution_trace |
| `frontend/src/App.jsx` | 190–191 | Hardcoded `14 Agents` / `500 Merchants` | Low | Dashboard counts |
| `models/revenue_forecasting.py` | 13 | Script locked to `M0001` | Low | Unused by API; keep as offline lab |
| `simulations/digital_twin_engine.py` | 7 | Script locked to `M0001` | Low | Unused by API |

## Architecture notes (pre-change)

- Core scoring is **rule-based**; LLM is **narrative**.
- LangGraph is a **linear DAG** of the same agents as REST.
- Advisor streaming/history already exist; grounding was incomplete if `MerchantAnalysis` missing.
- `chargeback_rate` exists in CSV but not in risk engine / merchant ORM overlay.

## Improvement roadmap

1. Honest traces (input / output / confidence / latency) — no cross-merchant leak.
2. Merchant snapshot maps `retention_rate`, `chargeback_rate`; no fake default merchant.
3. Forecast: sklearn trend + residual CI + method label.
4. Risk/churn: factor breakdown, feature importance, explanations.
5. Twin: API-driven recs/risk/forecast; UI debounce.
6. PDF + due-diligence + compare + explain-risk + what-changed.
7. Advisor RAG from **live** agent outputs.
8. Performance: merchant cache; graph `fast_mode` (no LLM wait) for pipeline < 5s.

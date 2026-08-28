# Audit Verification Report

| Previous finding | Status | Verification |
| --- | --- | --- |
| Hardcoded forecast values | Fixed | Live `ForecastService` projects from merchant metrics and returns statistical bounds. Legacy experiment remains unused. |
| Hardcoded recommendations | Partially Fixed | Risk/recommendation services use data-triggered recommendations; some policy text is deliberately templated. |
| Hardcoded merchant outputs | Fixed | Merchant context is loaded from ORM/seeded dataset with CSV enrichment, not fixed route payloads. |
| Hardcoded thresholds | Partially Fixed | Thresholds remain explicit underwriting policy bands. They are transparent, but not externally calibrated/configured. |
| Static decision logic | Partially Fixed | Decisions respond to risk, trend, and churn, but are explainable rules rather than a trained underwriting model. |
| Fake telemetry | Partially Fixed | Runtime, status, reasoning, confidence, and source metrics are persisted. Provider token use/dependency telemetry is incomplete. |
| Placeholder secrets | Partially Fixed | JWT code no longer falls back to the placeholder secret. The current environment still needs `SECRET_KEY` set. |
| Duplicate logic | Partially Fixed | Shared merchant-context services reduce duplication; duplicate auth/security configuration and legacy modules remain. |
| Incomplete executive reporting | Partially Fixed | API report contains data-grounded revenue, forecast, risk, recommendations, decision, and confidence. Churn/root-cause/action-plan need first-class report sections. |
| Rule outputs presented as AI | Partially Fixed | Models/policy names and source metrics are exposed, but product copy should more consistently distinguish model inference from policy logic. |
| CSV replacing ML inference | Partially Fixed | Churn model is loaded for inference; CSV is used as a fallback/enrichment source. Forecast is statistical rather than a persisted trained model. |
| Unfinished modules | Partially Fixed | Copilot UI and intelligence APIs are substantial; vector RAG, calibrated underwriting, and production observability remain unfinished. |

# Improvement Plan

1. **Secure deployment:** set `SECRET_KEY`, restrict CORS by environment, add upload size/content validation, and add route-level authorization tests.
2. **Model governance:** version training data/models, add calibration and drift checks, externalize policy bands, and clearly label policy vs ML outputs.
3. **Grounded advisor:** index persisted analyses/reports/action plans with embeddings and cite retrieved records in responses.
4. **Reporting:** add churn, root-cause, action-plan, source freshness, and confidence methodology to the executive report/PDF.
5. **Observability/performance:** capture provider token/latency/error events, add correlation IDs, cache safe read paths, and split the frontend bundle.
6. **Test hardening:** add API contract tests, data-sensitivity tests (mutating inputs changes outputs), authentication tests, and a mocked Copilot integration test.

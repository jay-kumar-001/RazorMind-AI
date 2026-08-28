# Remaining Risks

- Missing `SECRET_KEY` currently prevents protected auth flows, as intended.
- Copilot's end-to-end test needs a reachable LLM or a deterministic mocked-provider test.
- Policy thresholds are not calibrated against a labeled underwriting outcome dataset.
- The transaction fraud path is rule based; it must be labelled accordingly or replaced with an evaluated model.
- Historical/vector RAG, full token telemetry, and automated regression/security tests are incomplete.

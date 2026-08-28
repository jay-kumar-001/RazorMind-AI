# Performance Improvements

- Existing TTL caches are used for merchant, risk, and forecast reads.
- Build verification identified a 812 kB uncompressed JavaScript entry chunk; code splitting is the next priority.
- Copilot response latency is dependent on local/cloud LLM availability and should be measured with provider telemetry.

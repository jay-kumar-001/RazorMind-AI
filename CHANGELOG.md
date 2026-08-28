# Changelog

## Current audit pass

- Repaired backend startup by importing the registered transaction router.
- Removed unsafe JWT placeholder-secret fallbacks; token operations now require environment configuration.
- Replaced fixed KPI confidence with data-completeness/sample-size confidence.
- Removed live endpoint confidence/risk fallback values that could disguise missing analysis.
- Prevented the executive UI from presenting a fabricated report when no server report exists.
- Preserved feature-bearing changes already present in the working tree and verified backend/frontend build paths.

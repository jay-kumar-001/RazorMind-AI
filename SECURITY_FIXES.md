# Security Fixes

- JWT signing/verification no longer silently uses `CHANGE_THIS_TO_LONG_RANDOM_SECRET`.
- Configure a high-entropy `SECRET_KEY` outside source control before enabling authentication routes.

Remaining: restrict permissive CORS, validate uploads by size/content, and add authorization coverage to sensitive merchant data routes.

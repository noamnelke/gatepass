# Roadmap

## Reliability & Performance
- **SQLite concurrency settings**
  - Issue: No busy timeout; concurrent writes can fail under load.
  - Fix: Use `sqlite3.connect(..., timeout=5)` and enable WAL mode on init.
  - Tradeoff: Slightly more disk churn; better concurrency.

- **Error handling in login flows**
  - Issue: Login page reloads after auth without showing errors; index has a TODO for unauthorized.
  - Fix: Surface explicit error messages and handle “not validated” separately.
  - Tradeoff: Minor UI work; clearer UX.

# Roadmap

## Registration Token Design
- **Move to longer, URL-friendly tokens**
  - Issue: Current token is only 5 chars and easily brute‑forced.
  - Fix: Use a longer, random base64url token (e.g., 16–24 chars) with an HMAC or random stored token.
  - Tradeoff: Longer URLs but still shareable; better resistance to guessing.

- **Keep time-bounded validity**
  - Issue: Token expiry is enforced, but no rate-limiting on validation.
  - Fix: Keep hour‑based expiry and add basic rate limits per IP for `/validate-token` and `/register`.
  - Tradeoff: Adds state or middleware; reduces spam attempts.

- **Assumption check: tokens grant validated access**
  - If tokens are intended to grant immediate validated access, keep `validated=1` at registration. If not, switch to `validated=0` and require admin approval.

## Reliability & Performance
- **SQLite concurrency settings**
  - Issue: No busy timeout; concurrent writes can fail under load.
  - Fix: Use `sqlite3.connect(..., timeout=5)` and enable WAL mode on init.
  - Tradeoff: Slightly more disk churn; better concurrency.

- **Error handling in login flows**
  - Issue: Login page reloads after auth without showing errors; index has a TODO for unauthorized.
  - Fix: Surface explicit error messages and handle “not validated” separately.
  - Tradeoff: Minor UI work; clearer UX.

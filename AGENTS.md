# Repository Guidelines

## Project Structure & Module Organization
- `app/` contains the Flask application package, including routes (`app/routes.py`), database helpers (`app/models.py`), token utilities (`app/reg_tokens.py`), templates (`app/templates/`), and static assets (`app/static/`).
- Top-level entry point is `run.py` (app factory + SSL) for local dev.
- Configuration lives in `config.py`; local state uses `passkeys.db` (SQLite).

## Build, Test, and Development Commands
- `python -m venv venv` and `source venv/bin/activate` to set up a virtualenv.
- `pip install -r requirements.txt` to install dependencies.
- `flask run` to start the app (uses Flask defaults; see SSL setup below).
- `python run.py` to run with SSL using `cert.pem` and `key.pem`.
- `openssl req -x509 -nodes -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -config openssl.cnf` to create local SSL certs for passkey testing.

## Coding Style & Naming Conventions
- Python: follow PEP 8 with 4-space indentation; use `snake_case` for functions/variables and `UPPER_CASE` for constants in `config.py`.
- Templates: keep HTML in `app/templates/` and reference static assets via `app/static/`.
- Logging: use `logging` as in `app/routes.py` for request-level events and errors.

## Testing Guidelines
- No automated tests are currently present. If you add tests, place them under a `tests/` directory and document the command in this file.

## Commit & Pull Request Guidelines
- Recent commits use short, imperative, lowercase messages (e.g., “add background image”). Follow that style unless agreed otherwise.
- PRs should describe the user-facing change, reference any related issues, and include screenshots for template/CSS updates.

## Security & Configuration Tips
- Passkeys require SSL and a local domain. Add `127.0.0.1 gatepass.local` to `/etc/hosts`, generate certs, and trust them locally.
- Use `SECRET_KEY`, `RP_ID`, and `ORIGIN` env vars to override defaults in `config.py`.

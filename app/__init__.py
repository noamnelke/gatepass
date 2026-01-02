import secrets

from flask import Flask, session

from config import Config


def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    from . import models
    models.init_db()

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        return {"csrf_token": session["csrf_token"]}

    return app

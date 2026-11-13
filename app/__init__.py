"""Mini-VulnFinBot: a small, security-minded Flask application."""
import logging

from flask import Flask, jsonify

MAX_MESSAGE_LENGTH = 1000
MAX_REQUEST_BYTES = 16 * 1024


def create_app(config=None):
    app = Flask(__name__)
    app.config["MAX_MESSAGE_LENGTH"] = MAX_MESSAGE_LENGTH
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES
    if config:
        app.config.update(config)

    logging.basicConfig(level=logging.INFO)

    from .routes import bp

    app.register_blueprint(bp)
    _register_error_handlers(app)
    _register_security_headers(app)
    return app


def _register_error_handlers(app):
    """Return generic JSON errors. Never expose stack traces or internals."""

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(413)
    def too_large(_e):
        return jsonify(error="Request body too large"), 413

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify(error="Internal server error"), 500


def _register_security_headers(app):
    @app.after_request
    def add_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'"
        )
        return response

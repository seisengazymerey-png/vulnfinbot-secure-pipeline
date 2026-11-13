import logging

from flask import Blueprint, current_app, jsonify, request

from .assistant import generate_response

bp = Blueprint("main", __name__)
log = logging.getLogger(__name__)


@bp.get("/")
def index():
    return jsonify(service="Mini-VulnFinBot", endpoints=["/health", "/api/chat"])


@bp.get("/health")
def health():
    return jsonify(status="healthy")


@bp.post("/api/chat")
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    if "message" not in data:
        return jsonify(error="Field 'message' is required"), 400

    message = data["message"]
    if not isinstance(message, str):
        return jsonify(error="Field 'message' must be a string"), 400

    message = message.strip()
    if not message:
        return jsonify(error="Field 'message' must not be empty"), 400

    max_len = current_app.config["MAX_MESSAGE_LENGTH"]
    if len(message) > max_len:
        return jsonify(error=f"Message is too long (max {max_len} characters)"), 400

    # Log only metadata, never the user's text (it may contain sensitive data).
    log.info("chat request received, length=%d", len(message))

    return jsonify(response=generate_response(message)), 200

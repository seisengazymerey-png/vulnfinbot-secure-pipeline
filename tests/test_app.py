import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "healthy"}


def test_successful_chat_request(client):
    r = client.post("/api/chat", json={"message": "How can I manage my monthly budget?"})
    assert r.status_code == 200
    assert "response" in r.get_json()


def test_empty_message_rejected(client):
    r = client.post("/api/chat", json={"message": "   "})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_missing_message_rejected(client):
    r = client.post("/api/chat", json={"text": "hello"})
    assert r.status_code == 400


def test_invalid_json_handled(client):
    r = client.post("/api/chat", data="{not json", content_type="application/json")
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_wrong_content_type_handled(client):
    r = client.post("/api/chat", data="message=hi", content_type="text/plain")
    assert r.status_code == 400


def test_excessively_long_message_rejected(client):
    r = client.post("/api/chat", json={"message": "a" * 1001})
    assert r.status_code == 400


def test_message_at_limit_accepted(client):
    r = client.post("/api/chat", json={"message": "a" * 1000})
    assert r.status_code == 200


@pytest.mark.parametrize("bad", [123, 1.5, True, None, ["x"], {"a": 1}])
def test_unexpected_input_type_handled(client, bad):
    r = client.post("/api/chat", json={"message": bad})
    assert r.status_code == 400


def test_non_object_json_rejected(client):
    r = client.post("/api/chat", json=["message"])
    assert r.status_code == 400


def test_oversized_body_rejected(client):
    r = client.post("/api/chat", json={"message": "a" * 50000})
    assert r.status_code == 413


def test_unknown_route_returns_json_without_internals(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.get_json() == {"error": "Not found"}


def test_method_not_allowed_is_json(client):
    r = client.get("/api/chat")
    assert r.status_code == 405
    assert "error" in r.get_json()


def test_security_headers_present(client):
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in r.headers


def test_internal_errors_do_not_leak_details():
    app = create_app({"TESTING": False, "PROPAGATE_EXCEPTIONS": False})

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    r = app.test_client().get("/boom")
    assert r.status_code == 500
    assert "secret internal detail" not in r.get_data(as_text=True)
    assert "Traceback" not in r.get_data(as_text=True)

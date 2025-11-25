import importlib
import json
import os
import sys
import pytest


@pytest.fixture
def clear_input_module():
    # Ensure a clean import of the target module each time
    if "input" in sys.modules:
        del sys.modules["input"]
    yield
    if "input" in sys.modules:
        del sys.modules["input"]


def _import_app(monkeypatch, env_overrides=None):
    env_overrides = env_overrides or {}
    for k, v in env_overrides.items():
        monkeypatch.setenv(k, v)
    # Remove keys not set to avoid leaking from host
    for key in ["USERS_JSON", "ALICE_PASSWORD", "CSRF_TOKEN", "CSRF_TRUSTED_ORIGINS"]:
        if key not in env_overrides:
            monkeypatch.delenv(key, raising=False)
    return importlib.import_module("input")


@pytest.fixture
def app_default(clear_input_module, monkeypatch):
    # No USERS_JSON/ALICE_PASSWORD so default user path is exercised
    mod = _import_app(monkeypatch, env_overrides={})
    return mod


@pytest.fixture
def app_with_bob(clear_input_module, monkeypatch):
    users_json = json.dumps({"bob": "Password1!"})
    mod = _import_app(
        monkeypatch,
        env_overrides={
            "USERS_JSON": users_json,
            "CSRF_TOKEN": "TEST_CSRF_TOKEN",
        },
    )
    return mod


def test_default_password_not_usable(app_default):
    app = app_default.app
    client = app.test_client()

    # Obtain server-side CSRF token (generated on import)
    csrf_token = getattr(app_default, "CSRF_TOKEN", None)

    resp = client.post(
        "/login",
        json={"username": "alice", "password": "ChangeThisPassword!123"},
        headers={"X-CSRF-Token": csrf_token} if csrf_token else None,
    )
    assert resp.status_code == 401, (
        "Default hardcoded password must not authenticate the demo user 'alice'."
    )


def test_csrf_required_for_post_login(app_with_bob):
    app = app_with_bob.app
    client = app.test_client()

    # Missing CSRF token should be rejected
    resp = client.post(
        "/login",
        json={"username": "bob", "password": "Password1!"},
    )
    assert resp.status_code == 403, "POST /login must enforce CSRF protection"


def test_login_success_with_csrf(app_with_bob):
    app = app_with_bob.app
    client = app.test_client()

    resp = client.post(
        "/login",
        json={"username": "bob", "password": "Password1!"},
        headers={"X-CSRF-Token": "TEST_CSRF_TOKEN"},
    )
    assert resp.status_code == 200
    assert resp.get_json().get("status") == "login ok"


def test_security_headers_present(app_with_bob):
    app = app_with_bob.app
    client = app.test_client()

    resp = client.get("/greet?name=world")

    expected_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
    }
    for header, expected in expected_headers.items():
        assert resp.headers.get(header) == expected, f"Missing security header {header}"

    csp = resp.headers.get("Content-Security-Policy")
    assert csp and "default-src 'self'" in csp, "CSP header must be set"

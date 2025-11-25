import importlib
import os
import pickle
import sys
import types
import inspect

import pytest


def reload_input(monkeypatch, env=None):
    # Ensure fresh import reflects env changes
    sys.modules.pop('input', None)
    if env:
        for k, v in env.items():
            monkeypatch.setenv(k, v)
    import input  # noqa
    return importlib.reload(input)


def test_api_key_from_env(monkeypatch):
    module = reload_input(monkeypatch, {"API_KEY": "TEST_KEY"})
    assert module.API_KEY == "TEST_KEY"
    # Ensure no hardcoded pattern remains
    assert module.API_KEY is not None
    assert "AKIA_EXAMPLE" not in str(module.API_KEY)


def test_secret_key_from_env(monkeypatch):
    module = reload_input(monkeypatch, {"FLASK_SECRET_KEY": "s3cr3t"})
    assert module.app.config["SECRET_KEY"] == "s3cr3t"


def test_query_users_parameterized(monkeypatch):
    module = reload_input(monkeypatch)

    class FakeCursor:
        def __init__(self):
            self.sql = None
            self.params = None

        def execute(self, sql, params=None):
            self.sql = sql
            self.params = params

        def fetchall(self):
            return []

    class FakeConn:
        def __init__(self):
            self.cursor_obj = FakeCursor()

        def cursor(self):
            return self.cursor_obj

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_conn = FakeConn()
    # Patch the sqlite3.connect used by the module
    module.sqlite3 = types.SimpleNamespace(connect=lambda _: fake_conn)

    module.query_users_by_name("foo")
    assert fake_conn.cursor_obj.sql is not None
    assert "?" in fake_conn.cursor_obj.sql
    assert fake_conn.cursor_obj.params == ("%foo%",)
    # Ensure raw input isn't injected into SQL string
    assert "foo" not in fake_conn.cursor_obj.sql


def test_upload_profile_rejects_pickle(monkeypatch):
    module = reload_input(monkeypatch)
    client = module.app.test_client()
    payload = pickle.dumps({"name": "Bob"})
    resp = client.post("/upload_profile", data=payload, content_type="application/octet-stream")
    assert resp.status_code == 400


def test_upload_profile_accepts_json(monkeypatch):
    module = reload_input(monkeypatch)
    client = module.app.test_client()
    resp = client.post("/upload_profile", json={"name": "Bob"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Bob"


def test_run_command_whitelist(monkeypatch):
    module = reload_input(monkeypatch)
    client = module.app.test_client()

    resp_ok = client.post("/run", data={"cmd": "status"})
    assert resp_ok.status_code == 200
    assert resp_ok.get_json()["output"] == "status ok"

    resp_denied = client.post("/run", data={"cmd": "ls"})
    assert resp_denied.status_code == 400


def test_greet_escapes_html(monkeypatch):
    module = reload_input(monkeypatch)
    client = module.app.test_client()
    resp = client.get("/greet", query_string={"name": "<script>alert(1)</script>"})
    data = resp.get_data(as_text=True).lower()
    assert "<script>" not in data
    assert "&lt;script&gt;" in data


def test_password_is_hashed(monkeypatch):
    module = reload_input(monkeypatch)
    hashed = module.USERS["alice"]["password"]
    assert hashed != "password123"
    assert module.check_password_hash(hashed, "password123")


def test_no_debug_true_literal():
    with open("input.py", "r", encoding="utf-8") as f:
        source = f.read().replace(" ", "")
    assert "debug=True" not in source

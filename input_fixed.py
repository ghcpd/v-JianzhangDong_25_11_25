from flask import Flask, request, render_template_string, jsonify
import sqlite3
import os
import json
import secrets
import hmac
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Load sensitive configuration (e.g., API keys) from environment variables
API_KEY = os.environ.get("API_KEY")


def query_users_by_name(name: str):
    """Look up users by name safely using parameterized queries."""
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        # Parameterized query to prevent SQL injection
        sql = "SELECT id, username FROM users WHERE username LIKE ?"
        cur.execute(sql, (f"%{name}%",))
        rows = cur.fetchall()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    """Accept JSON profile payload instead of unsafe pickle deserialization."""
    profile = request.get_json(silent=True)
    if not isinstance(profile, dict):
        return jsonify({"error": "Invalid profile payload; expected JSON object."}), 400
    name = profile.get("name")
    return jsonify({"status": "ok", "name": name})


@app.route('/run', methods=['POST'])
def run_command():
    """Provide a safe, whitelisted set of actions instead of executing shell commands."""
    action = request.form.get('action') or (request.json or {}).get('action') if request.is_json else None
    allowed_actions = {
        "ping": lambda: {"status": "ok", "message": "pong"},
    }
    if action not in allowed_actions:
        return jsonify({"error": "Action not allowed"}), 400
    result = allowed_actions[action]()
    return jsonify(result)


@app.route('/greet')
def greet():
    name = request.args.get('name', 'guest')
    # Use Jinja templating with auto-escaping
    template = "<h1>Hello {{ name }}</h1>"
    return render_template_string(template, name=name)


def _load_users():
    """Load users from JSON env var USERS_JSON or fall back to a secure default hash."""
    users_json = os.environ.get("USERS_JSON")
    if users_json:
        try:
            raw_users = json.loads(users_json)
            users = {}
            for uname, pwd in raw_users.items():
                # If passwords are provided in plaintext, hash them on startup
                if pwd.startswith("pbkdf2:"):
                    users[uname] = {"password_hash": pwd}
                else:
                    users[uname] = {"password_hash": generate_password_hash(pwd)}
            return users
        except Exception:
            app.logger.exception("Failed to parse USERS_JSON; falling back to default user")
    # Default demo user (password should be overridden via USERS_JSON or ALICE_PASSWORD env var)
    default_pwd = os.environ.get("ALICE_PASSWORD")
    if default_pwd is None:
        # Generate an ephemeral strong password and DO NOT log it to avoid leaking credentials
        default_pwd = secrets.token_urlsafe(16)
        app.logger.warning(
            "ALICE_PASSWORD not set; generated ephemeral password for alice. "
            "Set USERS_JSON or ALICE_PASSWORD to provide deterministic credentials."
        )
    return {
        "alice": {"password_hash": generate_password_hash(default_pwd)}
    }


USERS = _load_users()

# CSRF protection settings
CSRF_TOKEN = os.environ.get("CSRF_TOKEN") or secrets.token_urlsafe(32)
CSRF_TRUSTED_ORIGINS = {o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o}
CSRF_EXEMPT_PATHS = {"/greet"}


@app.before_request
def enforce_csrf():
    """Lightweight CSRF protection for state-changing requests.

    Accepts either a shared secret via X-CSRF-Token/Form/JSON or validates Origin/Referer.
    """
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return None
    if request.path in CSRF_EXEMPT_PATHS:
        return None

    # 1) Token-based check (preferred)
    token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
    if request.is_json and token is None:
        token = (request.json or {}).get("csrf_token")
    if token is not None:
        if not hmac.compare_digest(str(token), str(CSRF_TOKEN)):
            return jsonify({"error": "Invalid CSRF token"}), 403
        return None

    # 2) Origin/Referer fallback check
    origin = request.headers.get("Origin") or request.headers.get("Referer")
    if origin:
        origin_host = urlparse(origin).hostname
        request_host = urlparse(request.host_url).hostname
        if origin_host == request_host or origin in CSRF_TRUSTED_ORIGINS or origin_host in CSRF_TRUSTED_ORIGINS:
            return None

    return jsonify({"error": "CSRF token required"}), 403


@app.after_request
def add_security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    resp.headers.setdefault("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'; object-src 'none'")
    # Apply HSTS only when served over HTTPS
    if request.scheme == "https":
        resp.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
    return resp

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username') or (request.json or {}).get('username') if request.is_json else None
    password = request.form.get('password') or (request.json or {}).get('password') if request.is_json else None
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400
    user = USERS.get(username)
    if user and check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"status": "login ok"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    # Debug mode controlled via environment variable only
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=debug)

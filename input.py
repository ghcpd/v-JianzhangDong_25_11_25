from flask import Flask, request, render_template_string, jsonify
import sqlite3
import os
import secrets
import subprocess
import sys
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Load secrets from environment; avoid hardcoding
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or os.environ.get('SECRET_KEY') or secrets.token_hex(16)

# External API key must be injected via environment
API_KEY = os.environ.get("API_KEY")


def query_users_by_name(name):
    # Parameterized query to prevent SQL injection
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        pattern = f"%{name}%"
        cur.execute("SELECT id, username FROM users WHERE username LIKE ?", (pattern,))
        rows = cur.fetchall()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    # Accept JSON only; reject unsafe pickle payloads
    profile = request.get_json(silent=True)
    if not isinstance(profile, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400
    name = profile.get("name")
    return jsonify({"status": "ok", "name": name}), 200


@app.route('/run', methods=['POST'])
def run_command():
    cmd = request.form.get('cmd', '')
    # Whitelist allowed commands to avoid injection
    ALLOWED_COMMANDS = {
        "status": [sys.executable, "-c", "print('status ok')"],
    }
    if cmd not in ALLOWED_COMMANDS:
        return jsonify({"error": "Command not allowed"}), 400
    result = subprocess.run(ALLOWED_COMMANDS[cmd], capture_output=True, text=True)
    return jsonify({"status": "ok", "output": result.stdout.strip()}), 200


@app.route('/greet')
def greet():
    name = request.args.get('name', 'guest')
    # Render with Jinja autoescaping
    template = "<h1>Hello {{ name }}</h1>"
    return render_template_string(template, name=name)


USERS = {
    "alice": {"password": generate_password_hash("password123")},
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = USERS.get(username)
    if user and check_password_hash(user.get("password"), password):
        return "login ok"
    return "login failed"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

from flask import Flask, request, render_template_string, jsonify, abort
import sqlite3
import os
import json
import subprocess
import shlex
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


API_KEY = os.environ.get('API_KEY')  # Read API_KEY from environment; no hardcoded keys
SECRET_KEY = os.environ.get('SECRET_KEY')  # Flask secret key should be set from env


def query_users_by_name(name):
    # Prevent SQL injection by using parameterized queries and limiting input length
    if not isinstance(name, str) or len(name) > 200:
        return []
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE username LIKE ?", (f"%{name}%",))
    rows = cur.fetchall()
    conn.close()
    return [(r['id'], r['username']) for r in rows]


@app.route('/search')
def search_users():
    name = request.args.get('name', '')
    rows = query_users_by_name(name)
    return jsonify([{"id": r[0], "username": r[1]} for r in rows])


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    # Accept only JSON, do not deserialize pickle data.
    try:
        profile = request.get_json(force=True)
    except Exception:
        abort(400, "Invalid JSON profile")
    if not isinstance(profile, dict):
        abort(400, "Invalid profile format")
    name = profile.get('name')
    if not isinstance(name, str) or len(name) > 200:
        abort(400, "Invalid name")
    return jsonify({"status": "ok", "name": name})


@app.route('/run', methods=['POST'])
def run_command():
    # Avoid running untrusted user commands in shell
    cmd = request.form.get('cmd', '')
    if not isinstance(cmd, str) or len(cmd) > 300:
        abort(400, "Invalid cmd")
    # Execute only in a safe manner (no shell=True). Here we do NOT execute arbitrary shells, we only echo safely.
    # This ensures command injection is not possible.
    safe_output = f"Running: {cmd}"
    # We can simulate / log the command rather than executing it, or execute safe commands if needed.
    return safe_output


@app.route('/greet')
def greet():
    name = request.args.get('name', 'guest')
    # Use Jinja template variable to ensure escaping is applied
    template = "<h1>Hello {{ name }}</h1>"
    return render_template_string(template, name=name)


# Use hashed passwords and initialize DB entry in startup
USERS = {}


def init_users():
    # Initialize a default user if not present in file. Store hashed password only.
    default_password = os.environ.get('DEFAULT_PASSWORD')
    if default_password is None:
        # Generate a random default password if not provided; do not hardcode secrets
        import secrets
        default_password = secrets.token_urlsafe(12)
    if 'alice' not in USERS:
        USERS['alice'] = {'password_hash': generate_password_hash(default_password)}


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = USERS.get(username)
    if user and check_password_hash(user.get('password_hash', ''), password):
        return "login ok"
    return "login failed"

def init_db():
    # Create users.db and insert sample user if it doesn't exist
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT)''')
    # Ensure alice exists in DB
    cur.execute('SELECT id FROM users WHERE username = ?', ('alice',))
    if cur.fetchone() is None:
        default_password = os.environ.get('DEFAULT_PASSWORD')
        if default_password is None:
            import secrets
            default_password = secrets.token_urlsafe(12)
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('alice', generate_password_hash(default_password)))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_users()
    init_db()
    app.run(debug=os.environ.get('DEBUG', 'False').lower() == 'true')

from flask import Flask, request, render_template_string, jsonify, abort
import sqlite3
import os
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)


# API keys and secrets must come from the environment. Do not hardcode.
API_KEY = os.getenv('APP_API_KEY')


DB_PATH = os.getenv('DB_PATH', 'users.db')


def query_users_by_name(name):
    # Use parameterized query to prevent SQL injection.
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    sql = "SELECT id, username FROM users WHERE username LIKE ?"
    cur.execute(sql, (f"%{name}%",))
    rows = cur.fetchall()
    conn.close()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    # Accept only JSON here — do not unpickle or eval raw user input
    try:
        profile = request.get_json(force=True)
    except Exception:
        abort(400, "invalid json payload")

    if not isinstance(profile, dict):
        abort(400, "expected object payload")

    name = profile.get('name')
    # Return a sanitized response
    return jsonify({"status": "ok", "name": escape(name)})


@app.route('/run', methods=['POST'])
def run_command():
    # Do NOT execute arbitrary shell commands. Accept only simple safe commands or return an error.
    cmd = (request.form.get('cmd') or '').strip()
    if not cmd:
        abort(400, 'no command provided')

    # Basic denylist: disallow shell metacharacters to avoid injection or redirection
    for bad in [';', '&', '|', '>', '<', '$', '`']:
        if bad in cmd:
            abort(400, 'forbidden characters in command')

    # For demonstrative purposes: only allow single-word commands from a short whitelist
    allowed = {'ping', 'status', 'echo'}
    parts = cmd.split()
    if parts[0] not in allowed:
        abort(403, 'command not allowed')

    # Implement allowed behaviours without shell execution
    if parts[0] == 'ping':
        return 'pong'
    if parts[0] == 'status':
        return jsonify({'status': 'ok'})
    if parts[0] == 'echo':
        # join the rest and safely return it
        return ' '.join(parts[1:])

    abort(400, 'unknown command')


@app.route('/greet')
def greet():
    name = request.args.get('name', 'guest')
    # Use templating safely — Jinja2 will escape user content by default
    template = "<h1>Hello {{ name }}</h1>"
    return render_template_string(template, name=name)


USERS = {
    # store password hashes instead of plain text (demonstration account)
    "alice": {"password": generate_password_hash('password123')},
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = USERS.get(username)
    if user and check_password_hash(user.get('password', ''), password or ''):
        return "login ok"
    return "login failed"

if __name__ == '__main__':
    # Do not enable debug mode in production
    app.run(debug=False)

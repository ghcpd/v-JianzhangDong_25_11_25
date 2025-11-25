from flask import Flask, request, jsonify
import sqlite3
import os
import json
import subprocess
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# FIXED: Load API_KEY from environment variable instead of hardcoding
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError('API_KEY environment variable not set')


def query_users_by_name(name):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # FIXED: Use parameterized query to prevent SQL injection
    sql = "SELECT id, username FROM users WHERE username LIKE ?"
    cur.execute(sql, ('%' + name + '%',))
    rows = cur.fetchall()
    conn.close()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    # FIXED: Use JSON deserialization instead of unsafe pickle.loads()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        profile = data
        return jsonify({"status": "ok", "name": profile.get("name")})
    except Exception as e:
        return jsonify({"error": "Failed to process profile"}), 400


@app.route('/run', methods=['POST'])
def run_command():
    cmd = request.form.get('cmd', '')
    # FIXED: Use subprocess with shell=False to prevent OS command injection
    try:
        result = subprocess.run(['echo', 'Running:', cmd], 
                              shell=False, 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        return jsonify({"status": "done", "output": result.stdout})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timeout"}), 500
    except Exception as e:
        return jsonify({"error": "Command execution failed"}), 500


@app.route('/greet')
def greet():
    name = request.args.get('name', 'guest')
    # FIXED: Escape user input to prevent XSS
    safe_name = escape(name)
    return f"<h1>Hello {safe_name}</h1>"


# FIXED: Use hashed passwords instead of plain text
USERS = {
    "alice": {"password": generate_password_hash("secure_pass_123")},
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = USERS.get(username)
    if user and check_password_hash(user.get("password"), password):
        return jsonify({"status": "login ok"})
    return jsonify({"status": "login failed"}), 401

if __name__ == '__main__':
    # FIXED: Control debug mode via environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)

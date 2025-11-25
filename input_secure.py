from flask import Flask, request, render_template_string, jsonify
import sqlite3
import os
import json
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import re
import logging

app = Flask(__name__)

# Security: Load API key from environment variable instead of hardcoding
API_KEY = os.environ.get('API_KEY', None)
if not API_KEY:
    logging.warning("API_KEY not set in environment variables")

# Configure secure session key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

def query_users_by_name(name):
    """
    Fixed: Use parameterized queries to prevent SQL injection
    """
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # Use parameterized query instead of string formatting
    sql = "SELECT id, username FROM users WHERE username LIKE ?"
    cur.execute(sql, ('%' + name + '%',))
    rows = cur.fetchall()
    conn.close()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    """
    Fixed: Use JSON instead of pickle to prevent remote code execution
    """
    try:
        data = request.data
        # Use JSON instead of pickle for safe deserialization
        profile = json.loads(data)
        # Validate the profile structure
        if not isinstance(profile, dict):
            return jsonify({"status": "error", "message": "Invalid profile format"}), 400
        # Sanitize and validate expected fields
        name = profile.get("name", "")
        if not isinstance(name, str) or len(name) > 100:
            return jsonify({"status": "error", "message": "Invalid name"}), 400
        return jsonify({"status": "ok", "name": name})
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400


@app.route('/run', methods=['POST'])
def run_command():
    """
    Fixed: Removed command execution capability entirely
    Alternative: Use whitelist of allowed commands if needed
    """
    cmd = request.form.get('cmd', '')
    # Instead of executing arbitrary commands, use a whitelist approach
    allowed_commands = {
        'status': lambda: 'System status: OK',
        'info': lambda: 'System info available',
    }
    
    if cmd in allowed_commands:
        result = allowed_commands[cmd]()
        return jsonify({"status": "ok", "result": result})
    else:
        return jsonify({"status": "error", "message": "Command not allowed"}), 403


@app.route('/greet')
def greet():
    """
    Fixed: Use Jinja2's autoescaping instead of render_template_string with user input
    """
    name = request.args.get('name', 'guest')
    # Validate and sanitize input
    # Remove any HTML/script tags to prevent XSS
    name = re.sub(r'[<>]', '', name)
    # Limit length
    name = name[:50]
    # Use Jinja2 with autoescaping enabled (default in Flask)
    template = "<h1>Hello {{ name }}</h1>"
    return render_template_string(template, name=name)


# Security: Use hashed passwords instead of plaintext
# In production, use a proper database and password hashing
USERS = {
    "alice": {
        # This is a hash of "SecurePassword123!" - in production, load from secure database
        "password_hash": generate_password_hash("SecurePassword123!")
    },
}

@app.route('/login', methods=['POST'])
def login():
    """
    Fixed: Use password hashing instead of plaintext comparison
    """
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Input validation
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400
    
    user = USERS.get(username)
    if user and check_password_hash(user.get("password_hash"), password):
        return jsonify({"status": "success", "message": "Login successful"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


if __name__ == '__main__':
    # Security: Disable debug mode in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)

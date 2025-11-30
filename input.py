from flask import Flask, request, render_template_string, jsonify
import sqlite3
import os
import json
import logging
import re
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SECURITY FIX (VULN-005): Load API key from environment variable instead of hardcoding
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    logger.warning("API_KEY environment variable not set")


def query_users_by_name(name):
    # SECURITY FIX (VULN-001): Use parameterized queries to prevent SQL injection
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # Use parameterized query with placeholders
    sql = "SELECT id, username FROM users WHERE username LIKE ?"
    cur.execute(sql, ('%' + name + '%',))
    rows = cur.fetchall()
    conn.close()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    # SECURITY FIX (VULN-002): Use JSON instead of pickle to prevent RCE
    data = request.data
    try:
        profile = json.loads(data.decode('utf-8'))
        # Validate that profile is a dictionary
        if not isinstance(profile, dict):
            return jsonify({"error": "Invalid format, expected JSON object"}), 400
        # Validate expected fields
        if 'name' not in profile:
            return jsonify({"error": "Missing required field: name"}), 400
        # Sanitize the name field
        name = str(profile.get("name", ""))[:100]  # Limit length
        return jsonify({"status": "ok", "name": name})
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Invalid JSON in upload_profile: {e}")
        return jsonify({"error": "Invalid JSON format"}), 400


@app.route('/run', methods=['POST'])
def run_command():
    # SECURITY FIX (VULN-003): Never execute user input as shell commands
    cmd = request.form.get('cmd', '')
    # Validate input - only allow alphanumeric and spaces
    if not cmd or not re.match(r'^[a-zA-Z0-9\s]+$', cmd):
        logger.warning(f"Invalid command format rejected: {cmd}")
        return jsonify({"error": "Invalid command format"}), 400
    # Log the command instead of executing it
    logger.info(f"Command request received (not executed): {cmd}")
    return jsonify({"status": "Command logged", "command": cmd})


@app.route('/greet')
def greet():
    # SECURITY FIX (VULN-004): Use proper template variable substitution with auto-escaping
    name = request.args.get('name', 'guest')
    # Escape user input to prevent SSTI
    safe_name = escape(name)
    # Use Jinja2 variable substitution instead of string formatting
    template = "<h1>Hello {{ name }}</h1>"
    return render_template_string(template, name=safe_name)


# SECURITY FIX (VULN-006): Use hashed passwords instead of plaintext
# In production, this should be stored in a secure database
USERS = {
    "alice": {
        "password_hash": generate_password_hash("password123")
    },
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # Input validation
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    user = USERS.get(username)
    # Use secure password comparison with hashed passwords
    if user and check_password_hash(user.get("password_hash", ""), password):
        logger.info(f"Successful login for user: {username}")
        return jsonify({"status": "login ok"})
    
    logger.warning(f"Failed login attempt for user: {username}")
    return jsonify({"error": "login failed"}), 401

if __name__ == '__main__':
    # SECURITY FIX (VULN-007): Disable debug mode in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    # Bind to localhost only by default for security
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    
    if debug_mode:
        logger.warning("Debug mode is enabled - DO NOT use in production!")
    
    app.run(debug=debug_mode, host=host, port=port)

from flask import Flask, request, render_template, jsonify, escape
import sqlite3
import os
import json
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import secrets
import logging

app = Flask(__name__)

# API Key from environment variable (not hardcoded)
API_KEY = os.getenv('API_KEY', secrets.token_urlsafe(32))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def query_users_by_name(name):
    """Query users by name using parameterized queries to prevent SQL injection."""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # Use parameterized query with placeholders
    sql = "SELECT id, username FROM users WHERE username LIKE ?"
    cur.execute(sql, (f'%{name}%',))
    rows = cur.fetchall()
    conn.close()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    """Upload profile using JSON instead of pickle to prevent RCE."""
    try:
        # Use JSON instead of pickle for safer deserialization
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        name = data.get('name', '')
        # Validate name is a string
        if not isinstance(name, str) or len(name) > 255:
            return jsonify({"error": "Invalid name"}), 400
        
        return jsonify({"status": "ok", "name": escape(name)})
    except Exception as e:
        logger.error(f"Error in upload_profile: {e}")
        return jsonify({"error": "Invalid request"}), 400


@app.route('/run', methods=['POST'])
def run_command():
    """Execute safe commands without shell interpretation."""
    cmd = request.form.get('cmd', '')
    
    # Restrict commands to a whitelist of safe operations
    safe_commands = ['echo', 'whoami', 'date']
    cmd_parts = cmd.split()
    
    if not cmd_parts or cmd_parts[0] not in safe_commands:
        return jsonify({"error": "Command not allowed"}), 403
    
    try:
        # Use subprocess.run instead of os.system to prevent shell injection
        import subprocess
        result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=5)
        return jsonify({"output": result.stdout}), 200
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return jsonify({"error": "Command execution failed"}), 500


@app.route('/greet')
def greet():
    """Greet user with properly escaped output."""
    name = request.args.get('name', 'guest')
    # Escape HTML to prevent template injection
    safe_name = escape(name)
    return f"<h1>Hello {safe_name}</h1>"


# Use environment variable for password storage, with hashing
USERS = {
    "alice": {
        "password_hash": os.getenv('DEFAULT_PASSWORD_HASH', 
                                   generate_password_hash('secure_password_123'))
    },
}


@app.route('/login', methods=['POST'])
def login():
    """Authenticate user with hashed password comparison."""
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = USERS.get(username)
    if user and check_password_hash(user.get("password_hash"), password):
        return jsonify({"status": "login ok"}), 200
    return jsonify({"status": "login failed"}), 401


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Disable debug mode in production, use environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1')

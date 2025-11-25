from flask import Flask, request, render_template_string, jsonify, escape
import sqlite3
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Security: Load API key from environment variable, not hardcoded
API_KEY = os.getenv('API_KEY', 'default_insecure_key')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Enable logging for security events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def query_users_by_name(name):
    """Secure database query using parameterized statements"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # SECURE: Use parameterized query to prevent SQL injection
    sql = "SELECT id, username FROM users WHERE username LIKE ?"
    # Use wildcard in Python, not in query
    cur.execute(sql, (f'%{name}%',))
    rows = cur.fetchall()
    conn.close()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    """Secure profile upload using JSON instead of pickle"""
    try:
        # SECURE: Use JSON instead of pickle for deserialization
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid request"}), 400
        
        # Validate and sanitize input
        name = data.get("name", "")
        if not isinstance(name, str) or len(name) > 255:
            return jsonify({"error": "Invalid name"}), 400
        
        # Escape output for safety
        safe_name = escape(name)
        return jsonify({"status": "ok", "name": safe_name})
    except Exception as e:
        logger.error(f"Profile upload error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/run', methods=['POST'])
def run_command():
    """Secure command execution (restricted and sanitized)"""
    cmd = request.form.get('cmd', '')
    
    # SECURE: Whitelist allowed commands instead of executing arbitrary commands
    allowed_commands = ['echo', 'date', 'whoami']
    cmd_parts = cmd.strip().split()
    
    if not cmd_parts or cmd_parts[0] not in allowed_commands:
        return jsonify({"error": "Command not allowed"}), 403
    
    try:
        # SECURE: Use subprocess.run with shell=False to prevent injection
        import subprocess
        result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=5)
        return jsonify({"output": result.stdout})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timeout"}), 500
    except Exception as e:
        logger.error(f"Command execution error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/greet')
def greet():
    """Secure greeting endpoint with proper escaping"""
    name = request.args.get('name', 'guest')
    
    # SECURE: Escape user input to prevent template injection
    safe_name = escape(name)
    
    # Or better, avoid template_string entirely:
    return jsonify({"greeting": f"Hello {safe_name}"})


# SECURE: Store hashed passwords, not plain text
USERS = {
    "alice": {"password_hash": generate_password_hash("password123")},
}


@app.route('/login', methods=['POST'])
def login():
    """Secure authentication with password hashing"""
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate input
        if not username or not password:
            logger.warning(f"Failed login attempt: missing credentials")
            return jsonify({"error": "Missing credentials"}), 400
        
        user = USERS.get(username)
        
        # SECURE: Use constant-time comparison with hashed passwords
        if user and check_password_hash(user.get("password_hash"), password):
            logger.info(f"Successful login for user: {username}")
            return jsonify({"status": "login ok"}), 200
        
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({"error": "Invalid credentials"}), 401
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors securely"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors securely"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # SECURE: Debug should never be True in production
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1')

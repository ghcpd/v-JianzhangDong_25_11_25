from flask import Flask, request, jsonify, escape
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# FIXED: Load API key from environment variable instead of hardcoding
API_KEY = os.environ.get('API_KEY', '')
if not API_KEY:
    # In production, this should raise an error. For testing, we'll allow it to continue
    print("WARNING: API_KEY environment variable is not set")


def query_users_by_name(name):
    """
    FIXED: Use parameterized queries to prevent SQL injection
    """
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # Use parameterized query with ? placeholder
    sql = "SELECT id, username FROM users WHERE username LIKE ?"
    cur.execute(sql, (f'%{name}%',))
    rows = cur.fetchall()
    conn.close()
    return rows


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    """
    FIXED: Use JSON instead of pickle to prevent insecure deserialization
    """
    # Validate content type
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    try:
        profile = request.get_json()
        # Validate that profile is a dict with expected fields
        if not isinstance(profile, dict):
            return jsonify({"error": "Invalid profile format - must be a JSON object"}), 400
        
        if 'name' not in profile:
            return jsonify({"error": "Invalid profile format - 'name' field is required"}), 400
        
        # Additional validation for name field
        name = profile.get("name")
        if not isinstance(name, str) or len(name) > 100:
            return jsonify({"error": "Invalid name - must be a string with max 100 characters"}), 400
            
        return jsonify({"status": "ok", "name": name})
    except Exception as e:
        return jsonify({"error": "Invalid JSON data"}), 400


@app.route('/run', methods=['POST'])
def run_command():
    """
    FIXED: Remove shell command execution, validate input strictly
    """
    cmd = request.form.get('cmd', '')
    
    # Validate input - only allow alphanumeric and basic punctuation
    if not re.match(r'^[a-zA-Z0-9\s.,!?-]+$', cmd):
        return jsonify({"error": "Invalid input - only alphanumeric and basic punctuation allowed"}), 400
    
    # Limit input length
    if len(cmd) > 200:
        return jsonify({"error": "Input too long - max 200 characters"}), 400
    
    # Don't execute shell commands - just return the message safely
    return jsonify({"message": f"Running: {cmd}"})


@app.route('/greet')
def greet():
    """
    FIXED: Use Flask's escape() to prevent template injection and XSS
    """
    name = request.args.get('name', 'guest')
    
    # Validate and limit input length
    if len(name) > 100:
        name = 'guest'
    
    # Use escape to prevent HTML/template injection
    return f"<h1>Hello {escape(name)}</h1>"


# FIXED: Use password hashing instead of plain text passwords
# This is a hashed version of a strong password "SecurePassword123!"
USERS = {
    "alice": {
        "password_hash": generate_password_hash("SecurePassword123!")
    },
}

@app.route('/login', methods=['POST'])
def login():
    """
    FIXED: Use password hashing for authentication
    """
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Input validation
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = USERS.get(username)
    if user and check_password_hash(user.get("password_hash"), password):
        return jsonify({"status": "login ok"})
    
    return jsonify({"error": "login failed"}), 401


if __name__ == '__main__':
    # FIXED: Only enable debug mode in development environment
    # Never run with debug=True in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Bind to localhost only for security (use reverse proxy in production)
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)

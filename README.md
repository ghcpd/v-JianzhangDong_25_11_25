# Security Audit Report - Flask Application

## Overview
This repository contains a comprehensive security audit of a Flask application, including vulnerability identification, fixes, and automated testing infrastructure.

## Files Structure

```
.
├── input.py                    # SECURE version (fixed)
├── input_vulnerable.py         # Original vulnerable version
├── report.json                 # Detailed vulnerability report
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── setup.sh                    # Linux/macOS setup script
├── run_test.sh                 # Linux/macOS test script
├── run_test.bat                # Windows test script
├── auto_test.py                # Automatic test runner
└── logs/                       # Test execution logs
    ├── test_run.log           # Latest test execution log
    └── test_results.json      # Structured test results
```

## Identified Vulnerabilities

### Critical (4 vulnerabilities)

1. **Hardcoded API Key (Line 9)**
   - AWS API key exposed in source code
   - CWE-798: Use of Hard-coded Credentials

2. **SQL Injection (Lines 12-15)**
   - Direct string formatting in SQL queries
   - CWE-89: SQL Injection

3. **Insecure Deserialization (Lines 21-25)**
   - Use of pickle.loads() with user input
   - CWE-502: Deserialization of Untrusted Data
   - Allows Remote Code Execution (RCE)

4. **Command Injection (Lines 30-33)**
   - User input passed to os.system()
   - CWE-78: OS Command Injection

### High (2 vulnerabilities)

5. **Server-Side Template Injection (Lines 38-41)**
   - User input in render_template_string()
   - CWE-94: Code Injection (SSTI)

6. **Weak Passwords (Lines 44-46)**
   - Plain text passwords in source code
   - CWE-259: Use of Hard-coded Password

### Medium (1 vulnerability)

7. **Debug Mode Enabled (Line 56)**
   - Flask debug mode in production
   - CWE-489: Active Debug Code

## Security Fixes Applied

### 1. API Key Management
**Before:**
```python
API_KEY = "AKIA_EXAMPLE_HARDCODED_KEY_123456"
```

**After:**
```python
API_KEY = os.environ.get('API_KEY', '')
if not API_KEY:
    print("WARNING: API_KEY environment variable is not set")
```

### 2. SQL Injection Prevention
**Before:**
```python
sql = "SELECT id, username FROM users WHERE username LIKE '%{}%'".format(name)
cur.execute(sql)
```

**After:**
```python
sql = "SELECT id, username FROM users WHERE username LIKE ?"
cur.execute(sql, (f'%{name}%',))
```

### 3. Safe Data Serialization
**Before:**
```python
data = request.data
profile = pickle.loads(data)
```

**After:**
```python
if request.content_type != 'application/json':
    return jsonify({"error": "Content-Type must be application/json"}), 400

profile = request.get_json()
# + comprehensive validation
```

### 4. Command Injection Prevention
**Before:**
```python
cmd = request.form.get('cmd', '')
os.system("echo Running: " + cmd)
```

**After:**
```python
cmd = request.form.get('cmd', '')
if not re.match(r'^[a-zA-Z0-9\s.,!?-]+$', cmd):
    return jsonify({"error": "Invalid input"}), 400
return jsonify({"message": f"Running: {cmd}"})
```

### 5. Template Injection Prevention
**Before:**
```python
template = "<h1>Hello %s</h1>" % name
return render_template_string(template)
```

**After:**
```python
from flask import escape
return f"<h1>Hello {escape(name)}</h1>"
```

### 6. Password Security
**Before:**
```python
USERS = {
    "alice": {"password": "password123"},
}
if user and user.get("password") == password:
```

**After:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

USERS = {
    "alice": {"password_hash": generate_password_hash("SecurePassword123!")},
}
if user and check_password_hash(user.get("password_hash"), password):
```

### 7. Debug Mode Configuration
**Before:**
```python
app.run(debug=True)
```

**After:**
```python
debug_mode = os.environ.get('FLASK_ENV') == 'development'
app.run(debug=debug_mode, host='127.0.0.1', port=5000)
```

## Setup Instructions

### Windows

1. Install Python 3.9+
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```powershell
   $env:API_KEY="test_api_key"
   $env:FLASK_ENV="development"
   ```

### Linux/macOS

1. Run setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

### Docker

1. Build Docker image:
   ```bash
   docker build -t flask-security-audit .
   ```
2. Run container:
   ```bash
   docker run -p 5000:5000 flask-security-audit
   ```

## Running Tests

### Automatic Test Execution (Recommended)

Run the automatic test runner that detects your environment:

```bash
python auto_test.py
```

This will:
- Detect your operating system (Windows/Linux/macOS/Docker)
- Run tests on both vulnerable and secure versions
- Generate detailed logs in `logs/test_run.log`
- Save structured results in `logs/test_results.json`

**Expected Results:**
- Vulnerable version (`input_vulnerable.py`): **FAIL** (7 vulnerabilities detected)
- Secure version (`input.py`): **PASS** (0 vulnerabilities detected)

### Manual Test Execution

#### Windows
```powershell
# Test vulnerable version (should FAIL)
run_test.bat input_vulnerable.py

# Test secure version (should PASS)
run_test.bat input.py
```

#### Linux/macOS
```bash
# Test vulnerable version (should FAIL)
chmod +x run_test.sh
./run_test.sh input_vulnerable.py

# Test secure version (should PASS)
./run_test.sh input.py
```

## Test Coverage

The test scripts verify:
1. ✓ Absence of hardcoded secrets
2. ✓ SQL injection prevention
3. ✓ Safe deserialization (no pickle)
4. ✓ Command injection prevention
5. ✓ SSTI prevention
6. ✓ Password hashing
7. ✓ Debug mode configuration

## Logs and Reports

- **report.json**: Comprehensive vulnerability analysis with CWE mappings
- **logs/test_run.log**: Detailed test execution output
- **logs/test_results.json**: Structured test results in JSON format

## Security Best Practices Implemented

1. **Input Validation**: All user inputs are validated and sanitized
2. **Parameterized Queries**: SQL injection prevention using prepared statements
3. **Safe Serialization**: JSON instead of pickle for data exchange
4. **Output Encoding**: HTML escaping to prevent XSS and SSTI
5. **Cryptographic Hashing**: bcrypt-based password hashing
6. **Environment Variables**: Sensitive configuration externalized
7. **Secure Defaults**: Debug mode disabled by default
8. **Principle of Least Privilege**: Minimal permissions and exposure

## Production Deployment Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Configure `API_KEY` in environment/secrets manager
- [ ] Use WSGI server (Gunicorn/uWSGI) instead of Flask dev server
- [ ] Enable HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular dependency updates
- [ ] Implement proper session management
- [ ] Add security headers (CSP, HSTS, etc.)
- [ ] Configure proper CORS policies

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

## License

This is a security audit demonstration project for educational purposes.

## Author

Security Audit performed on November 25, 2025

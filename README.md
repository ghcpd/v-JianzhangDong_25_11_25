# Flask Security Audit & Remediation Report

## Overview

This project contains a comprehensive security audit of a Flask application, identifying vulnerabilities and providing secure, remediated versions with automated testing.

## Vulnerabilities Identified

### Summary
- **Total Vulnerabilities**: 7
- **Critical Severity**: 5
- **High Severity**: 2

### Detailed Vulnerability List

| ID | Type | Severity | Line(s) | CWE |
|----|------|----------|---------|-----|
| 1 | Hardcoded Secret - API Key | CRITICAL | 10-11 | CWE-798 |
| 2 | SQL Injection | CRITICAL | 17-18 | CWE-89 |
| 3 | Unsafe Deserialization | CRITICAL | 24-25 | CWE-502 |
| 4 | OS Command Injection | CRITICAL | 33-34 | CWE-78 |
| 5 | Template Injection (XSS) | HIGH | 42-43 | CWE-79 |
| 6 | Hardcoded Credentials | CRITICAL | 48-49 | CWE-256 |
| 7 | Debug Mode Enabled | HIGH | 59-60 | CWE-215 |

## Files Generated

### Core Files
- **`input.py`** - Original vulnerable application (for reference only)
- **`secure_input.py`** - Secured version with all fixes applied
- **`report.json`** - Detailed JSON report with all vulnerability details
- **`test_vulnerabilities.py`** - Comprehensive test suite

### Environment Setup
- **`requirements.txt`** - Python package dependencies
- **`setup.sh`** - Setup script for Linux/macOS
- **`setup.bat`** - Setup script for Windows
- **`Dockerfile`** - Docker container configuration

### Testing Scripts
- **`run_test.sh`** - Test runner for Linux/macOS
- **`run_test.bat`** - Test runner for Windows
- **`run_tests.py`** - Automatic test execution with environment detection

## Quick Start

### Windows

```batch
# Setup environment
setup.bat

# Run tests
run_test.bat

# Or run automatic tests
python run_tests.py
```

### Linux/macOS

```bash
# Setup environment
chmod +x setup.sh run_test.sh
bash setup.sh

# Run tests
bash run_test.sh

# Or run automatic tests
python3 run_tests.py
```

### Docker

```bash
# Build Docker image
docker build -t flask-security-audit .

# Run tests in Docker
docker run flask-security-audit
```

## Vulnerabilities & Fixes

### 1. Hardcoded API Key (Lines 10-11)
**Vulnerability**: API key stored in source code
```python
# VULNERABLE
API_KEY = "AKIA_EXAMPLE_HARDCODED_KEY_123456"
```

**Fix**: Load from environment variable
```python
# SECURE
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError('API_KEY environment variable not set')
```

---

### 2. SQL Injection (Lines 17-18)
**Vulnerability**: User input directly formatted into SQL query
```python
# VULNERABLE
sql = "SELECT id, username FROM users WHERE username LIKE '%{}%'".format(name)
cur.execute(sql)
```

**Fix**: Use parameterized queries
```python
# SECURE
sql = "SELECT id, username FROM users WHERE username LIKE ?"
cur.execute(sql, ('%' + name + '%',))
```

---

### 3. Unsafe Deserialization (Lines 24-25)
**Vulnerability**: Using pickle.loads() on untrusted data
```python
# VULNERABLE
data = request.data
profile = pickle.loads(data)
```

**Fix**: Use safe JSON deserialization
```python
# SECURE
data = request.get_json()
profile = data
```

---

### 4. OS Command Injection (Lines 33-34)
**Vulnerability**: User input concatenated into shell command
```python
# VULNERABLE
os.system("echo Running: " + cmd)
```

**Fix**: Use subprocess with shell=False
```python
# SECURE
subprocess.run(['echo', 'Running:', cmd], shell=False, capture_output=True)
```

---

### 5. Template Injection/XSS (Lines 42-43)
**Vulnerability**: User input unsanitized in template
```python
# VULNERABLE
template = "<h1>Hello %s</h1>" % name
return render_template_string(template)
```

**Fix**: Escape user input
```python
# SECURE
from markupsafe import escape
safe_name = escape(name)
return f"<h1>Hello {safe_name}</h1>"
```

---

### 6. Hardcoded Credentials (Lines 48-49)
**Vulnerability**: Plain text passwords in source code
```python
# VULNERABLE
USERS = {
    "alice": {"password": "password123"},
}
```

**Fix**: Use password hashing
```python
# SECURE
from werkzeug.security import generate_password_hash, check_password_hash
USERS = {
    "alice": {"password": generate_password_hash("password123")},
}
# Use check_password_hash() for verification
```

---

### 7. Debug Mode Enabled (Lines 59-60)
**Vulnerability**: Debug mode active in production code
```python
# VULNERABLE
if __name__ == '__main__':
    app.run(debug=True)
```

**Fix**: Control debug mode via environment variable
```python
# SECURE
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
```

---

## Testing

### Test Suite Features

The test suite (`test_vulnerabilities.py`) includes:

1. **Security Feature Tests**
   - API key environment variable loading
   - SQL injection protection
   - Safe JSON deserialization
   - Command injection prevention
   - XSS protection through escaping
   - Password hashing verification
   - Debug mode control

2. **Vulnerability Documentation Tests**
   - Tests that document and verify vulnerabilities in the original code
   - Fail appropriately to highlight issues

3. **Best Practices Tests**
   - Security packages verification
   - Security report generation
   - Secure file existence

### Running Tests

```bash
# Automatic environment detection and test execution
python run_tests.py

# Manual pytest execution
pytest test_vulnerabilities.py -v

# With coverage
pytest test_vulnerabilities.py --cov=secure_input --cov-report=html
```

### Test Results

All tests in the secure version should **PASS**:
- ✓ Environment variable management
- ✓ SQL injection prevention
- ✓ Safe deserialization
- ✓ Command execution safety
- ✓ XSS protection
- ✓ Password hashing
- ✓ Security artifacts

## Log Files

Test execution logs are saved to `logs/test_run.log` and include:
- Timestamp and environment information
- Test execution details
- Pass/fail status for each test
- Detailed error messages if applicable

## Environment Variables Required

For the secure version, set:

```bash
# Required
export API_KEY="your-actual-api-key"

# Optional
export FLASK_DEBUG="False"  # Set to "True" only in development
export FLASK_ENV="production"  # Use "production" in production
```

## Docker Deployment

```bash
# Build
docker build -t flask-app:secure .

# Run tests
docker run flask-app:secure

# Run application
docker run -e API_KEY="your-key" -p 5000:5000 flask-app:secure
```

## Security Best Practices Applied

✓ **Secrets Management**: Environment variables for sensitive data
✓ **SQL Injection Prevention**: Parameterized queries
✓ **Deserialization Safety**: JSON instead of pickle
✓ **Command Injection Prevention**: Subprocess with safe arguments
✓ **XSS Prevention**: Output escaping
✓ **Password Security**: Industry-standard hashing
✓ **Debug Control**: Environment-based debug mode
✓ **Dependency Management**: Explicit requirements.txt with versions

## Deployment Checklist

- [ ] Review `report.json` for all vulnerability details
- [ ] Compare `input.py` vs `secure_input.py` for changes
- [ ] Run full test suite: `python run_tests.py`
- [ ] Set required environment variables (API_KEY, etc.)
- [ ] Disable debug mode in production
- [ ] Use HTTPS/TLS for all connections
- [ ] Implement proper authentication/authorization
- [ ] Set up monitoring and logging
- [ ] Conduct security testing before production deployment

## Additional Security Recommendations

1. **Input Validation**: Implement comprehensive input validation
2. **CSRF Protection**: Use Flask-WTF for CSRF tokens
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Logging & Monitoring**: Add comprehensive security logging
5. **Database Security**: Use ORM with parameterized queries
6. **HTTPS**: Always use HTTPS in production
7. **Security Headers**: Add security headers (CSP, X-Frame-Options, etc.)
8. **Authentication**: Implement proper user authentication
9. **Authorization**: Implement role-based access control
10. **Regular Updates**: Keep dependencies updated

## CWE References

- CWE-78: OS Command Injection
- CWE-79: Cross-Site Scripting (XSS)
- CWE-89: SQL Injection
- CWE-215: Information Exposure Through Debug Information
- CWE-256: Plaintext Storage of Password
- CWE-502: Deserialization of Untrusted Data
- CWE-798: Use of Hard-Coded Credentials

## Contact & Support

For questions or additional security concerns, consult:
- `report.json` - Detailed vulnerability report
- `test_vulnerabilities.py` - Test cases showing secure patterns
- `secure_input.py` - Reference implementation of secure code

---

**Audit Date**: 2025-11-25
**Status**: All vulnerabilities identified and remediated
**Recommendation**: Deploy secure version after security testing

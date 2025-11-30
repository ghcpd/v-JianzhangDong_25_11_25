# Flask Application Security Audit & Testing Suite

This repository contains a comprehensive security audit and repair of a vulnerable Flask application, along with automated testing infrastructure.

## 📋 Overview

This project demonstrates:
- **Security Vulnerability Identification**: 7 critical security vulnerabilities detected and documented
- **Secure Code Remediation**: All vulnerabilities fixed with secure coding practices
- **Automated Testing**: Cross-platform test scripts that validate fixes
- **Environment Replication**: Docker, Linux, macOS, and Windows support

## 🔒 Vulnerabilities Identified

### Critical Vulnerabilities (CVSS 9.0+)
1. **SQL Injection (VULN-001)** - Line 13-16
2. **Insecure Deserialization/RCE (VULN-002)** - Line 21-27
3. **Command Injection (VULN-003)** - Line 30-35
4. **Server-Side Template Injection (VULN-004)** - Line 38-43

### High Severity Vulnerabilities
5. **Hardcoded API Key (VULN-005)** - Line 9
6. **Weak Password Storage (VULN-006)** - Line 46-47

### Medium Severity Vulnerabilities
7. **Debug Mode in Production (VULN-007)** - Line 57

## 📁 Project Structure

```
.
├── input.py                  # SECURE version (repaired)
├── input_vulnerable.py       # Original vulnerable version (for testing)
├── report.json              # Detailed vulnerability report
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
├── setup.sh                 # Linux/macOS setup script
├── run_test.sh             # Linux/macOS test script
├── run_test.bat            # Windows test script
├── auto_test.py            # Automatic test execution (cross-platform)
├── .env.example            # Environment variable template
├── logs/                   # Test execution logs
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- curl (for testing)
- Git (optional)

### Installation & Testing

#### Option 1: Automatic Testing (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Run automatic tests (detects environment)
python auto_test.py
```

#### Option 2: Manual Testing

**Windows:**
```cmd
pip install -r requirements.txt
run_test.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh run_test.sh
./setup.sh
./run_test.sh
```

**Docker:**
```bash
docker build -t flask-security-audit .
docker run -p 5000:5000 flask-security-audit
```

## 🔧 Environment Variables

Create a `.env` file based on `.env.example`:

```bash
API_KEY=your-secure-api-key-here
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

**Important:** Never commit `.env` files to version control!

## 🧪 Testing Methodology

### Test Script Behavior

The test scripts validate that:
1. **Vulnerable version** (`input_vulnerable.py`) exhibits expected vulnerabilities
2. **Secure version** (`input.py`) successfully mitigates all vulnerabilities

### Test Cases

| Test | Vulnerable Version | Secure Version |
|------|-------------------|----------------|
| SQL Injection | ❌ Exploitable | ✅ Protected |
| SSTI | ❌ Exploitable | ✅ Protected |
| Command Injection | ❌ Exploitable | ✅ Protected |
| Insecure Deserialization | ❌ Exploitable | ✅ Protected |
| Hardcoded Secrets | ❌ Present | ✅ Removed |

### Expected Results
- **Vulnerable version**: Tests should FAIL (vulnerabilities detected)
- **Secure version**: Tests should PASS (vulnerabilities mitigated)

## 🛡️ Security Fixes Applied

### 1. SQL Injection → Parameterized Queries
```python
# Before (Vulnerable)
sql = f"SELECT * FROM users WHERE name LIKE '%{name}%'"

# After (Secure)
sql = "SELECT * FROM users WHERE name LIKE ?"
cur.execute(sql, ('%' + name + '%',))
```

### 2. Insecure Deserialization → JSON
```python
# Before (Vulnerable)
profile = pickle.loads(data)

# After (Secure)
profile = json.loads(data.decode('utf-8'))
if not isinstance(profile, dict):
    return jsonify({"error": "Invalid format"}), 400
```

### 3. Command Injection → Input Validation
```python
# Before (Vulnerable)
os.system("echo Running: " + cmd)

# After (Secure)
if not re.match(r'^[a-zA-Z0-9\s]+$', cmd):
    return jsonify({"error": "Invalid command"}), 400
logger.info(f"Command logged: {cmd}")
```

### 4. SSTI → Proper Escaping
```python
# Before (Vulnerable)
template = "<h1>Hello %s</h1>" % name
return render_template_string(template)

# After (Secure)
safe_name = escape(name)
template = "<h1>Hello {{ name }}</h1>"
return render_template_string(template, name=safe_name)
```

### 5. Hardcoded Secrets → Environment Variables
```python
# Before (Vulnerable)
API_KEY = "AKIA_EXAMPLE_HARDCODED_KEY_123456"

# After (Secure)
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    logger.warning("API_KEY not set")
```

### 6. Plaintext Passwords → Hashed Passwords
```python
# Before (Vulnerable)
USERS = {"alice": {"password": "password123"}}
if user["password"] == password:
    return "login ok"

# After (Secure)
USERS = {"alice": {"password_hash": generate_password_hash("password123")}}
if check_password_hash(user["password_hash"], password):
    return jsonify({"status": "login ok"})
```

### 7. Debug Mode → Controlled Configuration
```python
# Before (Vulnerable)
app.run(debug=True)

# After (Secure)
debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.run(debug=debug_mode, host='127.0.0.1')
```

## 📊 Vulnerability Report

Detailed findings are available in `report.json` including:
- Vulnerability descriptions
- CWE classifications
- CVSS scores
- Attack examples
- Remediation guidance

## 🔍 Manual Verification

### Test SQL Injection
```bash
# Vulnerable version (port 5001)
curl "http://127.0.0.1:5001/greet?name=' OR '1'='1"

# Secure version (port 5002)
curl "http://127.0.0.1:5002/greet?name=' OR '1'='1"
```

### Test SSTI
```bash
# Vulnerable version
curl "http://127.0.0.1:5001/greet?name={{7*7}}"  # Returns: 49

# Secure version
curl "http://127.0.0.1:5002/greet?name={{7*7}}"  # Returns: {{7*7}}
```

### Test Command Injection
```bash
# Vulnerable version
curl -X POST http://127.0.0.1:5001/run -d "cmd=test; whoami"

# Secure version
curl -X POST http://127.0.0.1:5002/run -d "cmd=test; whoami"
```

## 📝 Logs

Test execution logs are saved to `logs/test_run.log` with:
- Timestamp for each test
- Detailed test results
- Pass/fail status
- Error messages

## 🐛 Troubleshooting

### Tests Fail to Start Server
- Ensure ports 5001 and 5002 are not in use
- Check that Python dependencies are installed
- Verify Python 3.8+ is being used

### Permission Denied on Linux/macOS
```bash
chmod +x setup.sh run_test.sh
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Curl Not Found
**Windows:** Curl is included in Windows 10+  
**Linux:** `sudo apt-get install curl`  
**macOS:** `brew install curl`

## 📚 Additional Recommendations

1. **Security Headers**: Implement CSP, HSTS, X-Frame-Options
2. **Rate Limiting**: Add rate limiting to prevent brute force
3. **HTTPS**: Always use HTTPS in production
4. **Input Validation**: Implement comprehensive input validation
5. **Logging**: Add security event logging and monitoring
6. **Dependency Scanning**: Regularly scan for vulnerable dependencies

## 📄 License

This is an educational security audit project.

## 🤝 Contributing

This project is for educational purposes. Feel free to use it as a reference for security testing.

## ⚠️ Disclaimer

The vulnerable version (`input_vulnerable.py`) contains intentional security flaws for educational purposes. **Never deploy this in production!**

## 📞 Support

For issues or questions, refer to:
- `report.json` - Detailed vulnerability documentation
- `logs/test_run.log` - Test execution details
- This README - Setup and usage instructions

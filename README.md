# Flask Security Audit Project

## Overview
This project contains a comprehensive security audit of a Flask web application, including vulnerability identification, fixes, and automated testing infrastructure.

## Files Structure

### Core Files
- **input.py** - Original vulnerable Flask application
- **input_secure.py** - Repaired secure version with all vulnerabilities fixed
- **report.json** - Detailed security audit report with all findings

### Testing Infrastructure
- **test_vulnerabilities.py** - Comprehensive test suite for both versions
- **auto_test.py** - Automatic test runner (detects environment)

### Environment Setup
- **requirements.txt** - Python dependencies
- **Dockerfile** - Container configuration for Docker testing

#### Linux/macOS
- **setup.sh** - Environment setup script
- **run_test.sh** - Test execution script

#### Windows
- **setup.bat** - Environment setup script
- **run_test.bat** - Test execution script

## Identified Vulnerabilities

### Critical (5)
1. **Hardcoded API Key** (Line 9) - CVSS 9.8
2. **SQL Injection** (Lines 12-16) - CVSS 9.9
3. **Pickle Deserialization RCE** (Lines 20-26) - CVSS 10.0
4. **Command Injection** (Lines 29-34) - CVSS 10.0
5. **Server-Side Template Injection** (Lines 37-42) - CVSS 9.8

### High (1)
6. **Hardcoded Passwords** (Lines 45-46, 51-55) - CVSS 7.5

### Medium (1)
7. **Debug Mode Enabled** (Line 57) - CVSS 6.5

## Quick Start

### Windows
```batch
# Setup environment
setup.bat

# Run tests
run_test.bat

# Or use automatic test runner
python auto_test.py
```

### Linux/macOS
```bash
# Setup environment
chmod +x setup.sh run_test.sh
./setup.sh

# Run tests
./run_test.sh

# Or use automatic test runner
python3 auto_test.py
```

### Docker
```bash
# Build image
docker build -t flask-security-audit .

# Run tests
docker run flask-security-audit

# Or use automatic runner
docker run flask-security-audit python auto_test.py
```

## Test Execution

The test suite automatically:
1. Detects the current environment (Windows/Linux/Docker)
2. Runs appropriate test scripts
3. Tests both vulnerable and secure versions
4. Verifies that vulnerabilities are exploitable in input.py
5. Confirms that fixes prevent exploitation in input_secure.py
6. Saves detailed logs to `logs/test_run.log`

### Expected Results
- **Vulnerable Version (input.py)**: Tests should detect multiple vulnerabilities
- **Secure Version (input_secure.py)**: All security checks should pass

## Security Fixes Summary

### 1. API Key Management
- **Before**: Hardcoded in source code
- **After**: Loaded from environment variables

### 2. SQL Injection Prevention
- **Before**: String formatting in SQL queries
- **After**: Parameterized queries with placeholders

### 3. Safe Deserialization
- **Before**: Pickle deserialization (RCE risk)
- **After**: JSON deserialization with validation

### 4. Command Execution Safety
- **Before**: Direct os.system() with user input
- **After**: Whitelist-based command execution

### 5. Template Injection Prevention
- **Before**: Direct string interpolation in templates
- **After**: Jinja2 variables with autoescaping

### 6. Password Security
- **Before**: Plaintext password storage
- **After**: Werkzeug password hashing (PBKDF2)

### 7. Debug Mode Control
- **Before**: Always enabled (debug=True)
- **After**: Environment-controlled with production defaults

## Dependencies

- Flask 3.0.0
- Werkzeug 3.0.1
- requests 2.31.0

## Logging

All test execution logs are saved to:
- Windows: `logs\test_run.log`
- Linux/macOS: `logs/test_run.log`
- Docker: `/app/logs/test_run.log`

## Security Recommendations

1. Implement comprehensive input validation
2. Add authentication/authorization middleware
3. Enable HTTPS/TLS
4. Implement rate limiting
5. Add comprehensive logging and monitoring
6. Use Web Application Firewall (WAF)
7. Implement Content Security Policy (CSP)
8. Regular security audits
9. Keep dependencies updated
10. Use security linters in CI/CD

## Compliance Notes

- **GDPR**: Password storage previously violated Article 32
- **PCI-DSS**: Multiple violations if handling payment data
- **OWASP Top 10**: Addressed A03:2021, A05:2021, A08:2021

## License

This is a security audit demonstration project.

## Author

Security Audit System - 2025-11-25

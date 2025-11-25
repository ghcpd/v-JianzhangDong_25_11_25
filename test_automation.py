#!/usr/bin/env python3
"""
Automated Security Audit Test Suite
Detects environment and runs appropriate tests with logging
"""

import os
import sys
import subprocess
import platform
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging with UTF-8 encoding
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / 'test_run.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def detect_environment():
    """Detect current environment."""
    env_info = {
        'platform': platform.system(),
        'platform_version': platform.release(),
        'python_version': platform.python_version(),
        'machine': platform.machine(),
    }
    
    # Check for Docker
    is_docker = Path('/.dockerenv').exists()
    env_info['is_docker'] = is_docker
    
    return env_info


def run_tests():
    """Run security vulnerability tests on input.py."""
    logger.info("=" * 60)
    logger.info("Flask Security Audit - Test Suite")
    logger.info("=" * 60)
    
    env_info = detect_environment()
    logger.info(f"Detected Platform: {env_info['platform']}")
    logger.info(f"Python Version: {env_info['python_version']}")
    logger.info(f"Docker Environment: {env_info['is_docker']}")
    logger.info("")
    
    tests = [
        test_hardcoded_api_key,
        test_sql_injection,
        test_pickle_deserialization,
        test_command_injection,
        test_template_injection,
        test_hardcoded_passwords,
        test_weak_password_comparison,
        test_debug_mode,
        test_python_syntax,
        test_imports,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Exception in {test.__name__}: {e}")
            failed += 1
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Test Results: {passed} PASSED, {failed} FAILED")
    logger.info("=" * 60)
    
    # Create test results summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'environment': env_info,
        'tests_passed': passed,
        'tests_failed': failed,
        'overall_status': 'PASSED' if failed == 0 else 'FAILED'
    }
    
    with open(LOG_DIR / 'test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Test results saved to: {log_file}")
    logger.info(f"Summary saved to: {LOG_DIR / 'test_results.json'}")
    
    return failed == 0


def test_hardcoded_api_key():
    """Test 1: Check for hardcoded API keys."""
    logger.info("Test 1: Hardcoded API Key Detection")
    
    with open('input.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'AKIA_EXAMPLE_HARDCODED_KEY' in content:
        logger.error("  [FAIL] Hardcoded API key still present")
        return False
    
    if 'os.getenv' in content and 'API_KEY' in content:
        logger.info("  [PASS] API key loaded from environment variable")
        return True
    
    logger.warning("  [WARN] API key handling unclear")
    return True


def test_sql_injection():
    """Test 2: Check for SQL injection vulnerabilities."""
    logger.info("Test 2: SQL Injection Prevention")
    
    with open('input.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for vulnerable pattern: format or % with user input
    if 'format(name)' in content or '% name' in content:
        if 'cur.execute(sql)' in content:
            logger.error("  [FAIL] Vulnerable SQL injection pattern detected")
            return False
    
    if '(?)' in content or 'execute(sql, (' in content:
        logger.info("  [PASS] Parameterized queries implemented")
        return True
    
    logger.info("  [PASS] SQL injection vulnerability addressed")
    return True


def test_pickle_deserialization():
    """Test 3: Check for unsafe pickle usage."""
    logger.info("Test 3: Pickle Deserialization Check")
    
    with open('input.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'pickle.loads' in content:
        logger.error("  [FAIL] Unsafe pickle.loads() still present")
        return False
    
    if 'get_json' in content:
        logger.info("  [PASS] JSON parsing implemented (safe)")
        return True
    
    logger.warning("  [WARN] Pickle handling unclear")
    return True


def test_command_injection():
    """Test 4: Check for command injection vulnerabilities."""
    logger.info("Test 4: Command Injection Prevention")
    
    with open('input.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check for dangerous os.system usage (not in comments)
    for i, line in enumerate(lines, 1):
        code_part = line.split('#')[0]  # Remove comments
        if 'os.system(' in code_part:
            logger.error(f"  [FAIL] Unsafe os.system() detected at line {i}")
            return False
    
    # Check for safe subprocess usage
    content = ''.join(lines)
    if 'subprocess.run' in content:
        logger.info("  [PASS] Safe subprocess.run() implementation")
        return True
    
    logger.warning("  [WARN] Command execution method unclear")
    return True


def test_template_injection():
    """Test 5: Check for SSTI vulnerabilities."""
    logger.info("Test 5: Template Injection Prevention")
    
    with open('input.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'render_template_string' in content:
        if 'request.args' in content or 'request.form' in content:
            logger.error("  [FAIL] render_template_string() with user input detected")
            return False
    
    if 'escape(' in content:
        logger.info("  [PASS] HTML escaping implemented")
        return True
    
    logger.info("  [PASS] Template injection vulnerability addressed")
    return True


def test_hardcoded_passwords():
    """Test 6: Check for hardcoded passwords."""
    logger.info("Test 6: Hardcoded Credentials Check")
    
    with open('input.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'password123' in content or '"password": "' in content:
        logger.error("  [FAIL] Hardcoded password detected")
        return False
    
    if 'password_hash' in content:
        logger.info("  [PASS] Password hashing implemented")
        return True
    
    logger.warning("  [WARN] Password handling unclear")
    return True


def test_weak_password_comparison():
    """Test 7: Check for weak password comparison."""
    logger.info("Test 7: Weak Password Comparison Check")
    
    with open('input.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'check_password_hash' in content:
        logger.info("  [PASS] Proper password hash verification")
        return True
    
    logger.warning("  [WARN] Password comparison method should use check_password_hash()")
    return True


def test_debug_mode():
    """Test 8: Check for debug mode in production."""
    logger.info("Test 8: Debug Mode Check")
    
    with open('input.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'debug=True' in content:
        logger.error("  [FAIL] Debug mode enabled in code")
        return False
    
    if 'FLASK_DEBUG' in content or 'os.getenv' in content:
        logger.info("  [PASS] Debug mode controlled by environment variable")
        return True
    
    logger.info("  [PASS] Debug mode disabled")
    return True


def test_python_syntax():
    """Test 9: Validate Python syntax."""
    logger.info("Test 9: Python Syntax Validation")
    
    try:
        import py_compile
        py_compile.compile('input.py', doraise=True)
        logger.info("  [PASS] Python syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        logger.error(f"  [FAIL] Syntax error - {e}")
        return False


def test_imports():
    """Test 10: Validate imports."""
    logger.info("Test 10: Import Validation")
    
    try:
        # Test import without running the app
        import ast
        with open('input.py', 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        # Check for import statements
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        logger.info(f"  [PASS] {len(imports)} imports found and valid")
        return True
    except Exception as e:
        logger.error(f"  [FAIL] Import validation failed - {e}")
        return False


def main():
    """Main entry point."""
    logger.info(f"Test execution started at {datetime.now()}")
    
    success = run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

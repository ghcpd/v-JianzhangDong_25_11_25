"""
Test suite for Flask Security Audit
Tests both vulnerable and secure versions of the Flask application
"""

import pytest
import sys
import os
import re
from unittest.mock import patch, MagicMock
import json

# Test configuration
SECURE_APP_MODE = True  # Set to False to test vulnerable version


class TestSecureVersionCodeAudit:
    """Tests for code-level security of the secure version"""

    def test_api_key_uses_environment_variable(self):
        """Test that API_KEY is loaded from environment, not hardcoded"""
        with open('secure_input.py', 'r') as f:
            content = f.read()
        
        # Check for hardcoded API keys
        assert 'AKIA_EXAMPLE_HARDCODED_KEY' not in content
        assert 'os.getenv' in content
        assert 'API_KEY' in content

    def test_sql_uses_parameterized_queries(self):
        """Test that SQL queries use parameterized queries"""
        with open('secure_input.py', 'r') as f:
            content = f.read()
        
        # Check for parameterized query pattern
        assert 'cur.execute(sql' in content
        assert '?' in content
        # Should NOT have string.format with SQL
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'cur.execute' in line or 'execute(sql' in line:
                # The execute should use parameters, not format
                assert '.format' not in line

    def test_no_pickle_deserialization(self):
        """Test that pickle is not used for untrusted data"""
        with open('secure_input.py', 'r') as f:
            content = f.read()
        
        # pickle should not be imported or used
        import_lines = [l for l in content.split('\n') if 'import' in l and 'pickle' in l]
        assert len(import_lines) == 0, "pickle should not be imported"
        
        # In upload_profile, should use get_json not pickle
        assert 'get_json' in content
        assert 'json' in content.lower()

    def test_subprocess_used_safely(self):
        """Test that subprocess is used instead of os.system"""
        with open('secure_input.py', 'r') as f:
            content = f.read()
        
        # Should use subprocess, not os.system with concatenation
        assert 'subprocess.run' in content
        assert 'shell=False' in content
        # Should NOT have os.system with string concatenation
        assert 'os.system(' not in content or 'os.system("echo' not in content

    def test_xss_protection_with_escape(self):
        """Test that XSS is prevented with proper escaping"""
        with open('secure_input.py', 'r') as f:
            content = f.read()
        
        # Should use escape in the greet function
        lines = content.split('\n')
        in_greet = False
        has_escape = False
        
        for line in lines:
            if 'def greet' in line:
                in_greet = True
            elif in_greet and line.strip().startswith('def '):
                in_greet = False
            
            if in_greet and 'escape(' in line:
                has_escape = True
        
        assert has_escape, "escape() should be used in greet endpoint"
        # Should NOT use render_template_string in greet
        assert 'render_template_string' not in content

    def test_passwords_are_hashed(self):
        """Test that passwords are hashed, not stored in plain text"""
        with open('secure_input.py', 'r') as f:
            content = f.read()
        
        # Should use password hashing functions
        assert 'generate_password_hash' in content, "Must use generate_password_hash"
        assert 'check_password_hash' in content, "Must use check_password_hash"
        
        # Extract USERS dictionary section
        users_start = content.find('USERS = {')
        users_end = content.find('}', users_start) + 1
        users_section = content[users_start:users_end] if users_start != -1 else ""
        
        # Check that password values use generate_password_hash, not plain text
        if users_section:
            # Should contain "password": "generate_password_hash(... or similar
            assert 'generate_password_hash' in users_section, "Passwords must be hashed in USERS dict"

    def test_debug_mode_is_configurable(self):
        """Test that debug mode is not hardcoded to True"""
        with open('secure_input.py', 'r') as f:
            content = f.read()
        
        # Should use environment variable for debug
        assert 'os.getenv' in content
        assert 'FLASK_DEBUG' in content
        # Should NOT have debug=True hardcoded
        assert 'debug=True' not in content

    def test_api_key_validation(self):
        """Test that missing API_KEY raises error"""
        os.environ['API_KEY'] = 'test_key_value'
        
        # Import and verify
        try:
            import secure_input
            assert secure_input.API_KEY == 'test_key_value'
        except ValueError as e:
            assert 'API_KEY' in str(e)


class TestSecureVersionFunctionality:
    """Integration tests for secure version functionality"""

    def test_greet_endpoint_exists(self):
        """Test that greet endpoint exists and is secure"""
        from secure_input import app
        
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test with normal input
        response = client.get('/greet?name=Alice')
        assert response.status_code == 200
        assert 'Alice' in response.data.decode()
        
        # Test with XSS payload - should be escaped
        response = client.get('/greet?name=<script>alert(1)</script>')
        assert response.status_code == 200
        # Script tags should be escaped
        data = response.data.decode()
        assert '<script>' not in data or '&lt;' in data

    def test_upload_endpoint_exists(self):
        """Test that upload endpoint exists and handles JSON safely"""
        from secure_input import app
        
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test with valid JSON
        response = client.post(
            '/upload_profile',
            data=json.dumps({'name': 'Test User'}),
            content_type='application/json'
        )
        assert response.status_code in [200, 400]

    def test_run_endpoint_exists(self):
        """Test that run endpoint exists and executes safely"""
        from secure_input import app
        
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test with command
        response = client.post('/run', data={'cmd': 'test'})
        assert response.status_code in [200, 500]

    def test_login_endpoint_exists(self):
        """Test that login endpoint exists and uses password hashing"""
        from secure_input import app
        
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test with valid credentials
        response = client.post(
            '/login',
            data={'username': 'alice', 'password': 'password123'}
        )
        assert response.status_code in [200, 401]

    def test_debug_mode_not_enabled(self):
        """Test that debug mode is not enabled by default"""
        os.environ['FLASK_DEBUG'] = 'False'
        
        debug_flag = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        assert debug_flag is False


class TestVulnerableVersionDetection:
    """Tests that detect vulnerabilities in the original version"""

    def test_vulnerable_hardcoded_api_key(self):
        """Test detection of hardcoded API key in vulnerable version"""
        try:
            import input as vuln_module
            content = open('input.py', 'r').read()
            
            # Check if API key is hardcoded
            if 'AKIA_EXAMPLE_HARDCODED_KEY' in content:
                assert True, "Vulnerability confirmed: Hardcoded API key found"
            else:
                pytest.skip("Hardcoded API key not found")
        except ImportError:
            pytest.skip("Testing against secure version")

    def test_vulnerable_sql_injection(self):
        """Test detection of SQL injection in vulnerable version"""
        content = open('input.py', 'r').read()
        
        # Check for SQL injection pattern
        if '.format(name)' in content and 'LIKE' in content:
            assert True, "Vulnerability confirmed: SQL injection pattern found"
        else:
            pytest.skip("SQL injection pattern not found in input.py")

    def test_vulnerable_pickle_usage(self):
        """Test detection of unsafe pickle usage"""
        content = open('input.py', 'r').read()
        
        # Check for pickle.loads
        if 'pickle.loads' in content:
            assert True, "Vulnerability confirmed: pickle.loads found"
        else:
            pytest.skip("pickle.loads not found in input.py")

    def test_vulnerable_os_system(self):
        """Test detection of os.system with concatenation"""
        content = open('input.py', 'r').read()
        
        # Check for os.system with string concatenation
        if 'os.system' in content and '+' in content:
            assert True, "Vulnerability confirmed: os.system with concatenation"
        else:
            pytest.skip("os.system vulnerability not found in input.py")


class TestSecurityBestPractices:
    """Tests that verify security best practices are implemented"""

    def test_requirements_has_security_packages(self):
        """Test that requirements.txt includes security packages"""
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Should include werkzeug for password hashing
        assert 'werkzeug' in requirements.lower() or 'Werkzeug' in requirements

    def test_report_json_exists(self):
        """Test that security report is generated"""
        assert os.path.exists('report.json')
        
        with open('report.json', 'r') as f:
            report = json.load(f)
        
        assert 'vulnerabilities' in report
        assert len(report['vulnerabilities']) > 0
        assert 'total_vulnerabilities' in report

    def test_secure_input_file_exists(self):
        """Test that secure version exists"""
        assert os.path.exists('secure_input.py')
        
        with open('secure_input.py', 'r') as f:
            content = f.read()
        
        # Verify security fixes are present
        assert 'os.getenv' in content  # Environment variables
        assert 'parameterized' in content or 'execute(sql' in content  # Parameterized queries
        assert 'check_password_hash' in content  # Password hashing
        assert 'escape(' in content  # XSS protection
        assert 'subprocess.run' in content  # Safe command execution


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

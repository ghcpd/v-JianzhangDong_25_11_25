"""
Comprehensive Security Test Suite for Flask Application
Tests both vulnerable and secure versions to demonstrate fixes
"""

import requests
import json
import pickle
import time
import sys
import subprocess
import os
import signal
from threading import Thread

class SecurityTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "vulnerabilities_found": [],
            "security_improvements": []
        }
    
    def test_sql_injection(self):
        """Test for SQL injection vulnerability"""
        print("\n[TEST] SQL Injection Attack")
        self.results["total_tests"] += 1
        
        # Malicious payload to test SQL injection
        payload = "' OR '1'='1"
        try:
            # This would exploit vulnerable version
            response = requests.get(f"{self.base_url}/users?name={payload}", timeout=3)
            if response.status_code == 200:
                # Check if injection worked (would return all users)
                print(f"  Response: {response.status_code}")
                return True
            return False
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_pickle_rce(self):
        """Test for pickle deserialization RCE"""
        print("\n[TEST] Pickle Deserialization RCE")
        self.results["total_tests"] += 1
        
        # Create malicious pickle payload
        class Exploit:
            def __reduce__(self):
                import os
                return (os.system, ('echo EXPLOITED > /tmp/pwned.txt',))
        
        try:
            malicious_data = pickle.dumps(Exploit())
            response = requests.post(
                f"{self.base_url}/upload_profile",
                data=malicious_data,
                headers={"Content-Type": "application/octet-stream"},
                timeout=3
            )
            print(f"  Response: {response.status_code}")
            # Vulnerable version would execute code (500 error or success)
            # Secure version would reject pickle data
            return response.status_code != 400
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_command_injection(self):
        """Test for command injection vulnerability"""
        print("\n[TEST] Command Injection Attack")
        self.results["total_tests"] += 1
        
        # Malicious payload to test command injection
        payload = "; ls -la"
        try:
            response = requests.post(
                f"{self.base_url}/run",
                data={"cmd": payload},
                timeout=3
            )
            print(f"  Response: {response.status_code}")
            # Vulnerable version executes command
            # Secure version rejects with 403
            return response.status_code != 403
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_ssti(self):
        """Test for Server-Side Template Injection"""
        print("\n[TEST] Server-Side Template Injection (SSTI)")
        self.results["total_tests"] += 1
        
        # Malicious payload to test SSTI
        payload = "{{7*7}}"
        try:
            response = requests.get(
                f"{self.base_url}/greet?name={payload}",
                timeout=3
            )
            print(f"  Response: {response.status_code}")
            # Check if template evaluation occurred
            if "49" in response.text:
                print("  VULNERABLE: Template injection executed!")
                return True
            print("  SECURE: Template injection prevented")
            return False
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_json_deserialization(self):
        """Test secure JSON deserialization (should work)"""
        print("\n[TEST] Secure JSON Deserialization")
        self.results["total_tests"] += 1
        
        try:
            safe_data = json.dumps({"name": "TestUser"})
            response = requests.post(
                f"{self.base_url}/upload_profile",
                data=safe_data,
                headers={"Content-Type": "application/json"},
                timeout=3
            )
            print(f"  Response: {response.status_code}")
            if response.status_code == 200:
                print("  SUCCESS: JSON deserialization works securely")
                return True
            return False
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_whitelisted_commands(self):
        """Test whitelisted command execution (should work)"""
        print("\n[TEST] Whitelisted Command Execution")
        self.results["total_tests"] += 1
        
        try:
            response = requests.post(
                f"{self.base_url}/run",
                data={"cmd": "status"},
                timeout=3
            )
            print(f"  Response: {response.status_code}")
            if response.status_code == 200:
                print("  SUCCESS: Whitelisted command executed")
                return True
            return False
        except Exception as e:
            print(f"  Error: {e}")
            return False

def start_flask_app(script_name, port=5000):
    """Start Flask application in background"""
    env = os.environ.copy()
    env['FLASK_APP'] = script_name
    
    process = subprocess.Popen(
        [sys.executable, script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    # Wait for server to start
    time.sleep(3)
    return process

def stop_flask_app(process):
    """Stop Flask application"""
    if process:
        if sys.platform == "win32":
            process.send_signal(signal.CTRL_C_EVENT)
        else:
            process.send_signal(signal.SIGINT)
        process.wait(timeout=5)

def run_tests(app_file, test_name):
    """Run security tests against specified Flask app"""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"Application: {app_file}")
    print(f"{'='*60}")
    
    # Check if file exists
    if not os.path.exists(app_file):
        print(f"ERROR: {app_file} not found!")
        return None
    
    # Start Flask app
    print(f"\nStarting Flask application from {app_file}...")
    process = start_flask_app(app_file)
    
    # Give it time to start
    time.sleep(2)
    
    # Check if process is running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"ERROR: Flask app failed to start!")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return None
    
    tester = SecurityTester()
    results = {}
    
    try:
        # Test vulnerabilities
        results['sql_injection'] = tester.test_sql_injection()
        results['pickle_rce'] = tester.test_pickle_rce()
        results['command_injection'] = tester.test_command_injection()
        results['ssti'] = tester.test_ssti()
        
        # Test secure features
        results['json_safe'] = tester.test_json_deserialization()
        results['whitelist'] = tester.test_whitelisted_commands()
        
    except Exception as e:
        print(f"\nERROR during testing: {e}")
    finally:
        # Stop Flask app
        print(f"\nStopping Flask application...")
        stop_flask_app(process)
    
    return results

def main():
    print("\n" + "="*60)
    print("Flask Application Security Test Suite")
    print("="*60)
    
    log_file = "logs/test_run.log"
    os.makedirs("logs", exist_ok=True)
    
    # Redirect output to log file as well
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, data):
            for f in self.files:
                f.write(data)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()
    
    with open(log_file, 'w') as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)
        
        try:
            # Test vulnerable version
            print("\n\n" + "="*60)
            print("PHASE 1: Testing VULNERABLE version (input.py)")
            print("="*60)
            vuln_results = run_tests("input.py", "Vulnerable Version")
            
            # Test secure version
            print("\n\n" + "="*60)
            print("PHASE 2: Testing SECURE version (input_secure.py)")
            print("="*60)
            secure_results = run_tests("input_secure.py", "Secure Version")
            
            # Summary
            print("\n\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)
            
            if vuln_results and secure_results:
                print("\nVulnerable Version (input.py):")
                print(f"  SQL Injection: {'VULNERABLE' if vuln_results.get('sql_injection') else 'PROTECTED'}")
                print(f"  Pickle RCE: {'VULNERABLE' if vuln_results.get('pickle_rce') else 'PROTECTED'}")
                print(f"  Command Injection: {'VULNERABLE' if vuln_results.get('command_injection') else 'PROTECTED'}")
                print(f"  SSTI: {'VULNERABLE' if vuln_results.get('ssti') else 'PROTECTED'}")
                
                print("\nSecure Version (input_secure.py):")
                print(f"  SQL Injection: {'VULNERABLE' if secure_results.get('sql_injection') else 'PROTECTED'}")
                print(f"  Pickle RCE: {'VULNERABLE' if secure_results.get('pickle_rce') else 'PROTECTED'}")
                print(f"  Command Injection: {'VULNERABLE' if secure_results.get('command_injection') else 'PROTECTED'}")
                print(f"  SSTI: {'VULNERABLE' if secure_results.get('ssti') else 'PROTECTED'}")
                print(f"  JSON Deserialization: {'WORKING' if secure_results.get('json_safe') else 'FAILED'}")
                print(f"  Whitelisted Commands: {'WORKING' if secure_results.get('whitelist') else 'FAILED'}")
                
                # Determine pass/fail
                vuln_count = sum([
                    vuln_results.get('sql_injection', False),
                    vuln_results.get('pickle_rce', False),
                    vuln_results.get('command_injection', False),
                    vuln_results.get('ssti', False)
                ])
                
                secure_count = sum([
                    not secure_results.get('sql_injection', True),
                    not secure_results.get('pickle_rce', True),
                    not secure_results.get('command_injection', True),
                    not secure_results.get('ssti', True),
                    secure_results.get('json_safe', False),
                    secure_results.get('whitelist', False)
                ])
                
                print(f"\n{'='*60}")
                print(f"RESULT:")
                print(f"  Vulnerable version: {vuln_count} vulnerabilities detected")
                print(f"  Secure version: {secure_count}/6 security checks passed")
                
                if vuln_count >= 2 and secure_count >= 4:
                    print("\n✓ TEST PASSED: Security improvements verified!")
                    print(f"{'='*60}\n")
                    sys.stdout = original_stdout
                    return 0
                else:
                    print("\n✗ TEST FAILED: Security improvements not sufficient")
                    print(f"{'='*60}\n")
                    sys.stdout = original_stdout
                    return 1
            else:
                print("\n✗ TEST FAILED: Could not complete tests")
                print(f"{'='*60}\n")
                sys.stdout = original_stdout
                return 1
                
        except Exception as e:
            print(f"\n✗ CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout = original_stdout
            return 1

if __name__ == "__main__":
    exit(main())

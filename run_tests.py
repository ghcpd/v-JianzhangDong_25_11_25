#!/usr/bin/env python3
"""
Automatic test executor for Flask Security Audit
Detects the current environment and runs appropriate tests
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from datetime import datetime

class TestExecutor:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.log_dir = self.script_dir / "logs"
        self.log_file = self.log_dir / "test_run.log"
        self.log_dir.mkdir(exist_ok=True)
        
        self.platform = self._detect_platform()
        self.tests_passed = 0
        self.tests_failed = 0
        
    def _detect_platform(self):
        """Detect the current platform"""
        system = platform.system()
        if system == "Windows":
            return "windows"
        elif system == "Darwin":
            return "macos"
        elif system == "Linux":
            # Check if running in Docker
            if Path("/.dockerenv").exists():
                return "docker"
            return "linux"
        else:
            return "unknown"
    
    def log(self, message, to_console=True):
        """Log message to file and optionally to console"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")
        if to_console:
            print(message)
    
    def run_command(self, cmd, description=""):
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)
    
    def check_file_content(self, file_path, search_string, should_exist=True):
        """Check if a file contains specific content"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                found = search_string in content
                if should_exist:
                    return found
                else:
                    return not found
        except Exception as e:
            self.log(f"  Error reading file: {e}")
            return False
    
    def run_test(self, test_name, test_func):
        """Run a single test"""
        self.log(f"Running: {test_name}")
        try:
            if test_func():
                self.log(f"  ✓ PASSED")
                self.tests_passed += 1
                return True
            else:
                self.log(f"  ✗ FAILED")
                self.tests_failed += 1
                return False
        except Exception as e:
            self.log(f"  ✗ FAILED: {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_vulnerable_sql_injection(self):
        """Test 1: Check SQL injection vulnerability in input.py"""
        return self.check_file_content(
            self.script_dir / "input.py",
            ".format(name)"
        )
    
    def test_vulnerable_pickle(self):
        """Test 2: Check pickle vulnerability in input.py"""
        return self.check_file_content(
            self.script_dir / "input.py",
            "pickle.loads"
        )
    
    def test_vulnerable_command_injection(self):
        """Test 3: Check command injection vulnerability in input.py"""
        return self.check_file_content(
            self.script_dir / "input.py",
            "os.system"
        )
    
    def test_vulnerable_hardcoded_key(self):
        """Test 4: Check hardcoded API key in input.py"""
        return self.check_file_content(
            self.script_dir / "input.py",
            "AKIA_EXAMPLE_HARDCODED_KEY"
        )
    
    def test_fixed_version_exists(self):
        """Test 5: Check if fixed version exists"""
        return (self.script_dir / "input_fixed.py").exists()
    
    def test_fixed_parameterized_queries(self):
        """Test 6: Check parameterized queries in fixed version"""
        return self.check_file_content(
            self.script_dir / "input_fixed.py",
            "cur.execute(sql, ("
        )
    
    def test_fixed_json_instead_pickle(self):
        """Test 7: Check JSON used instead of pickle"""
        has_json = self.check_file_content(
            self.script_dir / "input_fixed.py",
            "get_json"
        )
        no_pickle = self.check_file_content(
            self.script_dir / "input_fixed.py",
            "pickle.loads",
            should_exist=False
        )
        return has_json and no_pickle
    
    def test_fixed_subprocess(self):
        """Test 8: Check subprocess used instead of os.system"""
        return self.check_file_content(
            self.script_dir / "input_fixed.py",
            "subprocess.run"
        )
    
    def test_fixed_api_key_from_env(self):
        """Test 9: Check API key loaded from environment"""
        return self.check_file_content(
            self.script_dir / "input_fixed.py",
            "os.getenv('API_KEY'"
        )
    
    def test_fixed_password_hashing(self):
        """Test 10: Check password hashing"""
        return self.check_file_content(
            self.script_dir / "input_fixed.py",
            "generate_password_hash"
        )
    
    def test_report_exists(self):
        """Test 11: Check if report.json exists"""
        return (self.script_dir / "report.json").exists()
    
    def test_report_valid_json(self):
        """Test 12: Validate report.json is valid JSON"""
        try:
            with open(self.script_dir / "report.json", "r") as f:
                json.load(f)
            return True
        except:
            return False
    
    def execute_platform_specific_tests(self):
        """Execute platform-specific test scripts"""
        self.log("")
        self.log("Platform-Specific Tests")
        self.log("=" * 50)
        
        if self.platform == "windows":
            cmd = f'cmd /c "{self.script_dir / "run_test.bat"}"'
        else:
            cmd = f'bash "{self.script_dir / "run_test.sh"}"'
        
        self.log(f"Running {self.platform} test script...")
        success, stdout, stderr = self.run_command(cmd)
        
        if success:
            self.log("✓ Platform-specific tests passed")
            self.tests_passed += 1
        else:
            self.log("✗ Platform-specific tests failed")
            if stderr:
                self.log(f"  Error: {stderr}")
            self.tests_failed += 1
    
    def create_summary(self):
        """Create test summary"""
        summary = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "platform": self.platform,
                "total_tests": self.tests_passed + self.tests_failed,
                "passed": self.tests_passed,
                "failed": self.tests_failed,
                "success_rate": f"{(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%" if (self.tests_passed + self.tests_failed) > 0 else "N/A",
                "log_file": str(self.log_file)
            },
            "status": "PASSED" if self.tests_failed == 0 else "FAILED"
        }
        
        # Save summary as JSON
        summary_file = self.log_dir / "test_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def run_all_tests(self):
        """Run all tests"""
        # Initialize log
        with open(self.log_file, "w") as f:
            f.write("")
        
        self.log("=" * 60)
        self.log("Flask Security Audit - Automatic Test Executor")
        self.log("=" * 60)
        self.log(f"Platform: {self.platform.upper()}")
        self.log(f"Started: {datetime.now()}")
        self.log("=" * 60)
        self.log("")
        
        # Run all tests
        self.log("Standard Security Tests")
        self.log("=" * 50)
        self.run_test("Vulnerable Version - SQL Injection", self.test_vulnerable_sql_injection)
        self.run_test("Vulnerable Version - Pickle Deserialization", self.test_vulnerable_pickle)
        self.run_test("Vulnerable Version - Command Injection", self.test_vulnerable_command_injection)
        self.run_test("Vulnerable Version - Hardcoded API Key", self.test_vulnerable_hardcoded_key)
        self.run_test("Fixed Version - File Exists", self.test_fixed_version_exists)
        self.run_test("Fixed Version - Parameterized Queries", self.test_fixed_parameterized_queries)
        self.run_test("Fixed Version - JSON Instead of Pickle", self.test_fixed_json_instead_pickle)
        self.run_test("Fixed Version - Subprocess Usage", self.test_fixed_subprocess)
        self.run_test("Fixed Version - API Key from Environment", self.test_fixed_api_key_from_env)
        self.run_test("Fixed Version - Password Hashing", self.test_fixed_password_hashing)
        self.run_test("Report Generation", self.test_report_exists)
        self.run_test("Report Validation", self.test_report_valid_json)
        
        # Print summary
        self.log("")
        self.log("=" * 60)
        self.log("Test Summary")
        self.log("=" * 60)
        self.log(f"Passed: {self.tests_passed}")
        self.log(f"Failed: {self.tests_failed}")
        self.log(f"Total:  {self.tests_passed + self.tests_failed}")
        self.log("")
        
        if self.tests_failed == 0:
            self.log("Status: ALL TESTS PASSED ✓")
            exit_code = 0
        else:
            self.log("Status: SOME TESTS FAILED ✗")
            exit_code = 1
        
        self.log(f"Log File: {self.log_file}")
        self.log(f"Completed: {datetime.now()}")
        self.log("=" * 60)
        
        # Create summary
        summary = self.create_summary()
        self.log(f"\nTest Summary JSON saved to: {self.log_dir / 'test_summary.json'}")
        
        return exit_code

def main():
    """Main entry point"""
    executor = TestExecutor()
    exit_code = executor.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

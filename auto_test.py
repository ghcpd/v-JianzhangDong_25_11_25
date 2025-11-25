#!/usr/bin/env python3
"""
Automatic Test Execution Script
Detects environment and runs appropriate security tests
"""

import os
import sys
import platform
import subprocess
import json
from datetime import datetime
from pathlib import Path


class TestRunner:
    def __init__(self):
        self.system = platform.system()
        self.log_dir = Path("logs")
        self.log_file = self.log_dir / "test_run.log"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "tests": []
        }
        
    def setup_logging(self):
        """Create logs directory if it doesn't exist"""
        self.log_dir.mkdir(exist_ok=True)
        
    def log(self, message):
        """Write message to both console and log file"""
        print(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    
    def detect_environment(self):
        """Detect the current execution environment"""
        self.log("=" * 60)
        self.log("Environment Detection")
        self.log("=" * 60)
        
        # Check if running in Docker
        if os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv'):
            env = "Docker"
        elif self.system == "Windows":
            env = "Windows"
        elif self.system == "Linux":
            env = "Linux"
        elif self.system == "Darwin":
            env = "macOS"
        else:
            env = "Unknown"
        
        self.log(f"Operating System: {self.system}")
        self.log(f"Platform: {platform.platform()}")
        self.log(f"Python Version: {platform.python_version()}")
        self.log(f"Environment: {env}")
        self.log("")
        
        return env
    
    def run_test_script(self, test_file="input.py"):
        """Run the appropriate test script based on the environment"""
        self.log("=" * 60)
        self.log(f"Running Security Tests on: {test_file}")
        self.log("=" * 60)
        self.log("")
        
        try:
            if self.system == "Windows":
                # Run Windows batch script
                result = subprocess.run(
                    ["cmd.exe", "/c", "run_test.bat", test_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                # Run bash script (Linux/macOS/Docker)
                # Make sure the script is executable
                script_path = Path("run_test.sh")
                if script_path.exists():
                    os.chmod(script_path, 0o755)
                
                result = subprocess.run(
                    ["bash", "run_test.sh", test_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            # Log output
            self.log(result.stdout)
            if result.stderr:
                self.log("STDERR:")
                self.log(result.stderr)
            
            # Record test results
            test_result = {
                "file": test_file,
                "exit_code": result.returncode,
                "passed": result.returncode == 0,
                "output": result.stdout
            }
            self.results["tests"].append(test_result)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.log("ERROR: Test execution timed out")
            return False
        except Exception as e:
            self.log(f"ERROR: Failed to run tests: {str(e)}")
            return False
    
    def run_comparative_tests(self):
        """Run tests on both vulnerable and fixed versions"""
        self.log("\n" + "=" * 60)
        self.log("Running Comparative Security Tests")
        self.log("=" * 60)
        self.log("")
        
        # Test vulnerable version (should fail)
        self.log("Phase 1: Testing VULNERABLE version (input_vulnerable.py)")
        self.log("-" * 60)
        vulnerable_passed = self.run_test_script("input_vulnerable.py")
        
        if vulnerable_passed:
            self.log("⚠ WARNING: Vulnerable version passed tests (unexpected)")
        else:
            self.log("✓ EXPECTED: Vulnerable version failed security tests")
        
        self.log("\n")
        
        # Test fixed version (should pass)
        self.log("Phase 2: Testing SECURE version (input.py)")
        self.log("-" * 60)
        secure_passed = self.run_test_script("input.py")
        
        if secure_passed:
            self.log("✓ SUCCESS: Secure version passed all security tests")
        else:
            self.log("✗ FAILURE: Secure version failed some tests (needs review)")
        
        return not vulnerable_passed and secure_passed
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = self.log_dir / "test_results.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"\nTest results saved to: {results_file}")
    
    def print_summary(self, success):
        """Print test execution summary"""
        self.log("\n" + "=" * 60)
        self.log("Test Execution Summary")
        self.log("=" * 60)
        
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for t in self.results["tests"] if t["passed"])
        
        self.log(f"Total test runs: {total_tests}")
        self.log(f"Passed: {passed_tests}")
        self.log(f"Failed: {total_tests - passed_tests}")
        
        if success:
            self.log("\n✓ Overall Status: SUCCESS")
            self.log("The vulnerable code correctly fails tests,")
            self.log("and the secure code passes all tests.")
        else:
            self.log("\n✗ Overall Status: FAILURE")
            self.log("Test results did not match expected outcomes.")
        
        self.log(f"\nLogs saved to: {self.log_file}")
        self.log("=" * 60)
    
    def run(self):
        """Main execution method"""
        self.setup_logging()
        
        # Clear previous log
        if self.log_file.exists():
            self.log_file.unlink()
        
        self.log("=" * 60)
        self.log("Automatic Security Test Execution")
        self.log("=" * 60)
        self.log(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("")
        
        # Detect environment
        env = self.detect_environment()
        
        # Run comparative tests
        success = self.run_comparative_tests()
        
        # Save results
        self.save_results()
        
        # Print summary
        self.print_summary(success)
        
        # Return appropriate exit code
        return 0 if success else 1


def main():
    """Entry point for the script"""
    runner = TestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

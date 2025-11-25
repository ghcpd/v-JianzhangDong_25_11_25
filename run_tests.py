#!/usr/bin/env python3
"""
Automatic Test Execution Script
Detects environment and runs appropriate test suite
Supports Windows, Linux, Docker, and macOS
"""

import os
import sys
import platform
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime


class EnvironmentDetector:
    """Detects the current environment"""
    
    @staticmethod
    def get_os():
        """Get operating system"""
        system = platform.system()
        return system

    @staticmethod
    def is_docker():
        """Check if running in Docker"""
        return os.path.exists('/.dockerenv') or os.path.exists('/run/.dockerenv')

    @staticmethod
    def is_wsl():
        """Check if running in WSL"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except FileNotFoundError:
            return False


class TestRunner:
    """Manages test execution"""
    
    def __init__(self):
        self.os = EnvironmentDetector.get_os()
        self.is_docker = EnvironmentDetector.is_docker()
        self.is_wsl = EnvironmentDetector.is_wsl()
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / 'test_run.log'
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.get_environment_info(),
            'tests': [],
            'summary': {}
        }
    
    def get_environment_info(self):
        """Get environment information"""
        return {
            'os': self.os,
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'in_docker': self.is_docker,
            'in_wsl': self.is_wsl,
            'platform': platform.platform(),
            'processor': platform.processor()
        }
    
    def log(self, message, level='INFO'):
        """Log message to both console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # Use a simple text format to avoid Unicode encoding issues on Windows
        safe_message = log_message.encode('ascii', errors='replace').decode('ascii')
        print(safe_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def check_requirements(self):
        """Check if requirements are installed"""
        self.log("Checking Python dependencies...")
        
        try:
            import flask
            import pytest
            self.log("[OK] All required packages found")
            return True
        except ImportError as e:
            self.log(f"[ERROR] Missing package: {e}", level='ERROR')
            return False
    
    def setup_environment(self):
        """Setup test environment"""
        self.log("Setting up test environment...")
        
        # Set required environment variables
        os.environ['API_KEY'] = 'test_api_key_for_testing'
        os.environ['FLASK_DEBUG'] = 'False'
        os.environ['PYTHONUNBUFFERED'] = '1'
        
        self.log("[OK] Environment variables configured")
    
    def run_tests(self):
        """Run pytest test suite"""
        self.log("=" * 60)
        self.log("RUNNING TEST SUITE")
        self.log("=" * 60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            'test_vulnerabilities.py',
            '-v',
            '--tb=short',
            '--color=yes',
            '-p', 'no:warnings'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=False,
                text=True,
                timeout=300
            )
            
            self.test_results['tests'].append({
                'name': 'pytest test suite',
                'status': 'passed' if result.returncode == 0 else 'failed',
                'exit_code': result.returncode
            })
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.log("[ERROR] Tests timed out", level='ERROR')
            return False
        except Exception as e:
            self.log(f"[ERROR] Error running tests: {e}", level='ERROR')
            return False
    
    def verify_security_files(self):
        """Verify security-related files exist"""
        self.log("Verifying security artifacts...")
        
        files_to_check = {
            'report.json': 'Security vulnerability report',
            'secure_input.py': 'Secure version of application',
            'requirements.txt': 'Python dependencies',
            'test_vulnerabilities.py': 'Test suite'
        }
        
        all_exist = True
        for filename, description in files_to_check.items():
            if Path(filename).exists():
                self.log(f"[OK] {description} ({filename})")
            else:
                self.log(f"[MISSING] {description} ({filename})", level='WARNING')
                all_exist = False
        
        return all_exist
    
    def load_and_display_report(self):
        """Load and display the security report"""
        self.log("=" * 60)
        self.log("SECURITY AUDIT REPORT")
        self.log("=" * 60)
        
        try:
            with open('report.json', 'r') as f:
                report = json.load(f)
            
            self.log(f"File: {report.get('file_audited', 'N/A')}")
            self.log(f"Audit Date: {report.get('audit_date', 'N/A')}")
            self.log(f"Total Vulnerabilities: {report.get('total_vulnerabilities', 0)}")
            
            vulnerabilities = report.get('vulnerabilities', [])
            for vuln in vulnerabilities:
                vuln_id = vuln.get('id', 'N/A')
                vuln_type = vuln.get('type', 'N/A')
                severity = vuln.get('severity', 'N/A')
                lines = vuln.get('location', {}).get('lines', [])
                
                self.log(f"\n[{vuln_id}] {vuln_type} (Severity: {severity})")
                self.log(f"    Lines: {lines}")
                self.log(f"    {vuln.get('description', '')}")
            
            return report
            
        except Exception as e:
            self.log(f"[ERROR] Error reading report: {e}", level='ERROR')
            return None
    
    def generate_summary(self, tests_passed):
        """Generate test summary"""
        self.log("=" * 60)
        self.log("TEST EXECUTION SUMMARY")
        self.log("=" * 60)
        
        self.test_results['summary'] = {
            'tests_passed': tests_passed,
            'environment_os': self.os,
            'in_docker': self.is_docker,
            'timestamp': datetime.now().isoformat(),
            'log_file': str(self.log_file)
        }
        
        if tests_passed:
            self.log("[PASS] All tests PASSED")
            self.log("[PASS] Secure version is ready for deployment")
            status = "SUCCESS"
        else:
            self.log("[FAIL] Some tests FAILED")
            self.log("[FAIL] Please review failures above")
            status = "FAILED"
        
        self.log("")
        self.log(f"Test Log: {self.log_file}")
        self.log(f"Environment: {self.os}")
        
        # Save results to JSON
        results_file = self.log_dir / 'test_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        self.log(f"Results saved to: {results_file}")
        
        return 0 if tests_passed else 1
    
    def run(self):
        """Execute full test pipeline"""
        self.log("=" * 60)
        self.log("FLASK SECURITY AUDIT - AUTOMATIC TEST EXECUTION")
        self.log("=" * 60)
        self.log("")
        
        # Display environment
        self.log(f"Detected OS: {self.os}")
        self.log(f"Python Version: {platform.python_version()}")
        self.log(f"In Docker: {self.is_docker}")
        self.log("")
        
        # Verify security files
        if not self.verify_security_files():
            self.log("⚠ Some security artifacts are missing", level='WARNING')
        
        self.log("")
        
        # Setup environment
        self.setup_environment()
        self.log("")
        
        # Check requirements
        if not self.check_requirements():
            self.log("Installing requirements...", level='WARNING')
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'])
        
        self.log("")
        
        # Run tests
        tests_passed = self.run_tests()
        
        self.log("")
        
        # Load and display report
        self.load_and_display_report()
        
        self.log("")
        
        # Generate summary
        return self.generate_summary(tests_passed)


def main():
    """Main entry point"""
    try:
        runner = TestRunner()
        exit_code = runner.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

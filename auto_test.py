#!/usr/bin/env python3
"""
Automatic Test Execution Script
Detects current environment and runs appropriate tests automatically
Supports: Windows, Linux, macOS, and Docker
"""

import os
import sys
import platform
import subprocess
import shutil
from datetime import datetime

class AutoTestRunner:
    def __init__(self):
        self.platform = platform.system()
        self.is_docker = os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER')
        self.log_dir = "logs"
        self.log_file = os.path.join(self.log_dir, "test_run.log")
        
    def setup_environment(self):
        """Create necessary directories and files"""
        print(f"Setting up test environment...")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Test Execution: {timestamp}\n")
            f.write(f"Platform: {self.platform}\n")
            f.write(f"Docker: {'Yes' if self.is_docker else 'No'}\n")
            f.write(f"{'='*60}\n\n")
    
    def detect_python(self):
        """Detect available Python executable"""
        for cmd in ['python3', 'python']:
            if shutil.which(cmd):
                return cmd
        return None
    
    def run_windows_tests(self):
        """Run tests on Windows platform"""
        print(f"\n[AUTO-TEST] Detected Windows environment")
        print(f"[AUTO-TEST] Running Windows test script...\n")
        
        # Check if setup is needed
        if not os.path.exists('venv') and not os.path.exists('venv\\Scripts'):
            print("[AUTO-TEST] Virtual environment not found. Running setup first...")
            setup_result = subprocess.run(['setup.bat'], shell=True)
            if setup_result.returncode != 0:
                print("[AUTO-TEST] Setup failed!")
                return 1
        
        # Run tests
        result = subprocess.run(['run_test.bat'], shell=True)
        return result.returncode
    
    def run_unix_tests(self):
        """Run tests on Linux/macOS platform"""
        print(f"\n[AUTO-TEST] Detected {self.platform} environment")
        print(f"[AUTO-TEST] Running Unix test script...\n")
        
        # Make scripts executable
        for script in ['setup.sh', 'run_test.sh']:
            if os.path.exists(script):
                os.chmod(script, 0o755)
        
        # Check if setup is needed
        if not os.path.exists('venv'):
            print("[AUTO-TEST] Virtual environment not found. Running setup first...")
            setup_result = subprocess.run(['./setup.sh'], shell=True)
            if setup_result.returncode != 0:
                print("[AUTO-TEST] Setup failed!")
                return 1
        
        # Run tests
        result = subprocess.run(['./run_test.sh'], shell=True)
        return result.returncode
    
    def run_docker_tests(self):
        """Run tests in Docker container"""
        print(f"\n[AUTO-TEST] Detected Docker environment")
        print(f"[AUTO-TEST] Running tests directly...\n")
        
        python_cmd = self.detect_python()
        if not python_cmd:
            print("[AUTO-TEST] Python not found!")
            return 1
        
        # Create test database
        print("[AUTO-TEST] Setting up test database...")
        db_setup = f"""
import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)')
cur.execute('DELETE FROM users')
cur.execute('INSERT INTO users VALUES (1, "testuser")')
cur.execute('INSERT INTO users VALUES (2, "admin")')
conn.commit()
conn.close()
"""
        subprocess.run([python_cmd, '-c', db_setup])
        
        # Run tests
        result = subprocess.run([python_cmd, 'test_vulnerabilities.py'])
        return result.returncode
    
    def run_python_tests(self):
        """Run tests directly with Python (fallback)"""
        print(f"\n[AUTO-TEST] Running tests with Python directly...\n")
        
        python_cmd = self.detect_python()
        if not python_cmd:
            print("[AUTO-TEST] Python not found!")
            return 1
        
        # Check dependencies
        print("[AUTO-TEST] Checking dependencies...")
        try:
            subprocess.run([python_cmd, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("[AUTO-TEST] Failed to install dependencies!")
            return 1
        
        # Create test database
        print("[AUTO-TEST] Setting up test database...")
        db_setup = f"""
import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)')
cur.execute('DELETE FROM users')
cur.execute('INSERT INTO users VALUES (1, "testuser")')
cur.execute('INSERT INTO users VALUES (2, "admin")')
conn.commit()
conn.close()
"""
        subprocess.run([python_cmd, '-c', db_setup])
        
        # Run tests
        result = subprocess.run([python_cmd, 'test_vulnerabilities.py'])
        return result.returncode
    
    def run(self):
        """Main execution method"""
        print("="*60)
        print("Automatic Test Execution System")
        print("="*60)
        
        self.setup_environment()
        
        # Detect environment and run appropriate tests
        if self.is_docker:
            exit_code = self.run_docker_tests()
        elif self.platform == "Windows":
            exit_code = self.run_windows_tests()
        elif self.platform in ["Linux", "Darwin"]:  # Darwin is macOS
            exit_code = self.run_unix_tests()
        else:
            print(f"[AUTO-TEST] Unknown platform: {self.platform}")
            print(f"[AUTO-TEST] Attempting direct Python execution...")
            exit_code = self.run_python_tests()
        
        # Summary
        print("\n" + "="*60)
        if exit_code == 0:
            print("✓ AUTOMATIC TESTS COMPLETED SUCCESSFULLY")
        else:
            print("✗ AUTOMATIC TESTS FAILED")
        print(f"Log file: {self.log_file}")
        print("="*60 + "\n")
        
        return exit_code

def main():
    """Entry point"""
    runner = AutoTestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

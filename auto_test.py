#!/usr/bin/env python3
"""
Automatic Test Execution Script
Detects the current environment and runs appropriate test scripts
Logs results to logs/test_run.log
"""

import os
import sys
import platform
import subprocess
import time
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "test_run.log")

def ensure_log_dir():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"✓ Created {LOG_DIR} directory")

def log_message(message, also_print=True):
    """Write message to log file and optionally print to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    if also_print:
        print(message)

def detect_environment():
    """Detect the current operating environment"""
    system = platform.system()
    
    # Check if running in Docker
    in_docker = False
    if os.path.exists("/.dockerenv"):
        in_docker = True
    elif os.path.exists("/proc/1/cgroup"):
        try:
            with open("/proc/1/cgroup", "r") as f:
                in_docker = "docker" in f.read()
        except:
            pass
    
    return {
        "system": system,
        "in_docker": in_docker,
        "platform": platform.platform(),
        "python_version": platform.python_version()
    }

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import flask
    except ImportError:
        missing.append("flask")
    
    try:
        import werkzeug
    except ImportError:
        missing.append("werkzeug")
    
    try:
        import markupsafe
    except ImportError:
        missing.append("markupsafe")
    
    # Check for curl (for tests)
    if platform.system() == "Windows":
        curl_check = subprocess.run(
            ["where", "curl"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        curl_check = subprocess.run(
            ["which", "curl"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    if curl_check.returncode != 0:
        missing.append("curl")
    
    return missing

def run_windows_tests():
    """Run tests on Windows using batch script"""
    log_message("=" * 50)
    log_message("Running Windows Test Script (run_test.bat)")
    log_message("=" * 50)
    
    if not os.path.exists("run_test.bat"):
        log_message("ERROR: run_test.bat not found!")
        return False
    
    try:
        # Run the batch script
        result = subprocess.run(
            ["cmd.exe", "/c", "run_test.bat"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Log output
        log_message("\n--- Test Output ---")
        log_message(result.stdout, also_print=False)
        if result.stderr:
            log_message("\n--- Test Errors ---")
            log_message(result.stderr, also_print=False)
        
        if result.returncode == 0:
            log_message("✓ Tests completed successfully")
            return True
        else:
            log_message(f"✗ Tests failed with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message("✗ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        log_message(f"✗ Error running tests: {e}")
        return False

def run_unix_tests():
    """Run tests on Linux/macOS using shell script"""
    log_message("=" * 50)
    log_message("Running Unix Test Script (run_test.sh)")
    log_message("=" * 50)
    
    if not os.path.exists("run_test.sh"):
        log_message("ERROR: run_test.sh not found!")
        return False
    
    # Make script executable
    try:
        os.chmod("run_test.sh", 0o755)
    except Exception as e:
        log_message(f"Warning: Could not set execute permission: {e}")
    
    try:
        # Run the shell script
        result = subprocess.run(
            ["bash", "run_test.sh"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Log output
        log_message("\n--- Test Output ---")
        log_message(result.stdout, also_print=False)
        if result.stderr:
            log_message("\n--- Test Errors ---")
            log_message(result.stderr, also_print=False)
        
        if result.returncode == 0:
            log_message("✓ Tests completed successfully")
            return True
        else:
            log_message(f"✗ Tests failed with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message("✗ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        log_message(f"✗ Error running tests: {e}")
        return False

def run_docker_tests():
    """Run tests in Docker environment"""
    log_message("=" * 50)
    log_message("Running Tests in Docker Environment")
    log_message("=" * 50)
    
    # In Docker, use the Unix script
    return run_unix_tests()

def main():
    """Main execution function"""
    print("=" * 60)
    print("Automatic Security Testing System")
    print("=" * 60)
    
    # Ensure log directory exists
    ensure_log_dir()
    
    # Start logging
    log_message("=" * 60)
    log_message("AUTOMATIC TEST EXECUTION STARTED")
    log_message("=" * 60)
    
    # Detect environment
    env = detect_environment()
    log_message(f"\nEnvironment Detection:")
    log_message(f"  Operating System: {env['system']}")
    log_message(f"  Platform: {env['platform']}")
    log_message(f"  Python Version: {env['python_version']}")
    log_message(f"  Running in Docker: {env['in_docker']}")
    
    # Check dependencies
    log_message("\nChecking Dependencies...")
    missing = check_dependencies()
    if missing:
        log_message(f"✗ Missing dependencies: {', '.join(missing)}")
        log_message("\nPlease install missing dependencies:")
        log_message("  pip install -r requirements.txt")
        return 1
    else:
        log_message("✓ All dependencies found")
    
    # Check for required files
    log_message("\nChecking Required Files...")
    required_files = ["input.py", "input_vulnerable.py", "report.json"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        log_message(f"✗ Missing required files: {', '.join(missing_files)}")
        return 1
    else:
        log_message("✓ All required files present")
    
    # Run appropriate tests based on environment
    log_message("\nStarting Security Tests...\n")
    time.sleep(1)
    
    success = False
    
    if env['in_docker']:
        success = run_docker_tests()
    elif env['system'] == "Windows":
        success = run_windows_tests()
    elif env['system'] in ["Linux", "Darwin"]:  # Darwin is macOS
        success = run_unix_tests()
    else:
        log_message(f"✗ Unsupported platform: {env['system']}")
        return 1
    
    # Final summary
    log_message("\n" + "=" * 60)
    if success:
        log_message("✓ ALL TESTS PASSED")
        log_message("=" * 60)
        log_message(f"\nTest log saved to: {LOG_FILE}")
        print(f"\n✓ Tests completed successfully!")
        print(f"Full log available at: {LOG_FILE}")
        return 0
    else:
        log_message("✗ TESTS FAILED")
        log_message("=" * 60)
        log_message(f"\nTest log saved to: {LOG_FILE}")
        print(f"\n✗ Tests failed. Check log for details: {LOG_FILE}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log_message("\n\n✗ Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        log_message(f"\n\n✗ Unexpected error: {e}")
        import traceback
        log_message(traceback.format_exc())
        sys.exit(1)

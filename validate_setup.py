"""
Quick validation script to verify the setup is working
"""
import os
import sys

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_content(filepath, search_string, should_exist=True):
    """Check if content exists in file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            exists = search_string in content
            if should_exist and exists:
                print(f"  ✓ Found: {search_string[:50]}...")
                return True
            elif not should_exist and not exists:
                print(f"  ✓ Not found (as expected): {search_string[:50]}...")
                return True
            else:
                if should_exist:
                    print(f"  ✗ Missing: {search_string[:50]}...")
                else:
                    print(f"  ✗ Found (should be removed): {search_string[:50]}...")
                return False
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False

def main():
    print("=" * 60)
    print("Security Audit Validation")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Check core files
    print("1. Checking Core Files...")
    all_passed &= check_file("input.py", "Secure version")
    all_passed &= check_file("input_vulnerable.py", "Vulnerable version")
    all_passed &= check_file("report.json", "Vulnerability report")
    print()
    
    # Check configuration files
    print("2. Checking Configuration Files...")
    all_passed &= check_file("requirements.txt", "Python dependencies")
    all_passed &= check_file(".env.example", "Environment template")
    all_passed &= check_file("Dockerfile", "Docker configuration")
    print()
    
    # Check setup scripts
    print("3. Checking Setup Scripts...")
    all_passed &= check_file("setup.sh", "Linux/macOS setup")
    print()
    
    # Check test scripts
    print("4. Checking Test Scripts...")
    all_passed &= check_file("run_test.sh", "Linux/macOS tests")
    all_passed &= check_file("run_test.bat", "Windows tests")
    all_passed &= check_file("auto_test.py", "Automatic test executor")
    print()
    
    # Check documentation
    print("5. Checking Documentation...")
    all_passed &= check_file("README.md", "README documentation")
    all_passed &= check_file("SUMMARY.md", "Summary document")
    all_passed &= check_file(".gitignore", "Git ignore file")
    print()
    
    # Validate security fixes in input.py
    print("6. Validating Security Fixes in input.py...")
    all_passed &= check_content("input.py", "SECURITY FIX", should_exist=True)
    all_passed &= check_content("input.py", "AKIA_EXAMPLE_HARDCODED_KEY", should_exist=False)
    all_passed &= check_content("input.py", "os.environ.get('API_KEY')", should_exist=True)
    all_passed &= check_content("input.py", "generate_password_hash", should_exist=True)
    all_passed &= check_content("input.py", "json.loads", should_exist=True)
    all_passed &= check_content("input.py", "pickle.loads", should_exist=False)
    print()
    
    # Validate vulnerabilities still exist in input_vulnerable.py
    print("7. Validating Vulnerabilities in input_vulnerable.py...")
    all_passed &= check_content("input_vulnerable.py", "AKIA_EXAMPLE_HARDCODED_KEY", should_exist=True)
    all_passed &= check_content("input_vulnerable.py", "pickle.loads", should_exist=True)
    all_passed &= check_content("input_vulnerable.py", ".format(name)", should_exist=True)
    print()
    
    # Check report.json structure
    print("8. Validating report.json...")
    try:
        import json
        with open("report.json", 'r') as f:
            report = json.load(f)
            if "audit_report" in report:
                print("  ✓ Report structure valid")
                vulns = report["audit_report"].get("vulnerabilities", [])
                print(f"  ✓ Found {len(vulns)} vulnerabilities documented")
                all_passed &= (len(vulns) == 7)
            else:
                print("  ✗ Invalid report structure")
                all_passed = False
    except Exception as e:
        print(f"  ✗ Error reading report: {e}")
        all_passed = False
    print()
    
    # Check logs directory
    print("9. Checking Logs Directory...")
    if os.path.exists("logs"):
        print("  ✓ Logs directory exists")
    else:
        print("  ✗ Logs directory missing")
        all_passed = False
    print()
    
    # Final summary
    print("=" * 60)
    if all_passed:
        print("✓ ALL VALIDATION CHECKS PASSED")
        print("=" * 60)
        print()
        print("The security audit is complete and all components are in place.")
        print("You can now run tests with: python auto_test.py")
        return 0
    else:
        print("✗ SOME VALIDATION CHECKS FAILED")
        print("=" * 60)
        print()
        print("Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

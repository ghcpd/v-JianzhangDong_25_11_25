"""
Quick verification script to check all files are in place
"""
import os
import json

def check_file(filename, description):
    """Check if a file exists and print status"""
    exists = os.path.exists(filename)
    status = "✓" if exists else "✗"
    print(f"{status} {filename:30s} - {description}")
    return exists

def main():
    print("="*70)
    print("Security Audit Project - File Verification")
    print("="*70)
    print()
    
    files_to_check = [
        ("input.py", "Original vulnerable Flask application"),
        ("input_secure.py", "Repaired secure version"),
        ("report.json", "Detailed security audit report"),
        ("test_vulnerabilities.py", "Comprehensive test suite"),
        ("auto_test.py", "Automatic test runner"),
        ("requirements.txt", "Python dependencies"),
        ("Dockerfile", "Docker configuration"),
        ("setup.sh", "Linux/macOS setup script"),
        ("setup.bat", "Windows setup script"),
        ("run_test.sh", "Linux/macOS test runner"),
        ("run_test.bat", "Windows test runner"),
        ("README.md", "Project documentation"),
        ("SECURITY_SUMMARY.txt", "Security summary"),
    ]
    
    print("Core Files:")
    print("-" * 70)
    all_exist = True
    for filename, description in files_to_check:
        exists = check_file(filename, description)
        all_exist = all_exist and exists
    
    print()
    print("="*70)
    
    if all_exist:
        print("✓ ALL FILES PRESENT")
        
        # Check report.json content
        print()
        print("Report Summary:")
        print("-" * 70)
        try:
            with open('report.json', 'r') as f:
                report = json.load(f)
                metadata = report.get('audit_metadata', {})
                print(f"  Total Vulnerabilities: {metadata.get('total_vulnerabilities', 0)}")
                print(f"  Critical: {metadata.get('critical_count', 0)}")
                print(f"  High: {metadata.get('high_count', 0)}")
                print(f"  Medium: {metadata.get('medium_count', 0)}")
                print()
                
                print("  Vulnerability IDs:")
                for vuln in report.get('vulnerabilities', []):
                    print(f"    - {vuln['id']}: {vuln['title']} ({vuln['severity']})")
        except Exception as e:
            print(f"  Error reading report: {e}")
        
        print()
        print("="*70)
        print("Setup Instructions:")
        print("-" * 70)
        print()
        print("Windows:")
        print("  1. Run: setup.bat")
        print("  2. Run: run_test.bat")
        print("  Or simply: python auto_test.py")
        print()
        print("Linux/macOS:")
        print("  1. Run: ./setup.sh")
        print("  2. Run: ./run_test.sh")
        print("  Or simply: python3 auto_test.py")
        print()
        print("Docker:")
        print("  1. Build: docker build -t flask-security-audit .")
        print("  2. Run: docker run flask-security-audit")
        print()
        print("="*70)
        return 0
    else:
        print("✗ SOME FILES MISSING")
        return 1

if __name__ == "__main__":
    exit(main())

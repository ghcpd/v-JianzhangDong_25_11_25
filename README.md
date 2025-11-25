# Security Patch and Test Suite for input.py

This repository contains an audited and remediated Flask application (`input.py`) plus a vulnerable copy (`input_vulnerable.py`) and a set of automated tests and scripts to reproduce the secure and insecure behaviors.

Files:
- `input.py`: Patched, secure version of the application.
- `input_vulnerable.py`: Original, intentionally insecure copy for testing.
- `tests/test_security.py`: Script which runs security tests against the server and writes `logs/test_run.log`.
- `run_test.sh` / `run_test.bat`: Test runner for patched server.
- `run_test_vulnerable.sh` / `run_test_vulnerable.bat`: Test runner for vulnerable server.
- `Dockerfile`: Build a containerized environment with required dependencies.
- `requirements.txt`: Python dependencies.
- `report.json`: Audit report describing vulnerabilities and fixes.

How to test (Linux / macOS):
1. Setup:
   ```bash
   ./setup.sh
   source .venv/bin/activate
   ```
2. Run tests against patched app (should PASS):
   ```bash
   ./run_test.sh
   tail -n +1 logs/test_run.log
   ```
3. Run tests against vulnerable app (should FAIL):
   ```bash
   ./run_test_vulnerable.sh
   tail -n +1 logs/test_run.log
   ```

How to test (Windows PowerShell):
1. Setup:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate
   pip install -r requirements.txt
   ```
2. Run tests against patched app (should PASS):
   ```powershell
   .\run_test.bat
   type logs\test_run.log
   ```
3. Run tests against vulnerable app (should FAIL):
   ```powershell
   .\run_test_vulnerable.bat
   type logs\test_run.log
   ```

Docker Instructions:
```bash
docker build -t flask-secure-app .
docker run -e API_KEY=DUMMY -e SECRET_KEY=dummy_secret -p 5000:5000 flask-secure-app
``` 
Then run tests against `http://127.0.0.1:5000/` as shown above.

Notes:
- `report.json` outlines detected vulnerabilities and remedial steps.
- The tests attempt a set of common webapp attacks: pickle deserialization, command injection, server-side template injection (SSTI), SQL injection, and checks for hardcoded secrets.
- The test suite will PASS against the patched app and FAIL against `input_vulnerable.py`.

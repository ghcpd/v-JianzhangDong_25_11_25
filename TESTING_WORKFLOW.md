# Security Audit - Testing Workflow

## Test Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    auto_test.py (Main Entry)                │
│                  Automatic Test Orchestrator                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Detect Environment  │
                │  - Windows          │
                │  - Linux/macOS      │
                │  - Docker           │
                └──────────┬──────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│   Test Vulnerable    │      │    Test Secure       │
│  (input_vulnerable)  │      │     (input.py)       │
└──────────┬───────────┘      └──────────┬───────────┘
           │                               │
           ▼                               ▼
   ┌───────────────┐              ┌───────────────┐
   │  Windows:     │              │  Windows:     │
   │ run_test.bat  │              │ run_test.bat  │
   │               │              │               │
   │  Linux/macOS: │              │  Linux/macOS: │
   │ run_test.sh   │              │ run_test.sh   │
   └───────┬───────┘              └───────┬───────┘
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │  Run 7 Security Tests │
               │  1. Hardcoded Secrets │
               │  2. SQL Injection     │
               │  3. Pickle Deser.     │
               │  4. Command Injection │
               │  5. SSTI              │
               │  6. Weak Passwords    │
               │  7. Debug Mode        │
               └───────────┬───────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
    ┌─────────────┐                ┌─────────────┐
    │ VULNERABLE  │                │   SECURE    │
    │   FAILS     │                │   PASSES    │
    │ (7 issues)  │                │ (0 issues)  │
    └──────┬──────┘                └──────┬──────┘
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  Save Results  │
                  └────────┬───────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
  ┌─────────────────┐            ┌─────────────────┐
  │ test_run.log    │            │test_results.json│
  │ (Text Format)   │            │ (JSON Format)   │
  └─────────────────┘            └─────────────────┘
```

## Expected Test Results

### Phase 1: Testing input_vulnerable.py
```
❌ Test Result: FAIL (Expected)
├── ❌ Hardcoded API Key Found
├── ❌ SQL Injection Detected
├── ❌ Insecure Deserialization (pickle)
├── ❌ Command Injection Found
├── ❌ SSTI Vulnerability
├── ❌ Plaintext Passwords
└── ❌ Debug Mode Enabled

Status: 7 vulnerabilities found ❌
```

### Phase 2: Testing input.py
```
✅ Test Result: PASS (Expected)
├── ✅ No Hardcoded Secrets
├── ✅ SQL Injection Prevented
├── ✅ Safe Deserialization (JSON)
├── ✅ Command Injection Prevented
├── ✅ SSTI Prevented
├── ✅ Passwords Hashed
└── ✅ Debug Mode Properly Configured

Status: All security tests passed ✅
```

## File Dependencies

```
auto_test.py
    ├── requires: Python 3.x
    ├── calls: run_test.bat (Windows) or run_test.sh (Linux/macOS)
    ├── tests: input_vulnerable.py and input.py
    └── outputs: 
        ├── logs/test_run.log
        └── logs/test_results.json

run_test.bat / run_test.sh
    ├── tests: input file (passed as argument)
    ├── checks:
    │   ├── Hardcoded secrets (grep/findstr)
    │   ├── SQL injection patterns
    │   ├── pickle.loads usage
    │   ├── os.system calls
    │   ├── render_template_string
    │   ├── plaintext passwords
    │   └── debug=True
    └── returns: exit code (0=pass, 1=fail)

input.py (Secure)
    ├── depends: Flask, Werkzeug
    ├── uses: 
    │   ├── os.environ for secrets
    │   ├── Parameterized queries
    │   ├── JSON for serialization
    │   ├── Input validation
    │   ├── HTML escaping
    │   └── Password hashing
    └── result: All tests pass ✅

input_vulnerable.py (Original)
    ├── depends: Flask
    ├── contains:
    │   ├── Hardcoded API key
    │   ├── String formatting in SQL
    │   ├── pickle.loads
    │   ├── os.system
    │   ├── render_template_string
    │   ├── Plaintext passwords
    │   └── debug=True
    └── result: All tests fail ❌
```

## Running the Tests

### Option 1: Automatic (Recommended)
```bash
python auto_test.py
```
- ✅ Auto-detects environment
- ✅ Tests both versions
- ✅ Generates comprehensive logs
- ✅ Saves structured results

### Option 2: Manual Testing

#### Windows:
```powershell
# Test vulnerable version
run_test.bat input_vulnerable.py

# Test secure version  
run_test.bat input.py
```

#### Linux/macOS:
```bash
# Test vulnerable version
./run_test.sh input_vulnerable.py

# Test secure version
./run_test.sh input.py
```

## Success Criteria

✅ **PASS**: Vulnerable version FAILS tests (finds 7 vulnerabilities)
✅ **PASS**: Secure version PASSES tests (finds 0 vulnerabilities)
❌ **FAIL**: If results don't match expected outcomes

## Output Files

| File | Description | Format |
|------|-------------|--------|
| `logs/test_run.log` | Detailed execution log | Plain text |
| `logs/test_results.json` | Structured test results | JSON |
| `report.json` | Vulnerability analysis | JSON |

---

Last Updated: November 25, 2025
Status: ✅ All Tests Passing

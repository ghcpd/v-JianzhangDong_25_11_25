import os
import sys
import time
import platform
import requests
import subprocess
import signal
import pickle

ROOT = os.path.dirname(os.path.dirname(__file__))
SERVER_PY = os.path.join(ROOT, 'input.py')
LOGS_DIR = os.path.join(ROOT, 'logs')
# Allow overriding log path by env var; attempt to use stable path but avoid deleting if already open
default_log = os.environ.get('TEST_LOG_PATH', os.path.join(LOGS_DIR, 'test_run.log'))
TEST_LOG = default_log

def write_log(msg):
    try:
        with open(TEST_LOG, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        # If writing to main log fails, fallback to a per-process log
        alt = os.path.join(LOGS_DIR, f'test_run_{os.getpid()}.log')
        with open(alt, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')


def start_server():
    env = os.environ.copy()
    env['API_KEY'] = 'DUMMY'  # Set safe env var
    env['SECRET_KEY'] = 'dummy_secret'
    env['DEBUG'] = 'False'
    # If EXTERNAL_SERVER env var is set, assume the server is already running and just confirm it is reachable.
    if os.environ.get('EXTERNAL_SERVER', '').lower() in ('1', 'true', 'yes'):
        for _ in range(20):
            try:
                r = requests.get('http://127.0.0.1:5000/greet')
                if r.status_code == 200:
                    return None
            except Exception:
                time.sleep(0.5)
        raise RuntimeError('External server did not become ready')

    p = subprocess.Popen([sys.executable, SERVER_PY], env=env)
    # wait for server to be ready
    for _ in range(20):
        try:
            r = requests.get('http://127.0.0.1:5000/greet')
            if r.status_code == 200:
                return p
        except Exception:
            time.sleep(0.5)
    # could not reach server; kill process
    stop_server(p)
    raise RuntimeError('Server did not start')


def stop_server(p):
    try:
        if p is None:
            return
        if p.poll() is None:
            p.terminate()
            time.sleep(1)
            if p.poll() is None:
                p.kill()
    except Exception as e:
        write_log(f'Error stopping server: {e}')


def test_pickle_rce():
    # Construct a pickle payload that writes a file when loaded
    class RCE(object):
        def __reduce__(self):
            import os, platform
            if platform.system() == 'Windows':
                return (os.system, ("cmd.exe /c echo rce > pwned.txt",))
            return (os.system, ("/bin/sh -c 'echo rce > pwned.txt'",))

    payload = pickle.dumps(RCE())
    url = 'http://127.0.0.1:5000/upload_profile'
    headers = {'Content-Type': 'application/octet-stream'}
    try:
        r = requests.post(url, data=payload, headers=headers, timeout=5)
    except Exception as e:
        write_log(f'upload_profile request failed: {e}')
        return False
    time.sleep(0.5)
    if os.path.exists('pwned.txt'):
        write_log('VULN: Pickle RCE succeeded (pwned.txt created)')
        return False
    return True


def test_command_injection():
    # Platform-specific injection payloads
    if platform.system() == 'Windows':
        injection = '& echo rce > rce_cmd.txt'
    else:
        injection = '; touch rce_cmd.txt'
    url = 'http://127.0.0.1:5000/run'
    try:
        r = requests.post(url, data={'cmd': injection}, timeout=5)
    except Exception as e:
        write_log(f'run request failed: {e}')
        return False
    time.sleep(0.5)
    if os.path.exists('rce_cmd.txt'):
        write_log('VULN: Command injection succeeded (rce_cmd.txt created)')
        return False
    return True


def test_template_injection():
    url = 'http://127.0.0.1:5000/greet?name={{7*7}}'
    r = requests.get(url, timeout=5)
    if '49' in r.text:
        write_log('VULN: Template injection rendered expression as 49')
        return False
    return True


def test_sql_injection():
    # Call /search endpoint with suspicious input; ensure we don't return extra users unexpectedly.
    url = 'http://127.0.0.1:5000/search?name=%27%20OR%20%271%27=%271'
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        write_log('Search endpoint error')
        return False
    data = r.json()
    # If injection succeeded, more than one user might be returned (depending on DB)
    if len(data) > 1:
        write_log('VULN: SQL injection returned multiple rows for payload')
        return False
    return True


def test_no_hardcoded_secrets():
    # Scan for obvious hardcoded secrets in input.py
    with open(SERVER_PY, 'r') as f:
        content = f.read()
    if 'AKIA_EXAMPLE_HARDCODED_KEY' in content or 'password123' in content:
        write_log('VULN: Found hardcoded secrets in input.py')
        return False
    return True


def main():
    os.makedirs(LOGS_DIR, exist_ok=True)
    # Try to create/truncate the log file; if it is locked, fall back to an alternate file
    try:
        with open(TEST_LOG, 'w', encoding='utf-8') as f:
            f.write('')
    except Exception:
        TEST_LOG = os.path.join(LOGS_DIR, f'test_run_{os.getpid()}.log')
        with open(TEST_LOG, 'w', encoding='utf-8') as f:
            f.write('')
    p = start_server()
    # Clean up exploit artifacts from prior runs
    for fname in ('pwned.txt', 'rce_cmd.txt'):
        try:
            if os.path.exists(fname):
                os.remove(fname)
        except Exception:
            pass
    write_log('Server started')
    tests = [
        ('pickle_rce', test_pickle_rce),
        ('command_injection', test_command_injection),
        ('template_injection', test_template_injection),
        ('sql_injection', test_sql_injection),
        ('no_hardcoded_secrets', test_no_hardcoded_secrets),
    ]
    all_ok = True
    try:
        for name, test_func in tests:
            ok = test_func()
            write_log(f'{name}: {"PASS" if ok else "FAIL"}')
            if not ok:
                all_ok = False
    finally:
        stop_server(p)
        # Clean up artifacts created by tests
        for fname in ('pwned.txt', 'rce_cmd.txt'):
            try:
                if os.path.exists(fname):
                    os.remove(fname)
            except Exception:
                pass
    if not all_ok:
        write_log('Some tests failed')
        sys.exit(1)
    write_log('All tests passed')
    sys.exit(0)


if __name__ == '__main__':
    main()

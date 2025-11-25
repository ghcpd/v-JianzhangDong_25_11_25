import os
import sqlite3
import pickle
import importlib
import time


def reload_module():
    # ensure fresh import of the app module
    if 'input' in globals():
        importlib.reload(input)
    else:
        import input
    return importlib.import_module('input')


def setup_users_db():
    if os.path.exists('users.db'):
        os.remove('users.db')
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)')
    cur.execute("INSERT INTO users (username) VALUES ('alice')")
    cur.execute("INSERT INTO users (username) VALUES ('bob')")
    conn.commit()
    conn.close()


def test_no_hardcoded_api_key():
    import re
    with open('input.py', 'r', encoding='utf-8') as f:
        src = f.read()
    # There should be no obvious hardcoded AWS style keys (AKIA_*)
    # And there should not be an assignment of API_KEY to a string literal in source
    assert 'AKIA_' not in src
    assert re.search(r"API_KEY\s*=\s*['\"]", src) is None


def test_sql_injection_prevented():
    setup_users_db()
    mod = reload_module()
    # Attempt a classical SQL injection that would return all rows if vulnerable
    res = mod.query_users_by_name("' OR '1'='1")
    # Secure behavior: literal search should not match and should return 0 rows
    assert isinstance(res, list)
    assert len(res) == 0


def test_pickled_upload_not_execute():
    # craft a malicious pickle payload that attempts to write a file
    class Expl(object):
        def __reduce__(self):
            return (os.system, ("echo PICKLE_PWN > pickle_exploit.txt",))

    payload = pickle.dumps(Expl())
    mod = reload_module()
    client = mod.app.test_client()
    # remove file if exists
    if os.path.exists('pickle_exploit.txt'):
        os.remove('pickle_exploit.txt')

    resp = client.post('/upload_profile', data=payload, content_type='application/octet-stream')
    # Give any executed process a moment
    time.sleep(0.1)
    # Secure behavior: the payload must NOT create the file
    assert not os.path.exists('pickle_exploit.txt')


def test_run_endpoint_no_command_execution():
    mod = reload_module()
    client = mod.app.test_client()
    if os.path.exists('cmd_exploit.txt'):
        os.remove('cmd_exploit.txt')

    # Try to craft a command that would create a file via shell
    cmd = "echo CMD_PWN > cmd_exploit.txt"
    resp = client.post('/run', data={'cmd': cmd})
    time.sleep(0.1)
    assert not os.path.exists('cmd_exploit.txt')


def test_xss_greet_escaped():
    mod = reload_module()
    client = mod.app.test_client()
    resp = client.get('/greet?name=<script>alert(1)</script>')
    # Secure: returned HTML should not contain raw <script> tag
    assert b'<script' not in resp.data


def test_passwords_hashed_and_debug_off():
    mod = reload_module()
    # passwords should not be in cleartext
    users = getattr(mod, 'USERS', {})
    for u, info in users.items():
        pw = info.get('password', '')
        # simple heuristic: hashed passwords contain salt/algorithm info
        assert pw and 'password123' not in pw

    # debug mode must be off in production
    assert not getattr(mod.app, 'debug', False)

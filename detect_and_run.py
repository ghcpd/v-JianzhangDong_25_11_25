import os
import platform
import subprocess
import sys


def is_docker():
    # crude check for running inside container
    try:
        if os.path.exists('/.dockerenv'):
            return True
        with open('/proc/1/cgroup', 'rt') as fh:
            return 'docker' in fh.read() or 'kubepods' in fh.read()
    except Exception:
        return False


def run_script(cmd):
    print('Running:', ' '.join(cmd))
    r = subprocess.run(cmd)
    sys.exit(r.returncode)


def main():
    system = platform.system().lower()
    if is_docker():
        print('Detected container environment; run tests inside container instead using Dockerfile')
    elif system == 'windows':
        run_script(['cmd', '/c', 'run_test.bat'])
    else:
        run_script(['bash', 'run_test.sh'])


if __name__ == '__main__':
    main()

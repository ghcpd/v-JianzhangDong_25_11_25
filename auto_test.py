import os
import sys
import platform
import subprocess

def main():
    system = platform.system()
    if system == 'Windows':
        runner = 'run_test.bat'
    else:
        runner = 'run_test.sh'
    rc = subprocess.call([os.path.join(os.getcwd(), runner)])
    sys.exit(rc)

if __name__ == '__main__':
    main()

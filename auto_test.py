import datetime
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_PATH = LOG_DIR / "test_run.log"


def is_docker() -> bool:
    return os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV") == "1"


def main():
    system = platform.system().lower()
    docker = is_docker()

    if system.startswith("win") and not docker:
        cmd = ["cmd", "/c", "run_test.bat"]
    else:
        cmd = ["sh", "run_test.sh"]

    LOG_PATH.parent.mkdir(exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        header = f"=== Test run {datetime.datetime.utcnow().isoformat()}Z (system={system}, docker={docker}) ===\n"
        log_file.write(header)
        log_file.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            log_file.write(line)
        retcode = proc.wait()
        log_file.write(f"Exit code: {retcode}\n\n")
    sys.exit(retcode)


if __name__ == "__main__":
    main()

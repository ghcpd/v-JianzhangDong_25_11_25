import os
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)


def is_docker() -> bool:
    # Common docker detection heuristics
    if Path("/.dockerenv").exists():
        return True
    cgroup = Path("/proc/1/cgroup")
    if cgroup.exists():
        try:
            text = cgroup.read_text()
            if "docker" in text or "kubepods" in text:
                return True
        except Exception:
            pass
    return False


def main():
    system = platform.system().lower()
    docker = is_docker()

    if system.startswith("windows"):
        script = ROOT / "run_test.bat"
        cmd = [str(script)]
    else:
        script = ROOT / "run_test.sh"
        cmd = ["bash", str(script)]

    if not script.exists():
        raise FileNotFoundError(f"Test script not found: {script}")

    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(ROOT))

    # Let platform-specific test script handle logging to logs/test_run.log to avoid Windows file lock contention.
    result = subprocess.run(cmd, cwd=ROOT, env=env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

"""Tools for the protein stability lab (used by runner_agent).

Gemini's built-in shell is blocked by the Antigravity SDK's default safety rule,
so the runner uses these two functions instead.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_MAX_OUT = 8000
_WORKDIR = Path("lab_runs")


def _clip(text: str) -> str:
    if len(text) <= _MAX_OUT:
        return text
    half = _MAX_OUT // 2
    return text[:half] + "\n...[output clipped]...\n" + text[-half:]


def run_python(code: str, timeout_seconds: int = 900) -> str:
    """Run a Python script and return its exit code, stdout and stderr.

    The script is saved under ./lab_runs/ so every run is kept as a record.
    """
    _WORKDIR.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", dir=_WORKDIR, delete=False, encoding="utf-8"
    ) as fh:
        fh.write(code)
        path = fh.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=int(timeout_seconds),
        )
    except subprocess.TimeoutExpired:
        return f"TIMEOUT after {timeout_seconds}s (script saved at {path})"
    return (
        f"script: {path}\nexit_code: {proc.returncode}\n"
        f"--- stdout ---\n{_clip(proc.stdout)}\n--- stderr ---\n{_clip(proc.stderr)}"
    )


_PKG_OK = re.compile(r"^[A-Za-z0-9_.\-\[\]=<>,]+$")


def pip_install(packages: str) -> str:
    """Install Python packages (space-separated), e.g. 'torch transformers pandas'."""
    names = packages.split()
    if not names:
        return "No packages given."
    for n in names:
        if not _PKG_OK.match(n) or n.startswith("-"):
            return f"Refused: '{n}' is not a plain package name."
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", *names],
        capture_output=True,
        text=True,
        timeout=1800,
    )
    return f"exit_code: {proc.returncode}\n{_clip(proc.stdout[-3000:])}\n{_clip(proc.stderr[-3000:])}"

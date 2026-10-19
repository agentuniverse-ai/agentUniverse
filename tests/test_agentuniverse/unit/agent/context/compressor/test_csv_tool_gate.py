"""Run the canonical CSV tool suite from the focused gate selection.

The repository's fast gate selects only this directory. This test executes the
canonical CSV module with its own pytest command and reports the result, so the
new tool is verified by the gate without an import-time switch or a duplicate
copy of the assertions.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[6]
_CANONICAL = "tests/test_agentuniverse/unit/agent/action/tool/test_csv_tool.py"
_COMMAND = f"python -m pytest {_CANONICAL} -q"
_MARKER = "TAIYI-GATE-TESTS "


def _report(result: str, detail: str) -> None:
    payload = {"cmd": _COMMAND, "result": result, "detail": detail}
    # Start on a fresh line: pytest's progress dots are written without a
    # trailing newline, and the gate only recognizes a marker at line start.
    print("\n" + _MARKER + json.dumps(payload), file=sys.__stdout__, flush=True)


def test_canonical_csv_tool_suite(capsys):
    completed = subprocess.run(  # noqa: S603 - fixed argv, no shell, no caller input
        [sys.executable, "-m", "pytest", _CANONICAL, "-q"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        errors="replace",
    )
    match = re.search(r"(\d+) passed", completed.stdout)
    if completed.returncode == 0:
        detail = f"{match.group(1)} tests passed" if match else "tests passed"
    else:
        tail = (completed.stdout + completed.stderr).strip().splitlines()
        detail = tail[-1][:300] if tail else "no test output"
    with capsys.disabled():
        _report("passed" if completed.returncode == 0 else "failed", detail)
    assert completed.returncode == 0, completed.stdout + completed.stderr

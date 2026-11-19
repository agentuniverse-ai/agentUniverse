# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def _run_platform_import(cwd: Path) -> list[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(REPO_ROOT), env.get("PYTHONPATH", "")]
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import platform; "
                "print(platform.__file__); "
                "print(platform.python_implementation())"
            ),
        ],
        cwd=str(cwd),
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().splitlines()


def test_example_app_root_imports_stdlib_platform():
    app_root = REPO_ROOT / "examples" / "sample_apps" / "react_agent_app"

    output = _run_platform_import(app_root)

    assert Path(output[0]).name == "platform.py"
    assert str(app_root / "platform") not in output[0]
    assert output[1]


def test_example_bootstrap_root_imports_stdlib_platform():
    bootstrap_root = (
        REPO_ROOT / "examples" / "sample_apps" / "react_agent_app" / "bootstrap"
    )

    output = _run_platform_import(bootstrap_root)

    assert Path(output[0]).name == "platform.py"
    assert str(bootstrap_root / "platform") not in output[0]
    assert output[1]

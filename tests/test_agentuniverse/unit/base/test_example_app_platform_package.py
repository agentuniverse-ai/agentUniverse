import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]

EXPECTED_PLATFORM_PATHS = (
    Path("examples/sample_apps/basic_sop_app/platform"),
    Path("examples/sample_apps/difizen_app/platform"),
    Path("examples/sample_apps/openai_protocol_app/platform"),
    Path("examples/sample_apps/peer_agent_app/platform"),
    Path("examples/sample_apps/rag_app/platform"),
    Path("examples/sample_apps/react_agent_app/platform"),
    Path("examples/sample_apps/toolkit_demo_app/platform"),
    Path("examples/sample_apps/workflow_agent_app/platform"),
    Path("examples/third_party_examples/apps/" "medical_consultation_assistant_app/platform"),
)

COLLISION_CHECK = """\
import platform
import sysconfig
from pathlib import Path

stdlib_platform = Path(sysconfig.get_path("stdlib")) / "platform.py"
assert Path(platform.__file__).resolve() == stdlib_platform.resolve(), platform.__file__
assert platform.python_implementation()
"""


def _discover_platform_paths() -> set[Path]:
    search_roots = (
        REPO_ROOT / "examples/sample_apps",
        REPO_ROOT / "examples/third_party_examples/apps",
    )
    return {
        platform_path.relative_to(REPO_ROOT)
        for search_root in search_roots
        for platform_path in search_root.glob("*/platform")
        if platform_path.is_dir()
    }


def _run_python(code: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _assert_process_succeeded(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, (
        f"returncode: {result.returncode}\n" f"stdout:\n{result.stdout}\n" f"stderr:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "relative_platform_path",
    EXPECTED_PLATFORM_PATHS,
    ids=lambda path: path.parent.name,
)
def test_example_app_does_not_shadow_stdlib_platform(
    relative_platform_path: Path,
) -> None:
    assert _discover_platform_paths() == set(EXPECTED_PLATFORM_PATHS)

    app_root = REPO_ROOT / relative_platform_path.parent
    result = _run_python(COLLISION_CHECK, cwd=app_root)

    _assert_process_succeeded(result)


@pytest.mark.parametrize(
    "relative_platform_path",
    EXPECTED_PLATFORM_PATHS,
    ids=lambda path: path.parent.name,
)
def test_example_app_platform_namespace_remains_importable(
    relative_platform_path: Path,
) -> None:
    app_root = REPO_ROOT / relative_platform_path.parent
    directory_name = app_root.name
    product_module = f"{directory_name}.platform.difizen.product"
    workflow_module = f"{directory_name}.platform.difizen.workflow"
    code = (
        "import importlib\n"
        f"importlib.import_module({product_module!r})\n"
        f"importlib.import_module({workflow_module!r})\n"
    )

    result = _run_python(code, cwd=app_root.parent)

    _assert_process_succeeded(result)

from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_PATH = REPOSITORY_ROOT / ".github/workflows/ci.yml"


def test_core_ci_workflow_contract():
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    triggers = workflow.get("on", workflow.get(True))

    assert workflow["permissions"] == {"contents": "read"}
    assert "pull_request" in triggers
    assert triggers["push"]["branches"] == ["master"]
    assert workflow["concurrency"]["cancel-in-progress"] is True

    core_job = workflow["jobs"]["core"]
    assert core_job["runs-on"] == "ubuntu-latest"
    steps = core_job["steps"]
    assert steps[0]["uses"] == "actions/checkout@v7"
    assert steps[1]["uses"] == "actions/setup-python@v6"
    assert steps[1]["with"]["python-version"] == "3.10"
    assert steps[1]["with"]["cache"] == "pip"

    run_commands = "\n".join(step.get("run", "") for step in steps)
    for package_path in (
        "agentuniverse",
        "agentuniverse_connector",
        "agentuniverse_extension",
        "agentuniverse_product",
    ):
        assert package_path in run_commands
    assert "tests/test_agentuniverse/unit/base/annotation/test_trace.py" in run_commands
    assert "tests/test_agentuniverse/unit/base/context/test_framework_context.py" in run_commands

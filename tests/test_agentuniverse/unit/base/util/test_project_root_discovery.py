from pathlib import Path

from agentuniverse.base.util import system_util


def test_project_root_discovery_handles_root_and_nested_working_directories(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    nested_working_directory = project_root / "app" / "intelligence" / "agentic"
    (project_root / "config").mkdir(parents=True)
    nested_working_directory.mkdir(parents=True)

    monkeypatch.setattr(
        system_util.Path,
        "cwd",
        classmethod(lambda cls: nested_working_directory),
    )
    monkeypatch.setattr(system_util, "PROJECT_ROOT_PATH", None)

    assert system_util.get_project_root_path() == Path(project_root)

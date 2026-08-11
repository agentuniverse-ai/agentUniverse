from pathlib import Path

from agentuniverse.base.util import system_util


def test_explicit_config_path_determines_project_root_independent_of_cwd(tmp_path, monkeypatch):
    app_root = tmp_path / "sample_app"
    config_path = app_root / "config" / "config.toml"
    config_path.parent.mkdir(parents=True)
    config_path.touch()
    unrelated_cwd = tmp_path / "elsewhere" / "nested"
    unrelated_cwd.mkdir(parents=True)
    monkeypatch.chdir(unrelated_cwd)
    monkeypatch.setattr(system_util, "PROJECT_ROOT_PATH", None)

    resolved_root = system_util.get_project_root_path(config_path)

    assert resolved_root == app_root.resolve()
    assert system_util.get_project_root_path() == app_root.resolve()


def test_project_root_without_config_keeps_cwd_fallback(tmp_path, monkeypatch):
    working_directory = tmp_path / "app" / "intelligence" / "test"
    working_directory.mkdir(parents=True)
    monkeypatch.chdir(working_directory)
    monkeypatch.setattr(system_util, "PROJECT_ROOT_PATH", None)

    assert system_util.get_project_root_path() == Path.cwd().parents[1]

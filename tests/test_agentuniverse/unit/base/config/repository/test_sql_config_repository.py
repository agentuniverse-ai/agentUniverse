import pytest
from sqlalchemy import create_engine

from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.repository import (
    ConfigConflictError,
    ConfigNotFoundError,
    LayeredConfigResolver,
    SQLConfigRepository,
    export_yaml_directory,
    import_yaml_files,
    merge_repository_configers,
)


@pytest.fixture
def repo(tmp_path):
    return SQLConfigRepository(create_engine(f"sqlite:///{tmp_path / 'config.db'}"))


def test_create_update_history_and_optimistic_lock(repo):
    first = repo.put("TOOL", "search", {"name": "search", "timeout": 3}, expected_revision=0, updated_by="alice")
    second = repo.put("TOOL", "search", {"name": "search", "timeout": 5}, expected_revision=1, updated_by="bob")
    assert (first.revision, second.revision) == (1, 2)
    assert [item.value["timeout"] for item in repo.history("TOOL", "search")] == [3, 5]
    with pytest.raises(ConfigConflictError, match="expected revision"):
        repo.put("TOOL", "search", {"timeout": 9}, expected_revision=1)
    assert repo.get("TOOL", "search").value["timeout"] == 5


def test_rollback_creates_auditable_new_revision(repo):
    repo.put("LLM", "model", {"temperature": 0.1})
    repo.put("LLM", "model", {"temperature": 0.9})
    rolled = repo.rollback("LLM", "model", 1, expected_revision=2, updated_by="operator")
    assert rolled.revision == 3 and rolled.value == {"temperature": 0.1}
    assert len(repo.history("LLM", "model")) == 3


def test_environments_are_isolated_and_export_is_deterministic(repo):
    repo.put("AGENT", "a", {"name": "dev"}, environment="dev")
    repo.put("AGENT", "a", {"name": "prod"}, environment="prod")
    assert repo.get("AGENT", "a", "dev").value["name"] == "dev"
    assert [item["environment"] for item in repo.export()] == ["dev", "prod"]


def test_raw_secrets_are_rejected_but_references_are_allowed(repo):
    with pytest.raises(ValueError, match="secret_ref"):
        repo.put("LLM", "x", {"api_key": "raw"})
    record = repo.put("LLM", "x", {"api_key": {"secret_ref": "env://OPENAI_API_KEY"}})
    assert record.value["api_key"]["secret_ref"].startswith("env://")
    placeholder = repo.put("LLM", "placeholder", {"api_key": "${OPENAI_API_KEY}"})
    assert placeholder.value["api_key"] == "${OPENAI_API_KEY}"
    ordinary = repo.put("LLM", "ordinary", {"max_tokens": 4096})
    assert ordinary.value["max_tokens"] == 4096


def test_repository_record_becomes_existing_configer(repo):
    repo.put("TOOL", "search", {"name": "search", "metadata": {"type": "TOOL"}})
    configer = repo.as_configer("TOOL", "search")
    assert configer.path == "db://default/TOOL/search@1"
    assert configer.value["name"] == "search"


def test_layered_precedence_and_copy_isolation():
    resolver = LayeredConfigResolver()
    result = resolver.resolve(
        defaults={"timeout": 1, "nested": {"a": 1, "b": 1}},
        yaml={"nested": {"b": 2}}, database={"timeout": 3}, runtime={"nested": {"a": 4}},
    )
    assert result == {"timeout": 3, "nested": {"a": 4, "b": 2}}


def test_list_delete_and_delete_audit(repo):
    repo.put("TOOL", "b", {"name": "b"})
    repo.put("TOOL", "a", {"name": "a"})
    assert [record.name for record in repo.list("TOOL")] == ["a", "b"]
    repo.delete("TOOL", "a", expected_revision=1, updated_by="operator")
    with pytest.raises(ConfigNotFoundError):
        repo.get("TOOL", "a")
    history = repo.history("TOOL", "a")
    assert [record.revision for record in history] == [1, 2]
    recreated = repo.put("TOOL", "a", {"name": "a2"}, expected_revision=0)
    assert recreated.revision == 3
    with pytest.raises(ConfigConflictError):
        repo.delete("TOOL", "b", expected_revision=9)


def test_database_overlay_and_database_only_component(repo, monkeypatch, tmp_path):
    yaml_configer = Configer(path=str(tmp_path / "search.yaml"))
    yaml_configer.value = {
        "name": "search", "timeout": 3, "nested": {"keep": True},
        "metadata": {"type": "TOOL", "module": "pkg.tool", "class": "Search"},
    }
    repo.put("TOOL", "search", {"timeout": 8, "nested": {"db": True}})
    repo.put("TOOL", "database_only", {
        "description": "from db",
        "metadata": {"type": "TOOL", "module": "pkg.tool", "class": "Search"},
    })
    merged = merge_repository_configers([yaml_configer], repo, "TOOL")
    assert [item.value["name"] for item in merged] == ["search", "database_only"]
    assert merged[0].value["timeout"] == 8
    assert merged[0].value["nested"] == {"keep": True, "db": True}
    assert merged[0].path == "db://default/TOOL/search@1"

    monkeypatch.setenv("DB_MODEL", "resolved-model")
    repo.put("LLM", "model", {
        "model_name": "${DB_MODEL}",
        "metadata": {"type": "LLM"},
    })
    assert merge_repository_configers([], repo, "LLM")[0].value["model_name"] == "resolved-model"


def test_database_metadata_type_must_match_repository_key(repo):
    repo.put("TOOL", "bad", {"metadata": {"type": "LLM"}})
    with pytest.raises(ValueError, match=r"metadata\.type=LLM"):
        merge_repository_configers([], repo, "TOOL")


def test_yaml_migration_round_trip_and_dry_run(repo, tmp_path):
    source = tmp_path / "search.yaml"
    source.write_text(
        "name: search\napi_key: '${SEARCH_KEY}'\n"
        "metadata:\n  type: TOOL\n  module: pkg.tool\n  class: Search\n",
        encoding="utf-8",
    )
    report = import_yaml_files(repo, [source], environment="staging")
    assert report.imported == ["TOOL/search"] and not report.errors
    assert repo.get("TOOL", "search", "staging").value["api_key"] == "${SEARCH_KEY}"

    skipped = import_yaml_files(repo, [source], environment="staging")
    assert skipped.skipped == ["TOOL/search"]
    output = export_yaml_directory(repo, tmp_path / "export", environment="staging")
    assert output == [tmp_path / "export" / "tool" / "search.yaml"]
    assert "${SEARCH_KEY}" in output[0].read_text(encoding="utf-8")

    dry_repo = SQLConfigRepository(create_engine("sqlite:///:memory:"))
    dry = import_yaml_files(dry_repo, [source], dry_run=True)
    assert dry.imported == ["TOOL/search"] and dry_repo.list() == []

"""Real Git fixtures: committed content is independent of the dirty worktree."""

import hashlib
import json
import shutil
import stat
import subprocess
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.reader.file.git_snapshot_reader import GitSnapshotReader


@pytest.fixture(scope="module", autouse=True)
def supported_git():
    if not shutil.which("git"):
        pytest.skip("real Git executable required")
    probe = subprocess.run(["git", "--no-lazy-fetch", "--version"], capture_output=True, timeout=10)
    if probe.returncode:
        pytest.skip("Git with --no-lazy-fetch support required for snapshot integration tests")


def git(repo, *arguments, data=None):
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "core.autocrlf=false", *arguments],
        input=data,
        capture_output=True,
        check=True,
        timeout=15,
    ).stdout


def commit(repo):
    git(repo, "add", ".")
    git(
        repo,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-qm",
        "fixture",
    )
    return git(repo, "rev-parse", "HEAD").decode().strip()


@pytest.fixture
def repository(tmp_path):
    if not shutil.which("git"):
        pytest.skip("real Git executable required")
    repo = tmp_path / "repository"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "manual.txt").write_bytes(b"alpha\r\nbeta\nlast")
    (repo / "readme.md").write_text("Unicode \u4e2d\u6587\n", encoding="utf-8")
    return repo, commit(repo)


def test_committed_bytes_lines_and_stable_ids_ignore_dirty_worktree(repository):
    repo, revision = repository
    (repo / "manual.txt").write_text("DIRTY", encoding="utf-8")
    (repo / "untracked.txt").write_text("untracked", encoding="utf-8")
    index_before = (repo / ".git" / "index").read_bytes()
    head_before = (repo / ".git" / "HEAD").read_bytes()
    reader = GitSnapshotReader(lines_per_document=2)
    result = reader.read_snapshot(repo, revision, "fixture/repo")
    chunks = [doc for doc in result.documents if doc.metadata["file_name"] == "manual.txt"]
    assert [doc.text for doc in chunks] == ["alpha\r\nbeta\n", "last"]
    assert [
        (doc.metadata["git_snapshot"]["start_line"], doc.metadata["git_snapshot"]["end_line"]) for doc in chunks
    ] == [(1, 2), (3, 3)]
    for doc in chunks:
        meta = doc.metadata["git_snapshot"]
        assert meta["blob"] == git(repo, "rev-parse", revision + ":manual.txt").decode().strip()
        assert meta["commit"] == revision and meta["repository_id"] == "fixture/repo"
    again = reader.read_snapshot(repo, revision.upper(), "fixture/repo")
    assert [d.model_dump() for d in again.documents] == [d.model_dump() for d in result.documents]
    assert (repo / ".git" / "index").read_bytes() == index_before
    assert (repo / ".git" / "HEAD").read_bytes() == head_before
    assert (repo / "manual.txt").read_text() == "DIRTY"
    assert all("untracked" not in doc.text for doc in result.documents)


def test_rename_old_commit_missing_worktree_and_bare_repository(repository, tmp_path):
    repo, old = repository
    git(repo, "mv", "manual.txt", "renamed.txt")
    new = commit(repo)
    reader = GitSnapshotReader(include=["*.txt"])
    assert reader.read_snapshot(repo, old, "repo").documents[0].metadata["git_snapshot"]["path"] == "manual.txt"
    assert reader.read_snapshot(repo, new, "repo").documents[0].metadata["git_snapshot"]["path"] == "renamed.txt"
    # Bare clone has no checkout at all; use only this test-created local repository.
    bare = tmp_path / "bare.git"
    git(repo, "clone", "--bare", "--quiet", str(repo), str(bare))
    expected = reader.read_snapshot(repo, old, "repo")
    actual = reader.read_snapshot(bare, old, "repo")
    assert [d.model_dump() for d in actual.documents] == [d.model_dump() for d in expected.documents]


def test_exclusions_binary_lfs_empty_and_invalid_utf8_are_explicit(repository):
    repo, _ = repository
    for name, content in {
        "binary.txt": b"a\x00b",
        "legacy.txt": b"\xff",
        "empty.txt": b"",
        "model.txt": b"version https://git-lfs.github.com/spec/v1\noid sha256:123\nsize 4\n",
        "private.key": b"fixture only",
        ".env": b"fixture only",
    }.items():
        (repo / name).write_bytes(content)
    revision = commit(repo)
    result = GitSnapshotReader(include=["*"]).read_snapshot(repo, revision, "repo")
    reasons = {item["path"]: item["reason"] for item in result.skipped}
    assert reasons == {
        "binary.txt": "binary",
        "legacy.txt": "non_utf8_content",
        "empty.txt": "empty",
        "model.txt": "lfs_pointer",
        "private.key": "excluded",
        ".env": "excluded",
    }
    assert len(result.documents) == 2
    assert result.documents[0].metadata["git_snapshot"]["skipped_counts"]["excluded"] == 2


def test_symlink_and_submodule_entries_are_not_followed(repository):
    repo, old = repository
    oid = git(repo, "hash-object", "-w", "--stdin", data=b"manual.txt").decode().strip()
    git(repo, "update-index", "--add", "--cacheinfo", "120000," + oid + ",link.txt")
    git(repo, "update-index", "--add", "--cacheinfo", "160000," + old + ",module.txt")
    git(
        repo,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-qm",
        "links",
    )
    revision = git(repo, "rev-parse", "HEAD").decode().strip()
    result = GitSnapshotReader().read_snapshot(repo, revision, "repo")
    assert {item["path"]: item["reason"] for item in result.skipped} == {
        "link.txt": "symlink_or_submodule",
        "module.txt": "symlink_or_submodule",
    }


def test_replacement_refs_do_not_change_pinned_content(repository):
    repo, old = repository
    (repo / "manual.txt").write_text("new content", encoding="utf-8")
    new = commit(repo)
    git(repo, "replace", old, new)
    result = GitSnapshotReader(include=["manual.txt"]).read_snapshot(repo, old, "repo")
    assert result.documents[0].text == "alpha\r\nbeta\nlast"


@pytest.mark.parametrize(
    "options",
    [
        {"max_blob_bytes": 1},
        {"max_total_bytes": 1},
        {"max_tree_bytes": 1},
        {"max_files": 1},
        {"max_documents": 1, "lines_per_document": 1},
    ],
)
def test_limits_fail_without_partial_result(repository, options):
    repo, revision = repository
    with pytest.raises(ValueError, match="budget|exceeds"):
        GitSnapshotReader(**options).read_snapshot(repo, revision, "repo")


@pytest.mark.parametrize("revision", ["HEAD", "main", "1234567", "--help", "0" * 39])
def test_requires_full_commit_id(repository, revision):
    repo, _ = repository
    with patch("subprocess.Popen") as process, pytest.raises(ValueError, match="full"):
        GitSnapshotReader().read_snapshot(repo, revision, "repo")
    process.assert_not_called()


def test_missing_object_and_annotated_tag_are_errors(repository):
    repo, revision = repository
    with pytest.raises(RuntimeError, match="availability"):
        GitSnapshotReader().read_snapshot(repo, "0" * 40, "repo")
    git(
        repo,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "tag",
        "-a",
        "fixture-tag",
        "-m",
        "tag",
        revision,
    )
    tag = git(repo, "rev-parse", "fixture-tag").decode().strip()
    with pytest.raises(ValueError, match="annotated tag"):
        GitSnapshotReader().read_snapshot(repo, tag, "repo")


def test_environment_isolation_and_no_lazy_fetch_option(repository, monkeypatch):
    repo, revision = repository
    monkeypatch.setenv("GIT_DIR", "/not-the-repository")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.bare")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")
    real_popen = subprocess.Popen
    observed = []

    def capture(args, **kwargs):
        observed.append((args, kwargs["env"]))
        return real_popen(args, **kwargs)

    with patch("subprocess.Popen", side_effect=capture):
        assert GitSnapshotReader().read_snapshot(repo, revision, "repo").documents
    for command, environment in observed:
        assert "--no-lazy-fetch" in command and "--no-replace-objects" in command
        assert environment["GIT_ALLOW_PROTOCOL"] == ""
        assert "GIT_DIR" not in environment and "GIT_CONFIG_COUNT" not in environment


def test_total_deadline_checked_before_process(repository):
    repo, _ = repository
    with patch("subprocess.Popen") as process, pytest.raises(TimeoutError):
        GitSnapshotReader()._run_git(repo, ["--version"], 100, time.monotonic() - 1)
    process.assert_not_called()


def test_manifest_relative_repository_and_no_provenance_override(repository, tmp_path):
    repo, revision = repository
    manifest = tmp_path / "source.gitsnapshot"
    manifest.write_text(
        json.dumps({"repository_path": repo.name, "commit": revision, "repository_id": "repo"}), encoding="utf-8"
    )
    reader = GitSnapshotReader()
    assert reader.load_data(manifest)[0].metadata["git_snapshot"]["commit"] == revision
    with pytest.raises(ValueError, match="provenance"):
        reader.load_data(manifest, ext_info={"commit": "other"})
    manifest.write_text('{"commit":"a","commit":"b"}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        reader.load_data(manifest)
    manifest.write_text(" " * 8193, encoding="utf-8")
    with pytest.raises(ValueError, match="8192"):
        reader.load_data(manifest)


def test_sha256_repository(tmp_path):
    repo = tmp_path / "sha256"
    repo.mkdir()
    git(repo, "init", "--object-format=sha256", "-q")
    (repo / "manual.txt").write_bytes(b"alpha\n")
    revision = commit(repo)
    result = GitSnapshotReader().read_snapshot(repo, revision, "sha256")
    assert len(revision) == 64
    assert result.documents[0].metadata["git_snapshot"]["blob"] == hashlib.sha256(b"blob 6\x00alpha\n").hexdigest()


def test_unicode_path_and_lf_line_numbers(repository):
    repo, _ = repository
    (repo / "\u4e2d\u6587 notes.txt").write_bytes("one\u2028same Git line\n\nlast\n".encode())
    revision = commit(repo)
    result = GitSnapshotReader(include=["\u4e2d\u6587*"], lines_per_document=1).read_snapshot(repo, revision, "repo")
    assert [doc.text for doc in result.documents] == ["one\u2028same Git line\n", "\n", "last\n"]
    assert [doc.metadata["git_snapshot"]["start_line"] for doc in result.documents] == [1, 2, 3]


def test_selected_missing_blob_fails_instead_of_partial_documents(repository):
    repo, revision = repository
    blob = git(repo, "rev-parse", revision + ":manual.txt").decode().strip()
    object_path = repo / ".git" / "objects" / blob[:2] / blob[2:]
    assert object_path.resolve().is_relative_to(repo.resolve())
    # Only this disposable pytest fixture object is removed.
    object_path.chmod(stat.S_IREAD | stat.S_IWRITE)
    object_path.unlink()
    with pytest.raises(RuntimeError, match="unavailable|availability"):
        GitSnapshotReader().read_snapshot(repo, revision, "repo")


def test_timer_kills_and_reaps_process(repository):
    from unittest.mock import MagicMock

    repo, _ = repository
    process = MagicMock()
    process.__enter__.return_value = process
    process.stdout.read.return_value = b""
    process.wait.return_value = -9
    process.poll.return_value = -9
    timer = MagicMock()

    def immediate_timer(seconds, callback):
        timer.start.side_effect = callback
        return timer

    with patch("subprocess.Popen", return_value=process), patch("threading.Timer", side_effect=immediate_timer):
        with pytest.raises(TimeoutError, match="timed out"):
            GitSnapshotReader()._run_git(repo, ["--version"], 100, time.monotonic() + 10)
    process.kill.assert_called_once()
    assert process.wait.call_count >= 1
    timer.cancel.assert_called_once()


def test_real_yaml_public_knowledge_sqlite_roundtrip(repository, tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    repo, revision = repository
    managers = [ReaderManager(), StoreManager(), RagRouterManager(), DocProcessorManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    knowledge, store = None, None
    try:
        app = Configer()
        app.value = {"BASE_INFO": {"appname": "git-snapshot-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        copied = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/file/git_snapshot_reader.yaml.example", copied
        )
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        reader = GitSnapshotReader().initialize_by_component_configer(config)
        assert config.get_component_config_type() == "READER"
        store = SQLiteStore(name="snapshot_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="keywords")
        store._new_client()
        components = [reader, store, BaseRouter(name="base_router"), JiebaKeywordExtractor(name="keywords", top_k=20)]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        manifest = tmp_path / "source.gitsnapshot"
        manifest.write_text(
            json.dumps({"repository_path": str(repo), "commit": revision, "repository_id": "repo"}), encoding="utf-8"
        )
        original = manifest.read_bytes()
        knowledge = Knowledge(stores=["snapshot_store"], readers={"gitsnapshot": "git_snapshot_reader"})
        knowledge.insert_knowledge(source_path=str(manifest))
        assert store.conn.execute("SELECT count(*) FROM documents").fetchone()[0] == 2
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            results = knowledge.query_knowledge(query_str="alpha")
        assert len(results) == 1 and results[0].text == "alpha\r\nbeta\nlast"
        assert results[0].metadata["git_snapshot"]["commit"] == revision
        assert results[0].metadata["git_snapshot"]["path"] == "manual.txt"
        assert manifest.read_bytes() == original
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store is not None and store.conn is not None:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous

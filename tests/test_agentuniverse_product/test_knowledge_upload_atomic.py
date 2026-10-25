"""Knowledge upload must preserve an existing file if transfer fails."""

import io
import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentuniverse_product.service.knowledge_service import knowledge_service as module


class FailingReader:
    def __init__(self):
        self.reads = 0

    def read(self, _size):
        self.reads += 1
        if self.reads == 1:
            return b"partial replacement"
        raise OSError("upload interrupted")


def prepare_upload(monkeypatch, tmp_path: Path):
    core = tmp_path / "core"
    (core / "store").mkdir(parents=True)
    (core / "store" / "safe_store.yaml").write_text("already configured", encoding="utf-8")
    resources = tmp_path / "resources"
    resources.mkdir()
    imported = []
    knowledge = SimpleNamespace(
        stores=[],
        insert_knowledge=lambda *, source_path, stores: imported.append(Path(source_path).read_bytes()),
    )
    manager = SimpleNamespace(get_instance_obj=lambda **_kwargs: knowledge)
    monkeypatch.setattr(module, "KnowledgeManager", lambda: manager)
    monkeypatch.setattr(module, "get_core_path", lambda: core)
    monkeypatch.setattr(module, "get_resources_path", lambda: resources)
    return resources, imported


def test_interrupted_upload_preserves_existing_file(monkeypatch, tmp_path):
    resources, imported = prepare_upload(monkeypatch, tmp_path)
    destination = resources / "report.txt"
    destination.write_bytes(b"keep original")

    with pytest.raises(OSError, match="upload interrupted"):
        module.KnowledgeService.upload_knowledge_file(
            "safe", SimpleNamespace(filename="report.txt", file=FailingReader())
        )

    assert destination.read_bytes() == b"keep original"
    assert imported == []
    assert sorted(path.name for path in resources.iterdir()) == ["report.txt"]


def test_successful_upload_replaces_file_before_import(monkeypatch, tmp_path):
    resources, imported = prepare_upload(monkeypatch, tmp_path)
    (resources / "report.txt").write_bytes(b"old")

    assert module.KnowledgeService.upload_knowledge_file(
        "safe", SimpleNamespace(filename="report.txt", file=io.BytesIO(b"new"))
    )
    assert (resources / "report.txt").read_bytes() == b"new"
    assert imported == [b"new"]


def test_failed_replace_cleans_up_temporary_file(monkeypatch, tmp_path):
    resources, imported = prepare_upload(monkeypatch, tmp_path)
    destination = resources / "report.txt"
    destination.write_bytes(b"old")
    def fail_replace(*_args):
        raise OSError("replace failed")

    monkeypatch.setattr(module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        module.KnowledgeService.upload_knowledge_file(
            "safe", SimpleNamespace(filename="report.txt", file=io.BytesIO(b"new"))
        )

    assert destination.read_bytes() == b"old"
    assert imported == []
    assert sorted(path.name for path in resources.iterdir()) == ["report.txt"]


def test_replacing_upload_preserves_existing_file_mode(monkeypatch, tmp_path):
    resources, imported = prepare_upload(monkeypatch, tmp_path)
    destination = resources / "report.txt"
    destination.write_bytes(b"old")
    os.chmod(destination, stat.S_IRUSR | stat.S_IWUSR)
    original_mode = stat.S_IMODE(destination.stat().st_mode)

    assert module.KnowledgeService.upload_knowledge_file(
        "safe", SimpleNamespace(filename="report.txt", file=io.BytesIO(b"new"))
    )

    assert stat.S_IMODE(destination.stat().st_mode) == original_mode
    assert imported == [b"new"]

"""Real archive loads must have independent per-call resource budgets."""
from concurrent.futures import ThreadPoolExecutor
import io
from threading import Barrier, Event
import zipfile

import pytest

from agentuniverse.agent.action.knowledge.reader.file.zip_reader import ZipReader


def _archive(path, entries):
    """Write a real, uncompressed archive and return its path."""
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in entries:
            archive.writestr(name, content)
    return path


@pytest.mark.parametrize("limits", [{"max_files": 1}, {"max_total_size": 5}])
def test_concurrent_valid_archives_keep_separate_budgets(
        tmp_path, monkeypatch, limits):
    """Two legal reads on one component must both succeed independently."""
    paths = [_archive(tmp_path / f"{name}.zip", [(f"{name}.json", value)])
             for name, value in [("left", '"one"'), ("right", '"two"')]]
    reader = ZipReader(**limits)
    ready = Barrier(2)
    original = ZipReader._iterate_archive

    def start_together(self, *args):
        # Pause only the two root calls after initialization; real parsing,
        # budget checks, document construction and metadata remain unchanged.
        if args[4] == 0:
            ready.wait(timeout=5)
        return original(self, *args)

    monkeypatch.setattr(ZipReader, "_iterate_archive", start_together)
    with ThreadPoolExecutor(max_workers=2) as executor:
        jobs = [executor.submit(reader.load_data, path,
                                ext_info={"request": path.stem})
                for path in paths]
        results = [job.result(timeout=10) for job in jobs]

    assert [docs[0].text for docs in results] == ['"one"', '"two"']
    for path, docs in zip(paths, results):
        assert len(docs) == 1
        assert docs[0].metadata["request"] == path.stem
        assert docs[0].metadata["archive_root"] == path.name
        assert docs[0].metadata["archive_path"] == f"{path.stem}.json"


@pytest.mark.parametrize("limits, message", [
    ({"max_files": 1}, "maximum file count"),
    ({"max_total_size": 5}, "maximum total size"),
])
def test_second_load_cannot_reset_an_active_archive_budget(
        tmp_path, monkeypatch, limits, message):
    """A concurrent empty archive must not let an over-limit read pass."""
    oversized = _archive(tmp_path / "oversized.zip", [
        ("first.json", '"one"'), ("second.json", '"two"')])
    empty = _archive(tmp_path / "empty.zip", [])
    reader = ZipReader(**limits)
    first_counted = Event()
    resume = Event()
    original = ZipReader._enforce_limits

    def pause_after_first_member(self, info):
        original(self, info)
        if info.filename == "first.json":
            first_counted.set()
            assert resume.wait(timeout=5)

    monkeypatch.setattr(ZipReader, "_enforce_limits", pause_after_first_member)
    with ThreadPoolExecutor(max_workers=1) as executor:
        job = executor.submit(reader.load_data, oversized)
        try:
            assert first_counted.wait(timeout=5)
            assert reader.load_data(empty) == []
        finally:
            resume.set()
        with pytest.raises(ValueError, match=message):
            job.result(timeout=10)


def _nested_archive(tmp_path):
    """Build two text documents spread across one root and one nested ZIP."""
    buffer = io.BytesIO()
    _archive(buffer, [("inner.json", '"two"')])
    nested = buffer.getvalue()
    path = _archive(tmp_path / "nested.zip", [
        ("outer.json", '"one"'), ("child.zip", nested)])
    return path, len(nested) + 10


@pytest.mark.parametrize("budget", ["max_files", "max_total_size"])
def test_nested_archives_still_share_the_root_budget(tmp_path, budget):
    """Call isolation must not reset the limits at a nested archive boundary."""
    path, full_size = _nested_archive(tmp_path)
    limit = 2 if budget == "max_files" else full_size - 5
    with pytest.raises(ValueError, match="maximum"):
        ZipReader(**{budget: limit}).load_data(path)


def test_nested_archive_at_exact_limits_and_sequential_reuse(tmp_path):
    """Inclusive configured limits and subsequent calls retain their behavior."""
    path, full_size = _nested_archive(tmp_path)
    reader = ZipReader(max_files=3, max_total_size=full_size)
    for _ in range(2):
        docs = reader.load_data(path)
        assert [doc.text for doc in docs] == ['"one"', '"two"']
        assert [doc.metadata["archive_depth"] for doc in docs] == [0, 1]
        assert [doc.metadata["archive_path"] for doc in docs] == [
            "outer.json", "child.zip/inner.json"]

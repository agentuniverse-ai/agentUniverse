"""Verify bounded writes and resource cleanup on failed 7Z extraction."""

import io

import pytest

from agentuniverse.agent.action.knowledge.reader.file import sevenzip_reader as module


def test_buffered_flush_failure_still_releases_handle(tmp_path):
    """A pending write error during close must not leave the raw file open."""

    class FailingRawFile(io.BytesIO):
        def write(self, data):
            raise OSError("disk full")

    writer = module._BoundedFileIO(tmp_path, ".txt", 10, module._ExtractionBudget(10, 10, 1))
    writer._file.close()
    raw = FailingRawFile()
    writer._file = io.BufferedWriter(raw)
    writer.write(b"pending")
    try:
        with pytest.raises(OSError, match="disk full"):
            writer.close()
        assert raw.closed
        assert writer._file.closed
        assert writer._closed
        writer.close()  # Cleanup remains idempotent after a failed flush.
    finally:
        raw.close()


@pytest.mark.parametrize("error_type", [OSError, ValueError])
@pytest.mark.parametrize("cleanup_error", [False, True])
def test_extraction_failure_closes_writers_and_removes_temp_directory(tmp_path, monkeypatch, error_type, cleanup_error):
    """Exercise the real py7zr exception path after a partial file write."""
    py7zr = pytest.importorskip("py7zr")
    archive_path = tmp_path / "input.7z"
    with py7zr.SevenZipFile(archive_path, "w") as archive:
        archive.writestr(b"partial output", "data.txt")

    extraction_root = tmp_path / "extract"
    extraction_root.mkdir()
    monkeypatch.setattr(module.tempfile, "mkdtemp", lambda **kwargs: str(extraction_root))
    writers = []
    original_create = module._BoundedWriterFactory.create
    original_write = module._BoundedFileIO.write
    original_close = module._BoundedFileIO.close
    failure = error_type("injected extraction failure")

    def capture_writer(factory, filename):
        writer = original_create(factory, filename)
        writers.append(writer)
        return writer

    def fail_after_write(writer, data):
        original_write(writer, data)
        raise failure

    def close_with_error(writer):
        original_close(writer)
        if cleanup_error:
            raise OSError("injected close failure")

    monkeypatch.setattr(module._BoundedWriterFactory, "create", capture_writer)
    monkeypatch.setattr(module._BoundedFileIO, "write", fail_after_write)
    monkeypatch.setattr(module._BoundedFileIO, "close", close_with_error)
    try:
        with pytest.raises(error_type) as caught:
            module.SevenZipReader()._load_data(archive_path)
        assert caught.value is failure
        assert writers, "The failure must occur after a real writer was opened"
        assert all(writer._file.closed for writer in writers)
        assert not extraction_root.exists()
    finally:
        # Also release handles when testing the unfixed implementation on Windows.
        for writer in writers:
            original_close(writer)


@pytest.mark.parametrize(
    ("expected_size", "file_limit", "total_limit", "message"),
    [
        (4, 10, 20, "more data than declared"),
        (10, 4, 20, "entry exceeds maximum size"),
        (10, 10, 4, "exceeds maximum total size"),
    ],
)
def test_rejected_chunk_is_not_written_or_charged(tmp_path, expected_size, file_limit, total_limit, message):
    """All three byte limits reject a chunk before it reaches the file."""
    budget = module._ExtractionBudget(file_limit, total_limit, 2)
    writer = module._BoundedFileIO(tmp_path, ".txt", expected_size, budget)
    try:
        assert writer.write(b"1234") == 4
        with pytest.raises(ValueError, match=message):
            writer.write(b"5")
        writer.flush()
        assert writer.path.read_bytes() == b"1234"
        assert writer.size() == budget.written_bytes == 4
    finally:
        writer.close()


def test_writers_share_actual_byte_budget(tmp_path):
    """Separate members cannot reset the cumulative actual-write budget."""
    budget = module._ExtractionBudget(10, 6, 2)
    writers = [module._BoundedFileIO(tmp_path, ".txt", 10, budget) for _ in range(2)]
    try:
        writers[0].write(b"1234")
        writers[1].write(b"56")
        with pytest.raises(ValueError, match="maximum total size"):
            writers[1].write(b"7")
        for writer in writers:
            writer.flush()
        assert sum(writer.path.stat().st_size for writer in writers) == 6
        assert budget.written_bytes == 6
    finally:
        for writer in writers:
            writer.close()


def test_factory_closes_remaining_members_after_one_close_error(tmp_path, monkeypatch):
    """A failed close must not leave later factory products open."""
    budget = module._ExtractionBudget(10, 20, 2)
    factory = module._BoundedWriterFactory(tmp_path, {"a.txt": 1, "b.txt": 1}, budget)
    writers = [factory.create(str(tmp_path / name)) for name in ("a.txt", "b.txt")]
    original_close = module._BoundedFileIO.close
    failure = OSError("first close failed")

    def close_with_error(writer):
        original_close(writer)
        if writer is writers[0]:
            raise failure

    monkeypatch.setattr(module._BoundedFileIO, "close", close_with_error)
    try:
        with pytest.raises(OSError) as caught:
            factory.close()
        assert caught.value is failure
        assert all(writer._file.closed for writer in writers)
    finally:
        for writer in writers:
            original_close(writer)

"""Real XLSX serialization must preserve existing files on failure or conflict."""

import asyncio
import gc
import json
import threading
from datetime import datetime, time, timezone

import pytest

openpyxl = pytest.importorskip("openpyxl")

from agentuniverse.agent.action.tool.common_tool.excel_tool import ExcelTool


def execute(tool, path, mode, asynchronous=False, **kwargs):
    if asynchronous:
        return json.loads(asyncio.run(tool.async_execute(str(path), mode, **kwargs)))
    return json.loads(tool.execute(str(path), mode, **kwargs))


def create_original(path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Records"
    sheet.append(["original", 42, "=B1*2"])
    sheet["A1"].font = openpyxl.styles.Font(bold=True)
    workbook.create_sheet("Other").append(["preserved"])
    workbook.save(path)
    workbook.close()


def read_values(path, sheet="Records"):
    workbook = openpyxl.load_workbook(path)
    try:
        return list(workbook[sheet].values)
    finally:
        workbook.close()


def assert_clean(path):
    assert not list(path.parent.glob(".excel-*"))


@pytest.mark.parametrize("overwrite", [False, True])
def test_create_race_preserves_winner_unless_overwrite_is_explicit(tmp_path, monkeypatch, overwrite):
    path = tmp_path / "result.xlsx"
    tool = ExcelTool()
    paused, release = threading.Event(), threading.Event()
    original_init = openpyxl.Workbook.__init__
    results = []

    def first_write():
        results.append(execute(tool, path, "write", data=[["first"]], overwrite=overwrite))

    first = threading.Thread(target=first_write)

    def pause_first(workbook, *args, **kwargs):
        if threading.current_thread() is first:
            paused.set()
            assert release.wait(15)
        return original_init(workbook, *args, **kwargs)

    # Pause after the public existence check, before workbook preparation.
    # Native workbook construction, serialization and filesystem writes run.
    monkeypatch.setattr(openpyxl.Workbook, "__init__", pause_first)
    first.start()
    try:
        assert paused.wait(15)
        winner = execute(tool, path, "write", data=[["winner"]])
        assert winner["status"] == "success", winner
        winning_bytes = path.read_bytes()
    finally:
        release.set()
        first.join(15)
    assert not first.is_alive()
    assert read_values(path, "Sheet1") == [("first" if overwrite else "winner",)]
    if not overwrite:
        assert path.read_bytes() == winning_bytes
    assert results[0]["status"] == ("success" if overwrite else "error"), results
    assert_clean(path)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("value", [
    datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc),
    time(3, 4, tzinfo=timezone.utc),
])
def test_append_serialization_failure_preserves_original_bytes(tmp_path, value, asynchronous):
    path = tmp_path / "original.xlsx"
    create_original(path)
    before = path.read_bytes()
    result = execute(ExcelTool(), path, "append", asynchronous,
                     sheet_name="Records", data=[["new", value]])
    assert_clean(path)
    # Release cycles created inside openpyxl's failed XML writer. This does not
    # change the tool's result, the workbook bytes, or publication behavior.
    gc.collect()
    assert result["status"] == "error", result
    assert "timezone" in result["error"].lower(), result
    assert path.read_bytes() == before
    assert read_values(path) == [("original", 42, "=B1*2")]
    assert read_values(path, "Other") == [("preserved",)]


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("value", ["\ud800", "\udfff"])
@pytest.mark.skipif(not openpyxl.LXML, reason="lxml rejects unpaired XML surrogates during serialization")
def test_write_serialization_failure_never_publishes_partial_xlsx(tmp_path, existing, value):
    path = tmp_path / "result.xlsx"
    if existing:
        create_original(path)
    before = path.read_bytes() if existing else None
    result = execute(ExcelTool(), path, "write", overwrite=True, data=[[value]])
    assert_clean(path)
    gc.collect()
    assert result["status"] == "error", result
    if existing:
        assert path.read_bytes() == before
        assert read_values(path) == [("original", 42, "=B1*2")]
    else:
        assert not path.exists()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_existing_create_only_destination_is_unchanged(tmp_path, asynchronous):
    path = tmp_path / "original.xlsx"
    create_original(path)
    before = path.read_bytes()
    result = execute(ExcelTool(), path, "write", asynchronous, data=[["replacement"]])
    assert result["status"] == "error", result
    assert path.read_bytes() == before
    assert_clean(path)


@pytest.mark.parametrize("sheet_name", [None, "Records"])
def test_append_preserves_other_sheets_formulas_and_styles(tmp_path, sheet_name):
    path = tmp_path / "original.xlsx"
    create_original(path)
    result = execute(ExcelTool(), path, "append", sheet_name=sheet_name, data=[["new", 5]])
    assert result["status"] == "success", result
    assert result["start_row"] == 2
    assert result["end_row"] == 2
    assert read_values(path) == [("original", 42, "=B1*2"), ("new", 5, None)]
    assert read_values(path, "Other") == [("preserved",)]
    workbook = openpyxl.load_workbook(path)
    try:
        assert workbook["Records"]["A1"].font.bold
    finally:
        workbook.close()
    assert_clean(path)


@pytest.mark.parametrize("asynchronous", [False, True])
def test_explicit_overwrite_publishes_valid_formatted_workbook(tmp_path, asynchronous):
    path = tmp_path / "original.xlsx"
    create_original(path)
    result = execute(ExcelTool(), path, "write", asynchronous, overwrite=True,
                     sheet_name="Replaced", data=[["header", "value"], ["row", 7]])
    assert result["status"] == "success", result
    assert result["rows_written"] == 2
    assert result["file_size"] == path.stat().st_size
    assert read_values(path, "Replaced") == [("header", "value"), ("row", 7)]
    workbook = openpyxl.load_workbook(path)
    try:
        assert workbook.sheetnames == ["Replaced"]
        assert workbook.active["A1"].font.bold
    finally:
        workbook.close()
    assert_clean(path)


def test_write_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "more" / "new.xlsx"
    result = execute(ExcelTool(), path, "write", data=[["saved"]])
    assert result["status"] == "success", result
    assert read_values(path, "Sheet1") == [("saved",)]
    assert_clean(path)


def test_append_validation_error_preserves_original(tmp_path):
    path = tmp_path / "original.xlsx"
    create_original(path)
    before = path.read_bytes()
    result = execute(ExcelTool(), path, "append", data=[["illegal\x01character"]])
    assert result["status"] == "error", result
    assert path.read_bytes() == before
    assert read_values(path) == [("original", 42, "=B1*2")]
    assert_clean(path)


def test_publication_error_leaves_directory_and_cleans_temporary(tmp_path):
    path = tmp_path / "directory.xlsx"
    path.mkdir()
    marker = path / "keep.txt"
    marker.write_text("preserved", encoding="utf-8")
    result = execute(ExcelTool(), path, "write", data=[["data"]], overwrite=True)
    assert result["status"] == "error", result
    assert marker.read_text(encoding="utf-8") == "preserved"
    assert_clean(path)

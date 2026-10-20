# -*- coding:utf-8 -*-

import io

import pytest

from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader


def test_csv_reader_preserves_missing_file_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        CSVReader().load_data(tmp_path / "missing.csv")


def test_csv_reader_reports_invalid_file_input_type():
    with pytest.raises(TypeError, match="file must be a path"):
        CSVReader().load_data(42)


def test_csv_reader_chains_malformed_csv_error():
    malformed = io.StringIO('"unclosed,field\nnext line\n')

    with pytest.raises(ValueError, match="Failed to parse CSV file") as error:
        CSVReader().load_data(malformed)

    assert error.value.__cause__ is not None

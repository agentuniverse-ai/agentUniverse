from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager


def test_default_reader_registry_covers_file_reader_formats():
    expected = {
        "epub": "default_epub_reader",
        "xlsx": "xlsx_reader",
        "7z": "default_sevenzip_reader",
    }

    for file_type, reader_name in expected.items():
        assert ReaderManager.DEFAULT_READER[file_type] == reader_name


def test_sevenzip_legacy_alias_remains_available():
    assert ReaderManager.DEFAULT_READER["sevenzip"] == "default_sevenzip_reader"

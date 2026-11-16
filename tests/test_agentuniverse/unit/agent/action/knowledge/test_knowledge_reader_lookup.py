from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.knowledge import Knowledge


def test_load_data_normalizes_local_file_extension(tmp_path):
    source_path = tmp_path / "NOTES.TxT"
    source_path.write_text("hello", encoding="utf-8")
    reader = MagicMock()
    reader.load_data.return_value = []
    reader_manager = MagicMock()
    reader_manager.get_file_default_reader.return_value = reader

    with patch(
        "agentuniverse.agent.action.knowledge.knowledge.ReaderManager",
        return_value=reader_manager,
    ):
        result = Knowledge()._load_data(source_path=str(source_path))

    reader_manager.get_file_default_reader.assert_called_once_with("txt")
    reader.load_data.assert_called_once_with(str(source_path))
    assert result == []

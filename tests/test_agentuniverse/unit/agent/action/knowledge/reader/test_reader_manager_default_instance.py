from unittest.mock import Mock

from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager


def test_get_file_default_reader_forwards_new_instance_flag():
    manager = ReaderManager()
    manager.get_instance_obj = Mock(return_value=object())

    manager.get_file_default_reader("txt", new_instance=False)
    manager.get_instance_obj.assert_called_once_with(
        "default_txt_reader",
        new_instance=False,
    )

    manager.get_instance_obj.reset_mock()
    manager.get_file_default_reader("txt", new_instance=True)
    manager.get_instance_obj.assert_called_once_with(
        "default_txt_reader",
        new_instance=True,
    )

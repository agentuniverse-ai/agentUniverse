from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock
import zipfile

from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.action.knowledge.reader.file.zip_reader import ZipReader


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


def test_get_file_default_reader_keeps_historical_isolated_default():
    manager = ReaderManager()
    manager.get_instance_obj = Mock(return_value=object())

    manager.get_file_default_reader("txt")

    manager.get_instance_obj.assert_called_once_with(
        "default_txt_reader",
        new_instance=True,
    )


def test_zip_reader_instances_are_safe_for_concurrent_loads(tmp_path: Path):
    archives = []
    for name in ("first.zip", "second.zip"):
        archive_path = tmp_path / name
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("payload.txt", name)
        archives.append(archive_path)

    registered_reader = ZipReader()

    def resolve(_name, new_instance=True):
        return deepcopy(registered_reader) if new_instance else registered_reader

    manager = ReaderManager()
    manager.get_instance_obj = Mock(side_effect=resolve)
    readers = (
        manager.get_file_default_reader("zip"),
        manager.get_file_default_reader("zip"),
    )

    assert readers[0] is not readers[1]

    def load(reader_and_archive):
        reader, archive_path = reader_and_archive
        documents = reader.load_data(archive_path)
        return documents[0].text

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(load, zip(readers, archives)))

    assert results == ["first.zip", "second.zip"]

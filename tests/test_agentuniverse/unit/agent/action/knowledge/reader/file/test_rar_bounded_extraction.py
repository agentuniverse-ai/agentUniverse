import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.file.rar_reader import RarReader


class FakeRar:
    def __init__(self, entries):
        self.entries = entries
        self.extract_called = False
    def __enter__(self):
        return self
    def __exit__(self, *_):
        pass
    def infolist(self):
        return [SimpleNamespace(filename=name, file_size=len(data), compress_size=len(data), is_dir=lambda: False) for name, data in self.entries.items()]
    def open(self, entry):
        from io import BytesIO
        return BytesIO(self.entries[entry.filename])
    def extract(self, *args):
        self.extract_called = True
        raise AssertionError('unsafe extract must not be used')


class TestRarBoundedExtraction(unittest.TestCase):
    def test_extracts_through_bounded_stream_not_rar_extract(self):
        fake = FakeRar({'nested/ok.txt': b'hello'})
        reader = RarReader()
        seen = []
        reader._process_file = lambda **kwargs: seen.append(Path(kwargs['file_path']).read_bytes()) or []
        with tempfile.TemporaryDirectory() as directory, patch('rarfile.RarFile', return_value=fake):
            reader._process_rar(Path('unused.rar'), directory, 0, 5, 100, 100, 2, 1000, {}, 'unused.rar')
        self.assertEqual(seen, [b'hello'])
        self.assertFalse(fake.extract_called)

    def test_rejects_actual_size_exceeding_archive_metadata(self):
        fake = FakeRar({'bomb.txt': b'a' * 20})
        fake.infolist = lambda: [SimpleNamespace(filename='bomb.txt', file_size=1, compress_size=1, is_dir=lambda: False)]
        reader = RarReader()
        with tempfile.TemporaryDirectory() as directory, patch('rarfile.RarFile', return_value=fake):
            with self.assertRaises(ValueError):
                reader._process_rar(Path('unused.rar'), directory, 0, 5, 10, 100, 2, 1000, {}, 'unused.rar')
        self.assertFalse(fake.extract_called)

    def test_nested_entries_share_file_budget_with_siblings(self):
        root = FakeRar({'child.rar': b'archive', 'sibling.txt': b'sibling'})
        child = FakeRar({'inside.txt': b'inside'})
        reader = RarReader()
        seen = []
        reader._process_file = lambda **kwargs: seen.append(Path(kwargs['file_path']).read_bytes()) or []
        def open_rar(path, mode):
            return child if Path(path).name == 'child.rar' else root
        with tempfile.TemporaryDirectory() as directory, patch('rarfile.RarFile', side_effect=open_rar):
            reader._process_rar(Path('root.rar'), directory, 0, 5, 100, 100, 2, 1000, {}, 'root.rar')
        self.assertEqual(seen, [b'inside'])

    def test_reader_value_error_skips_only_its_entry(self):
        fake = FakeRar({'bad.txt': b'bad', 'good.txt': b'good'})
        reader = RarReader()
        seen = []
        def process_file(**kwargs):
            if kwargs['file_path'].name == 'bad.txt':
                raise ValueError('unsupported content')
            seen.append(kwargs['file_path'].read_bytes())
            return []
        reader._process_file = process_file
        with tempfile.TemporaryDirectory() as directory, patch('rarfile.RarFile', return_value=fake):
            reader._process_rar(Path('unused.rar'), directory, 0, 5, 100, 100, 2, 1000, {}, 'unused.rar')
        self.assertEqual(seen, [b'good'])

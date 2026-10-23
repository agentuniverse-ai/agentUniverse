"""Filesystem publication contracts; runs with only the Python standard library."""
from pathlib import Path
import tempfile
import threading
import unittest

from agentuniverse.agent.action.tool.common_tool.file_path_utils import atomic_publish_file


class AtomicFilePublishTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def test_create_publishes_complete_file_and_removes_temporary(self):
        for index, content in enumerate([b"", b"complete archive bytes"]):
            with self.subTest(content=content):
                source, target = self.root / f"source-{index}", self.root / f"target-{index}"
                source.write_bytes(content)
                atomic_publish_file(str(source), str(target))
                self.assertEqual(target.read_bytes(), content)
                self.assertFalse(source.exists())

    def test_create_refuses_existing_destination_without_changing_either_file(self):
        source, target = self.root / "source", self.root / "target"
        source.write_bytes(b"new document")
        target.write_bytes(b"existing document")
        with self.assertRaises(FileExistsError):
            atomic_publish_file(str(source), str(target))
        self.assertEqual(target.read_bytes(), b"existing document")
        self.assertEqual(source.read_bytes(), b"new document")

    def test_explicit_overwrite_replaces_existing_destination(self):
        source, target = self.root / "source", self.root / "target"
        source.write_bytes(b"new document")
        target.write_bytes(b"existing document")
        atomic_publish_file(str(source), str(target), overwrite=True)
        self.assertEqual(target.read_bytes(), b"new document")
        self.assertFalse(source.exists())

    def test_missing_source_does_not_damage_destination(self):
        target = self.root / "target"
        target.write_bytes(b"existing document")
        with self.assertRaises(FileNotFoundError):
            atomic_publish_file(str(self.root / "missing"), str(target), overwrite=True)
        self.assertEqual(target.read_bytes(), b"existing document")

    def test_concurrent_publishers_have_exactly_one_winner(self):
        target = self.root / "target"
        sources = [self.root / "first", self.root / "second"]
        contents = [b"first complete document", b"second complete document"]
        for source, content in zip(sources, contents):
            source.write_bytes(content)
        ready = threading.Barrier(2)
        completed, rejected = [], []

        def publish(index):
            ready.wait(timeout=5)
            try:
                atomic_publish_file(str(sources[index]), str(target))
                completed.append(index)
            except FileExistsError:
                rejected.append(index)

        threads = [threading.Thread(target=publish, args=(index,)) for index in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(5)
            self.assertFalse(thread.is_alive())
        self.assertEqual(len(completed), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(target.read_bytes(), contents[completed[0]])
        self.assertFalse(sources[completed[0]].exists())
        self.assertTrue(sources[rejected[0]].exists())


if __name__ == "__main__":
    unittest.main()

import sys
import types
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.file.markdown_reader import MarkdownReader


class TestMarkdownReader(unittest.TestCase):

    def test_load_data_returns_empty_list_for_empty_loader_result(self):
        class EmptyMarkdownLoader:
            def __init__(self, file):
                self.file = file

            def load(self):
                return []

        community_module = types.ModuleType("langchain_community")
        loaders_module = types.ModuleType("langchain_community.document_loaders")
        loaders_module.UnstructuredMarkdownLoader = EmptyMarkdownLoader

        with patch.dict(sys.modules, {
            "langchain_community": community_module,
            "langchain_community.document_loaders": loaders_module,
        }):
            documents = MarkdownReader()._load_data("empty.md")

        self.assertEqual(documents, [])


if __name__ == "__main__":
    unittest.main()

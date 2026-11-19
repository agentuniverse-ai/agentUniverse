import sys
import types
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.reader.file.pptx_reader import PptxReader


class TestPptxReader(unittest.TestCase):

    def test_load_data_skips_empty_shapes(self):
        slide = MagicMock()
        slide.shapes = [
            MagicMock(text="Title"),
            MagicMock(text="   "),
            MagicMock(text=""),
        ]
        presentation = MagicMock()
        presentation.slides = [slide]

        pptx_module = types.ModuleType("pptx")
        pptx_module.Presentation = MagicMock(return_value=presentation)

        with patch.dict(sys.modules, {"pptx": pptx_module}):
            documents = PptxReader()._load_data("deck.pptx")

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].text, "Title")
        self.assertEqual(documents[0].metadata["slide_number"], 1)


if __name__ == "__main__":
    unittest.main()

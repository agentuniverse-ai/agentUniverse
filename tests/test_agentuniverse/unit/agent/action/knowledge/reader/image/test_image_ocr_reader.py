import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.image.image_ocr_reader import ImageOCRReader


class ImageOCRReaderTest(unittest.TestCase):

    def test_load_data_does_not_print_file_path(self):
        reader = ImageOCRReader()
        stdout = io.StringIO()

        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file, \
                patch.object(reader, "_ocr", return_value=("text", "mock")), \
                redirect_stdout(stdout):
            documents = reader._load_data(Path(temp_file.name))

        self.assertEqual("text", documents[0].text)
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()

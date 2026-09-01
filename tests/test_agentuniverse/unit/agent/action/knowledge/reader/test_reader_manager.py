import unittest
from pathlib import Path
from unittest.mock import patch, sentinel

from agentuniverse.agent.action.knowledge.reader.file.code_reader import \
    CODE_FILE_EXTENSIONS
from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import \
    XlsxReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import \
    ReaderManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestReaderManager(unittest.TestCase):
    """Tests for built-in file reader routing."""

    def setUp(self):
        self.manager = ReaderManager()

    def test_xlsx_config_uses_component_metadata_schema(self):
        """The XLSX config should be discoverable as a Reader component."""
        config_path = Path(__file__).resolve().parents[7] / (
            'agentuniverse/agent/action/knowledge/reader/file/xlsx_reader.yaml'
        )

        configer = ComponentConfiger().load_by_configer(
            Configer(path=str(config_path)).load()
        )

        self.assertEqual(configer.name, 'xlsx_reader')
        self.assertEqual(
            configer.get_component_config_type(),
            ComponentEnum.READER.value,
        )
        self.assertEqual(
            configer.metadata_module,
            XlsxReader.__module__,
        )
        self.assertEqual(configer.metadata_class, XlsxReader.__name__)

    def test_default_reader_map_covers_available_file_readers(self):
        """Every available file reader should have a reachable extension."""
        expected_routes = {
            'xlsx': 'xlsx_reader',
            'epub': 'default_epub_reader',
            '7z': 'default_sevenzip_reader',
        }
        expected_routes.update({
            extension.lstrip('.'): 'default_code_reader'
            for extension in CODE_FILE_EXTENSIONS
            if extension not in {'.json', '.md'}
        })

        for extension, reader_name in expected_routes.items():
            with self.subTest(extension=extension):
                self.assertEqual(
                    self.manager.DEFAULT_READER[extension],
                    reader_name,
                )

        self.assertEqual(
            self.manager.DEFAULT_READER['json'],
            'default_json_reader',
        )
        self.assertEqual(
            self.manager.DEFAULT_READER['md'],
            'default_markdown_reader',
        )

    def test_lookup_strips_leading_dot_and_forwards_new_instance(self):
        """Lookup options should be passed through to the component manager."""
        for new_instance in (False, True):
            with self.subTest(new_instance=new_instance):
                with patch.object(
                    self.manager,
                    'get_instance_obj',
                    return_value=sentinel.reader,
                ) as get_instance_obj:
                    result = self.manager.get_file_default_reader(
                        '.xlsx',
                        new_instance=new_instance,
                    )

                self.assertIs(result, sentinel.reader)
                get_instance_obj.assert_called_once_with(
                    'xlsx_reader',
                    new_instance=new_instance,
                )

    def test_lookup_preserves_copy_by_default_behavior(self):
        """Omitting new_instance should keep returning an independent copy."""
        with patch.object(
            self.manager,
            'get_instance_obj',
            return_value=sentinel.reader,
        ) as get_instance_obj:
            result = self.manager.get_file_default_reader('txt')

        self.assertIs(result, sentinel.reader)
        get_instance_obj.assert_called_once_with(
            'default_txt_reader',
            new_instance=True,
        )

    def test_unknown_file_type_does_not_query_component_manager(self):
        """Unknown extensions should preserve the existing None behavior."""
        with patch.object(self.manager, 'get_instance_obj') as get_instance_obj:
            result = self.manager.get_file_default_reader('unknown')

        self.assertIsNone(result)
        get_instance_obj.assert_not_called()


if __name__ == '__main__':
    unittest.main()

import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from agentuniverse.agent.action.knowledge.doc_processor.code_ast_processor import CodeAstProcessor


class TestCodeAstUnicodeOffsets(unittest.TestCase):
    def test_ast_text_uses_utf8_byte_offsets(self):
        processor = CodeAstProcessor()
        code = '中foo'
        node = SimpleNamespace(start_byte=3, end_byte=6, start_point=(0, 3),
                               end_point=(0, 6), type='identifier', child_count=0,
                               children=[])
        ast = processor._convert_tree_to_json(node, code)
        self.assertEqual(ast['text'], 'foo')

    def test_chunk_identifier_after_unicode_prefix(self):
        processor = CodeAstProcessor()
        code = '中\nfunction foo() {\n return 1;\n}'
        start = code.encode('utf8').find(b'foo')
        child = SimpleNamespace(type='identifier', start_byte=start, end_byte=start + 3)
        root = Mock(type='function_definition', start_point=(0, 0), end_point=(3, 1),
                    children=[child])
        cursor = Mock(node=root)
        cursor.goto_first_child.return_value = False
        cursor.goto_next_sibling.return_value = False
        root.walk.return_value = cursor
        processor._parser = Mock()
        processor._parser.parse.return_value.root_node = root
        processor._convert_tree_to_json = lambda *_, **__: {}
        chunks = processor._generate_code_chunks(code, root, 'javascript', {})
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].metadata['chunk_name'], 'foo')
        self.assertEqual(json.loads(chunks[0].text)['name'], 'foo')

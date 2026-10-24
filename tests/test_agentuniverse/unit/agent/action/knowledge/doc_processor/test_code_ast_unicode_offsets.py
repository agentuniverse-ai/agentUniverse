import json
import unittest
from types import SimpleNamespace

import pytest

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
        tree_sitter = pytest.importorskip('tree_sitter')
        javascript = pytest.importorskip('tree_sitter_javascript')
        processor = CodeAstProcessor()
        code = '// 中文前缀\nfunction foo() {\n const value = 1;\n return value;\n}'
        processor._parser = tree_sitter.Parser(tree_sitter.Language(javascript.language()))
        root = processor._parser.parse(code.encode('utf8')).root_node
        self.assertFalse(root.has_error)
        chunks = processor._generate_code_chunks(code, root, 'javascript', {})
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].metadata['chunk_name'], 'foo')
        self.assertEqual(json.loads(chunks[0].text)['name'], 'foo')

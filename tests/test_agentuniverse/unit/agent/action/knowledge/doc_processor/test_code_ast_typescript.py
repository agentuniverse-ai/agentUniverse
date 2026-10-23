"""Exercise the installed TypeScript grammar through native code ingestion."""
import json

import pytest

pytest.importorskip('tree_sitter')
pytest.importorskip('tree_sitter_typescript')
pytest.importorskip('tree_sitter_python')

from agentuniverse.agent.action.knowledge.doc_processor.code_ast_processor import CodeAstProcessor
from agentuniverse.agent.action.knowledge.reader.file.code_reader import CodeReader
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


@pytest.fixture
def processor(tmp_path):
    config = ComponentConfiger()
    config.name = 'test_ast'
    config.description = 'AST test'
    config.language_dir = str(tmp_path)
    return CodeAstProcessor().initialize_by_component_configer(config)


def read_code(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding='utf-8')
    return CodeReader().load_data(path)[0]


def node_types(ast):
    yield ast['type']
    for child in ast.get('children', []):
        yield from node_types(child)


@pytest.mark.parametrize('code,expected_node', [
    ('const answer: number = 42;', 'lexical_declaration'),
    ('function identity<T>(value: T): T { return value; }', 'function_declaration'),
    ('class Report { title: string = "报告"; }', 'class_declaration'),
])
def test_typescript_file_parses_with_native_grammar(processor, tmp_path, code, expected_node):
    source = read_code(tmp_path, 'example.ts', code)
    result = processor.process_docs([source])[0]
    parsed = json.loads(result.text)
    assert parsed['language'] == 'typescript'
    assert parsed['ast']['type'] == 'program'
    assert parsed['ast']['text'] == code
    types = set(node_types(parsed['ast']))
    assert expected_node in types
    assert 'ERROR' not in types
    assert result.metadata['file_name'] == 'example.ts'
    assert result.metadata['processing_method'] == 'tree_sitter'


def test_standard_python_language_entrypoint_still_works(processor, tmp_path):
    source = read_code(tmp_path, 'example.py', 'def identity(value):\n    return value\n')
    result = json.loads(processor.process_docs([source])[0].text)
    assert result['language'] == 'python'
    assert result['ast']['type'] == 'module'
    assert result['features']['function_count'] == 1


def test_cached_typescript_grammar_survives_language_switch(processor, tmp_path):
    ts = read_code(tmp_path, 'example.ts', 'const answer: number = 42;')
    py = read_code(tmp_path, 'example.py', 'answer = 42\n')
    first = processor.process_docs([ts])[0]
    results = processor.process_docs([py, ts])
    assert json.loads(results[0].text)['ast']['type'] == 'module'
    assert json.loads(results[1].text) == json.loads(first.text)
    assert set(processor._languages) == {'typescript', 'python'}

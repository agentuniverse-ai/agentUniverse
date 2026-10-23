"""AST node text limits must load from real component YAML."""
import json

import pytest
import yaml

pytest.importorskip('tree_sitter')
pytest.importorskip('tree_sitter_python')

from agentuniverse.agent.action.knowledge.doc_processor.code_ast_processor import CodeAstProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


@pytest.mark.parametrize('settings,initial,expected', [
    ({'max_node_len': 5}, 100, 5),
    ({'max_node_len': 200}, 100, 200),
    ({'max_node_text_length': 5}, 100, 5),
    ({'max_node_text_length': 200}, 100, 200),
    ({'max_node_len': 5, 'max_node_text_length': 200}, 100, 5),
    ({'max_node_len': 200, 'max_node_text_length': 5}, 100, 200),
    ({}, 100, 100),
    ({}, 23, 23),
])
def test_yaml_node_length_controls_native_ast_text(tmp_path, settings, initial, expected):
    path = tmp_path / 'processor.yaml'
    path.write_text(yaml.safe_dump(dict(name='ast', description='test',
                                      language_dir=str(tmp_path), **settings)))
    config = ComponentConfiger().load_by_configer(Configer().load_by_path(str(path)))
    processor = CodeAstProcessor(max_node_len=initial).initialize_by_component_configer(config)
    assert processor.max_node_len == expected
    code = 'def example():\n    return "A moderately long return value"\n'
    output = processor.process_docs([Document(text=code, metadata={'language': 'python'})])[0]
    ast = json.loads(output.text)['ast']
    assert ('text' in ast) is (len(code) < expected)
    if 'text' in ast:
        assert ast['text'] == code
    assert ast['type'] == 'module'
    assert ast['children']

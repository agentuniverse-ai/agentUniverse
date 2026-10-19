"""Exercise wide/deep syntax trees with real optional Tree-sitter grammars."""

import json
import sys

import pytest

pytest.importorskip("tree_sitter")

from agentuniverse.agent.action.knowledge.doc_processor.code_ast_processor import CodeAstProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


WIDTH = 1400
DEPTH = 1800


def processor(tmp_path, language):
    pytest.importorskip("tree_sitter_" + language)
    config = ComponentConfiger()
    config.name = "native-ast-traversal"
    config.description = "native traversal regression"
    config.language_dir = str(tmp_path)
    result = CodeAstProcessor()
    result._initialize_by_component_configer(config)
    return result


def process(proc, code, language, metadata=None):
    info = {"language": language, "file_name": "fixture"}
    info.update(metadata or {})
    original = Document(text=code, metadata=info)
    before = original.metadata.copy()
    limit = sys.getrecursionlimit()
    docs = proc.process_docs([original])
    assert sys.getrecursionlimit() == limit
    assert original.metadata == before
    assert docs[0].metadata["document_type"] == "code_ast"
    assert docs[0].metadata["processing_method"] == "tree_sitter"
    result = json.loads(docs[0].text)
    assert result["language"] == language
    assert result["code_length"] == len(code)
    return result, docs


@pytest.mark.parametrize("language", ["python", "javascript"])
def test_public_processing_counts_all_wide_module_nodes(tmp_path, language):
    proc = processor(tmp_path, language)
    code = "".join(
        ("value_%d = %d\n" if language == "python" else "const value_%d = %d;\n") % (n, n)
        for n in range(WIDTH)
    )
    result, docs = process(proc, code, language)
    features = result["features"]
    declaration = "assignment" if language == "python" else "variable_declarator"
    literal = "integer" if language == "python" else "number"
    assert features["identifier_count"] == WIDTH
    assert features["node_counts"][declaration] == WIDTH
    assert features["node_counts"][literal] == WIDTH
    assert features["function_count"] == 0
    assert features["code_metrics"]["line_count"] == WIDTH
    assert len(docs) > 1  # Existing line-window chunks are still emitted.


@pytest.mark.parametrize("language", ["python", "javascript"])
def test_public_processing_counts_deep_binary_expression_beyond_json_depth(tmp_path, language):
    proc = processor(tmp_path, language)
    code = ("value = " if language == "python" else "const value = ") + " + ".join(["1"] * DEPTH) + "\n"
    result, _ = process(proc, code, language)
    features = result["features"]
    binary = "binary_operator" if language == "python" else "binary_expression"
    literal = "integer" if language == "python" else "number"
    assert features["node_counts"][binary] == DEPTH - 1
    assert features["node_counts"][literal] == DEPTH
    assert features["identifier_count"] == 1
    assert proc.max_depth == 8


@pytest.mark.parametrize("language", ["python", "javascript"])
def test_chunk_collection_visits_every_wide_declaration(tmp_path, language):
    proc = processor(tmp_path, language)
    template = (
        "def func_%d():\n    x = 1\n    y = 2\n    return x + y\n\n"
        if language == "python" else
        "function func_%d() {\n  const x = 1;\n  const y = 2;\n  return x + y;\n}\n\n"
    )
    code = "".join(template % n for n in range(WIDTH))
    # A short public call configures the native parser's selected language.
    process(proc, "x = 1" if language == "python" else "const x = 1;", language)
    tree = proc._parser.parse(code.encode("utf8"))
    limit = sys.getrecursionlimit()
    chunks = proc._generate_code_chunks(code, tree.root_node, language, {"source": "kept"})
    assert sys.getrecursionlimit() == limit
    assert len(chunks) == WIDTH
    assert [doc.metadata["chunk_name"] for doc in chunks] == ["func_%d" % n for n in range(WIDTH)]
    assert all(doc.metadata["chunk_type"] == "function" for doc in chunks)
    assert all(doc.metadata["source"] == "kept" for doc in chunks)
    assert json.loads(chunks[-1].text)["name"] == "func_1399"
    assert "return x + y" in json.loads(chunks[-1].text)["code"]


def test_small_python_feature_counts_remain_unchanged(tmp_path):
    proc = processor(tmp_path, "python")
    code = "class Greeter:\n    def speak(self, name):\n        print(name)\n        return name\n\ndef outside(x):\n    return x + 1\n"
    result, _ = process(proc, code, "python")
    features = result["features"]
    assert features["function_count"] == 2
    assert features["class_count"] == 1
    assert features["identifier_count"] == 10
    assert features["statement_count"] == 3


def test_small_javascript_features_and_declaration_order_remain_unchanged(tmp_path):
    proc = processor(tmp_path, "javascript")
    proc.chunk_size = 10
    proc.chunk_overlap = 2
    code = "// 中文\nfunction first() {\n  const x = 1;\n  const y = 2;\n  return x + y;\n}\nfunction second() {\n  const x = 3;\n  const y = 4;\n  return x + y;\n}\n"
    result, docs = process(proc, code, "javascript")
    assert result["features"]["function_count"] == 2
    assert [doc.metadata["chunk_name"] for doc in docs[1:]] == ["first", "second"]


def test_native_cursor_stays_within_requested_subtree(tmp_path):
    proc = processor(tmp_path, "python")
    code = "def first():\n    return 1\ndef second():\n    return 2\n"
    process(proc, code, "python")
    tree = proc._parser.parse(code.encode())
    subtree = tree.root_node.named_children[0]
    counts = proc._count_node_types(subtree)
    assert counts["function_definition"] == 1
    assert counts["identifier"] == 1
    assert counts["integer"] == 1
    assert proc._extract_features(subtree, code, "python")["function_count"] == 1


def test_unicode_metadata_and_json_depth_limit_remain_unchanged(tmp_path):
    proc = processor(tmp_path, "python")
    proc.max_depth = 2
    result, docs = process(proc, "# 中文\ndef 名字():\n    x = 1\n    y = 2\n    return x + y\n", "python", {"source": "原文"})
    pending = [result["ast"]]
    nodes = []
    while pending:
        node = pending.pop()
        nodes.append(node)
        pending.extend(node.get("children", []))
    assert any(node.get("text") == "名字" for node in nodes)
    assert any(node["type"] == "max_depth_reached" for node in nodes)
    assert all(doc.metadata["source"] == "原文" for doc in docs)
    assert result["features"]["function_count"] == 1


def test_nested_python_declaration_order_remains_unchanged(tmp_path):
    proc = processor(tmp_path, "python")
    proc.chunk_size = 10
    proc.chunk_overlap = 2
    code = "class Outer:\n    def method(self):\n        def nested():\n            x = 1\n            y = 2\n            return x + y\n        return nested()\n"
    result, docs = process(proc, code, "python")
    assert result["features"]["function_count"] == 2
    assert result["features"]["class_count"] == 1
    assert [doc.metadata["chunk_name"] for doc in docs[1:]] == ["Outer", "method", "nested"]


def test_backtracking_visits_the_next_parent_after_a_large_child_set(tmp_path):
    proc = processor(tmp_path, "python")
    code = "".join("def %s():\n" % name + "".join("    value_%d = %d\n" % (n, n) for n in range(300)) for name in ("first", "second"))
    result, _ = process(proc, code, "python")
    features = result["features"]
    assert features["function_count"] == 2
    assert features["identifier_count"] == 602
    assert features["node_counts"]["assignment"] == 600


def chunking_processor(tmp_path, language):
    proc = processor(tmp_path, language)
    proc.chunk_size = 10
    proc.chunk_overlap = 2
    return proc


def assert_named_chunks(docs, names, kinds):
    chunks = docs[1:]
    assert [doc.metadata["chunk_name"] for doc in chunks] == names
    assert [doc.metadata["chunk_type"] for doc in chunks] == kinds
    assert [json.loads(doc.text)["name"] for doc in chunks] == names
    assert [json.loads(doc.text)["type"] for doc in chunks] == kinds


def test_java_methods_are_functions_in_features_and_chunks(tmp_path):
    proc = chunking_processor(tmp_path, "java")
    code = "class Demo {\n int run() {\n  int x = 1;\n  int y = 2;\n  return x + y;\n }\n}\n"
    result, docs = process(proc, code, "java")
    assert result["features"]["function_count"] == 1
    assert result["features"]["class_count"] == 1
    assert_named_chunks(docs, ["Demo", "run"], ["class", "function"])


def test_java_multiline_interface_methods_are_counted_and_named(tmp_path):
    proc = chunking_processor(tmp_path, "java")
    code = "interface Service {\n String run(\n  String name,\n  int count\n );\n int count(\n  String name,\n  int limit\n );\n}\n"
    result, docs = process(proc, code, "java")
    assert result["features"]["function_count"] == 2
    assert_named_chunks(docs, ["run", "count"], ["function", "function"])


def test_javascript_class_method_variants_have_function_chunks(tmp_path):
    proc = chunking_processor(tmp_path, "javascript")
    code = """class Demo {
 constructor() {
  const x = 1;
  const y = 2;
  this.value = x + y;
 }
 run() {
  const x = 1;
  const y = 2;
  return x + y;
 }
 async runAsync() {
  const x = 1;
  const y = 2;
  return x + y;
 }
 *items() {
  const x = 1;
  const y = 2;
  yield x + y;
 }
 get value() {
  const x = 1;
  const y = 2;
  return x + y;
 }
 set value(next) {
  const x = next;
  const y = 2;
  this.saved = x + y;
 }
}
"""
    result, docs = process(proc, code, "javascript")
    assert result["features"]["function_count"] == 6
    assert result["features"]["class_count"] == 1
    assert_named_chunks(docs, ["Demo", "constructor", "run", "runAsync", "items", "value", "value"],
                        ["class"] + ["function"] * 6)


def test_javascript_object_methods_use_grammar_name_fields(tmp_path):
    proc = chunking_processor(tmp_path, "javascript")
    code = "const object = {\n run() {\n  const x = 1;\n  const y = 2;\n  return x + y;\n },\n [\"méthod\"]() {\n  const x = 3;\n  const y = 4;\n  return x + y;\n }\n};\n"
    result, docs = process(proc, code, "javascript")
    assert result["features"]["function_count"] == 2
    assert_named_chunks(docs, ["run", '["méthod"]'], ["function", "function"])


def test_javascript_private_and_unicode_method_names_preserve_byte_slices(tmp_path):
    proc = chunking_processor(tmp_path, "javascript")
    code = "// 中文\nclass Demo {\n #secret() {\n  const x = 1;\n  const y = 2;\n  return x + y;\n }\n 处理() {\n  const x = 3;\n  const y = 4;\n  return x + y;\n }\n}\n"
    result, docs = process(proc, code, "javascript")
    assert result["features"]["function_count"] == 2
    assert_named_chunks(docs, ["Demo", "#secret", "处理"], ["class", "function", "function"])


def test_public_processing_switches_languages_without_mixing_method_metadata(tmp_path):
    proc = chunking_processor(tmp_path, "python")
    samples = {
        "python": "class Demo:\n def run(self):\n  x = 1\n  y = 2\n  return x + y\n",
        "javascript": "class Demo {\n run() {\n  const x = 1;\n  const y = 2;\n  return x + y;\n }\n}\n",
        "java": "class Demo {\n int run() {\n  int x = 1;\n  int y = 2;\n  return x + y;\n }\n}\n",
    }
    for language, code in samples.items():
        pytest.importorskip("tree_sitter_" + language)
        result, docs = process(proc, code, language)
        assert result["features"]["function_count"] == 1
        assert_named_chunks(docs, ["Demo", "run"], ["class", "function"])
        assert all(doc.metadata["language"] == language for doc in docs)

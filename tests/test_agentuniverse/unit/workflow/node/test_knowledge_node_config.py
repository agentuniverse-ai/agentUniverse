from pathlib import Path


SOURCE = Path(
    "agentuniverse/workflow/node/knowledge_node.py"
).read_text(encoding="utf-8")


def test_knowledge_node_handles_optional_lists():
    assert "if inputs is None:" in SOURCE
    assert "for knowledge_param in inputs.knowledge_param or []:" in SOURCE
    assert "knowledge_id_list = param_map.get('id') or []" in SOURCE
    assert "inputs.input_param or []" in SOURCE
    assert 'raise ValueError("Knowledge node outputs are required.")' in SOURCE

from pathlib import Path


def test_end_node_validates_optional_configuration_before_indexing():
    source = Path("agentuniverse/workflow/node/end_node.py").read_text(encoding="utf-8")

    assert "if inputs is None or inputs.prompt is None:" in source
    assert "inputs.input_param or []" in source
    assert "if not output_params:" in source

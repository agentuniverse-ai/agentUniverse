from pathlib import Path


def test_start_node_validates_missing_outputs_before_indexing():
    source = Path("agentuniverse/workflow/node/start_node.py").read_text(encoding="utf-8")

    assert "if not output_params:" in source
    assert "Start node output configuration is required." in source

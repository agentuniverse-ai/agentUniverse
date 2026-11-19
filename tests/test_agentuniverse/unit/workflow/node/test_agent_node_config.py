from pathlib import Path


SOURCE = Path(
    "agentuniverse/workflow/node/agent_node.py"
).read_text(encoding="utf-8")


def test_agent_node_handles_missing_lists_and_outputs():
    assert "if inputs is None:" in SOURCE
    assert "for agent_param in inputs.agent_param or []:" in SOURCE
    assert "inputs.input_param or []" in SOURCE
    assert "self._data.outputs or []" in SOURCE
    assert 'raise ValueError("Agent node outputs are required.")' in SOURCE

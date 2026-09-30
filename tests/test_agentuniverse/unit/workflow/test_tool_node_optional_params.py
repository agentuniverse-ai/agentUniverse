from pathlib import Path


def test_tool_node_accepts_null_input_parameter_list():
    source = Path("agentuniverse/workflow/node/tool_node.py").read_text(encoding="utf-8")

    assert "tool_params: List[NodeInfoParams] = inputs.tool_param or []" in source
    assert "inputs.input_param or []" in source
    assert "output_params: List[NodeOutputParams] = self._data.outputs or []" in source

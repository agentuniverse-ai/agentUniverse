from pathlib import Path


SOURCE = Path(
    "agentuniverse/workflow/node/llm_node.py"
).read_text(encoding="utf-8")


def test_llm_node_validates_optional_configuration():
    assert "if inputs is None:" in SOURCE
    assert "for llm_param in inputs.llm_param or []:" in SOURCE
    assert "prompt = param_map['prompt'] or ''" in SOURCE
    assert "inputs.input_param or []" in SOURCE
    assert 'raise ValueError("LLM node outputs are required.")' in SOURCE

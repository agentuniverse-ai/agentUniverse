from pathlib import Path


SOURCE = Path(
    "agentuniverse/workflow/node/node.py"
).read_text(encoding="utf-8")


def test_resolver_tolerates_missing_and_malformed_values():
    assert "for input_param in input_params or []:" in SOURCE
    assert "if val is None:" in SOURCE
    assert "len(content) < 2" in SOURCE

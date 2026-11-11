from pathlib import Path


SOURCE = Path(
    "agentuniverse/prompt/prompt.py"
).read_text(encoding="utf-8")


def test_prompt_ignores_non_mapping_configuration_payloads():
    assert 'config_value = getattr(component_configer.configer, "value", {})' in SOURCE
    assert "if not isinstance(config_value, dict):" in SOURCE
    assert "for k, v in config_value.items():" in SOURCE

from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent/action/toolkit/toolkit.py"
).read_text(encoding="utf-8")


def test_toolkit_ignores_non_mapping_configuration_payloads():
    assert 'config_value = getattr(component_configer.configer, "value", {})' in SOURCE
    assert "if not isinstance(config_value, dict):" in SOURCE
    assert "for key, value in config_value.items():" in SOURCE

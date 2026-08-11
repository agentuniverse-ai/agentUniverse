from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent_serve/service_configer.py"
).read_text(encoding="utf-8")


def test_service_configer_normalizes_non_mapping_values():
    assert "if not isinstance(configer.value, dict):" in SOURCE
    assert "configer.value = {}" in SOURCE
    assert "config_value = configer.value" in SOURCE

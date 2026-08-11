from pathlib import Path


SOURCE = Path(
    "agentuniverse/base/config/custom_configer/default_llm_configer.py"
).read_text(encoding="utf-8")


def test_default_llm_configer_guards_nested_section_shape():
    assert "if isinstance(self.value, dict):" in SOURCE
    assert "default_config = self.value.get('DEFAULT')" in SOURCE
    assert "if isinstance(default_config, dict):" in SOURCE

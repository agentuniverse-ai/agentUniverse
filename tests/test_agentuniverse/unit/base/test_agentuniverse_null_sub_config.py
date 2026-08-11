from pathlib import Path


def test_startup_normalizes_nullable_sub_config_path_section():
    source = Path("agentuniverse/base/agentuniverse.py").read_text(encoding="utf-8")

    assert source.count("if not isinstance(sub_config_path, dict):") == 2
    assert "sub_config_path.get('custom_key_path')" in source
    assert "sub_config_path.get('log_config_path')" in source

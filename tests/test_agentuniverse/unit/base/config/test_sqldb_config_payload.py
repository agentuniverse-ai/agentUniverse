from pathlib import Path


SOURCE = Path(
    "agentuniverse/base/config/component_configer/configers/sqldb_wrapper_config.py"
).read_text(encoding="utf-8")


def test_sqldb_configer_normalizes_payload_and_nested_args():
    assert "if not isinstance(configer.value, dict):" in SOURCE
    assert "engine_args = config_value.get('engine_args')" in SOURCE
    assert "if isinstance(engine_args, dict) else {}" in SOURCE
    assert "if isinstance(sql_database_args, dict) else {}" in SOURCE

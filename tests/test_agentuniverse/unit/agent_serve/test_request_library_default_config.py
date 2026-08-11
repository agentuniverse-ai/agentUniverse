from pathlib import Path


def test_request_library_normalizes_missing_database_config():
    source = Path(
        "agentuniverse/agent_serve/web/dal/request_library.py"
    ).read_text(encoding="utf-8")

    assert "db_config = configer.get('DB', {}) if configer else {}" in source
    assert "if not isinstance(db_config, dict):" in source
    assert "db_config.get('update_interval', 5)" in source

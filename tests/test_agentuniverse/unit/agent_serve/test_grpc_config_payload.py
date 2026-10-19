from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent_serve/web/rpc/grpc/grpc_server_booster.py"
).read_text(encoding="utf-8")


def test_grpc_config_handles_missing_nested_section():
    assert 'config_value = getattr(configer, "value", {})' in SOURCE
    assert "if not isinstance(grpc_config, dict):" in SOURCE
    assert "grpc_config.get('server_port', 50051)" in SOURCE

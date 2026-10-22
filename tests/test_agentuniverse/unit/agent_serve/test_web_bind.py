import pytest

from agentuniverse.agent_serve.web import web_booster


@pytest.mark.parametrize(
    ("bind", "expected"),
    [
        ("127.0.0.1:8002", ("127.0.0.1", 8002)),
        ("localhost:8888", ("localhost", 8888)),
        ("[::1]:9000", ("::1", 9000)),
        ("::1:9000", ("::1", 9000)),
    ],
)
def test_parse_bind_supports_ipv4_hostnames_and_ipv6(bind, expected):
    assert web_booster._parse_bind(bind) == expected


@pytest.mark.parametrize(
    "bind",
    [
        None,
        "localhost",
        ":8888",
        "localhost:",
        "[::1:8888",
        "localhost:not-a-port",
        "localhost:65536",
    ],
)
def test_parse_bind_rejects_invalid_values(bind):
    with pytest.raises(ValueError, match="bind"):
        web_booster._parse_bind(bind)

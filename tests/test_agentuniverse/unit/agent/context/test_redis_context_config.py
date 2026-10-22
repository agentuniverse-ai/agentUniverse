"""Exercise the actual YAML configuration path without a Redis server."""

from unittest.mock import patch

import pytest
import yaml

from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

fakeredis = pytest.importorskip("fakeredis")


def load_config(tmp_path, **values):
    values["metadata"] = {
        "type": "CONTEXT_STORE",
        "module": "agentuniverse.agent.context.store.redis_context_store",
        "class": "RedisContextStore",
    }
    path = tmp_path / "store.yaml"
    path.write_text(yaml.safe_dump(values), encoding="utf-8")
    return ComponentConfiger().load_by_configer(Configer().load_by_path(str(path)))


@pytest.mark.parametrize("field,value", [
    ("redis_host", "redis.internal"),
    ("redis_port", 6381),
    ("redis_db", 7),
    ("redis_password", "example-test-password"),
])
def test_yaml_connection_settings_reach_client(tmp_path, field, value):
    config = load_config(tmp_path, **{field: value})
    with fakeredis.FakeRedis() as client:
        with patch("redis.Redis", return_value=client) as factory:
            store = RedisContextStore().initialize_by_component_configer(config)
        argument = {"redis_host": "host", "redis_port": "port",
                    "redis_db": "db", "redis_password": "password"}[field]
        assert factory.call_args.kwargs[argument] == value
        assert getattr(store, field) == value
        assert factory.call_args.kwargs["decode_responses"] is False


def test_yaml_prefix_and_ttl_control_persisted_keys(tmp_path):
    config = load_config(tmp_path, name="custom_context", key_prefix="custom:",
                         default_ttl_seconds=7200, ttl_hours=48,
                         storage_tier="warm-custom", max_segments=123)
    with fakeredis.FakeRedis() as client:
        with patch("redis.Redis", return_value=client):
            store = RedisContextStore().initialize_by_component_configer(config)
        segment = ContextSegment(type=ContextType.CONVERSATION, content="hello", tokens=1)
        store.add([segment], session_id="session")
        assert client.hget("custom:session:session", segment.id) is not None
        assert client.zscore("custom:index:session", segment.id) is not None
        assert 7190 <= client.ttl("custom:session:session") <= 7200
        assert 7190 <= client.ttl("custom:index:session") <= 7200
        assert store.name == "custom_context"
        assert store.ttl_hours == 48
        assert store.max_segments == 123
        assert store.storage_tier == "warm-custom"


def test_explicit_zero_db_and_null_password_override_constructor(tmp_path):
    config = load_config(tmp_path, redis_db=0, redis_password=None)
    with fakeredis.FakeRedis() as client:
        with patch("redis.Redis", return_value=client) as factory:
            RedisContextStore(redis_db=5, redis_password="old").initialize_by_component_configer(config)
        assert factory.call_args.kwargs["db"] == 0
        assert factory.call_args.kwargs["password"] is None


def test_omitted_options_preserve_constructor_values(tmp_path):
    config = load_config(tmp_path, name="named")
    with fakeredis.FakeRedis() as client:
        with patch("redis.Redis", return_value=client) as factory:
            store = RedisContextStore(redis_host="preconfigured", redis_db=3,
                                      key_prefix="existing:").initialize_by_component_configer(config)
        assert factory.call_args.kwargs["host"] == "preconfigured"
        assert factory.call_args.kwargs["db"] == 3
        assert store.key_prefix == "existing:"


def test_default_config_uses_default_connection(tmp_path):
    config = load_config(tmp_path)
    with fakeredis.FakeRedis() as client:
        with patch("redis.Redis", return_value=client) as factory:
            RedisContextStore().initialize_by_component_configer(config)
        factory.assert_called_once_with(host="localhost", port=6379, db=0,
                                        password=None, decode_responses=False)

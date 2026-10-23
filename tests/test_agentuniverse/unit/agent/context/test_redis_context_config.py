import sys
from types import SimpleNamespace
from unittest.mock import patch

from agentuniverse.agent.context.store.redis_context_store import RedisContextStore
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class FakeRedis:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.expirations = []
        self.__class__.instances.append(self)

    def ping(self):
        return True


def test_yaml_settings_are_applied_before_redis_connection(tmp_path):
    config_path = tmp_path / "redis_context_store.yaml"
    config_path.write_text(
        """name: custom_context
storage_tier: warm
max_segments: 321
ttl_hours: 12
redis_host: redis.internal
redis_port: 6381
redis_db: 7
redis_password: test-password
key_prefix: 'tenant:'
default_ttl_seconds: 7200
metadata:
  type: CONTEXT_STORE
  module: agentuniverse.agent.context.store.redis_context_store
  class: RedisContextStore
""",
        encoding="utf-8",
    )
    configer = Configer(path=str(config_path)).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    fake_module = SimpleNamespace(Redis=FakeRedis)
    FakeRedis.instances.clear()

    with patch.dict(sys.modules, {"redis": fake_module}):
        store = RedisContextStore().initialize_by_component_configer(component_configer)

    assert store.name == "custom_context"
    assert store.max_segments == 321
    assert store.ttl_hours == 12
    assert store.redis_host == "redis.internal"
    assert store.redis_port == 6381
    assert store.redis_db == 7
    assert store.redis_password == "test-password"
    assert store.key_prefix == "tenant:"
    assert store.default_ttl_seconds == 7200
    assert FakeRedis.instances[0].kwargs == {
        "host": "redis.internal",
        "port": 6381,
        "db": 7,
        "password": "test-password",
        "decode_responses": False,
    }

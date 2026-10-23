"""Exercise actual YAML loading before context backend initialization."""
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
import yaml

from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def configuration(tmp_path, values):
    path = tmp_path / "context.yaml"
    path.write_text(yaml.safe_dump(values), encoding="utf-8")
    return ComponentConfiger().load_by_configer(Configer().load_by_path(str(path)))


@pytest.mark.parametrize("store_class", [RamContextStore, RedisContextStore, ChromaContextStore])
def test_common_fields_and_false_values(tmp_path, store_class):
    store = store_class(name="old", enable_metrics=True, ttl_hours=24)
    # The shared hook is tested separately from optional network constructors.
    result = store._initialize_by_component_configer(configuration(tmp_path, {
        "name": "configured", "storage_tier": "custom", "max_segments": 2,
        "ttl_hours": 0, "enable_metrics": False,
    }))
    assert result is store
    assert (store.name, store.storage_tier, store.max_segments) == ("configured", "custom", 2)
    assert store.ttl_hours == 0
    assert store.enable_metrics is False


def test_yaml_metrics_are_initialized_and_ram_capacity_is_applied(tmp_path):
    store = RamContextStore().initialize_by_component_configer(configuration(tmp_path, {
        "name": "hot_reports", "max_segments": 2, "ttl_hours": 0,
        "enable_metrics": True, "default_symbol": True,
    }))
    for index in range(3):
        store.add([ContextSegment(id=str(index), type=ContextType.BACKGROUND,
                                  content="report", tokens=1)], session_id="session")
    assert {item.id for item in store.get("session")} == {"1", "2"}
    assert store.get_metrics()["add_count"] == 3
    assert store.default_symbol is True


@pytest.mark.parametrize("store_class", [RamContextStore, RedisContextStore, ChromaContextStore])
def test_omitted_fields_keep_constructor_values(tmp_path, store_class):
    store = store_class(name="custom", max_segments=17, ttl_hours=0)
    store._initialize_by_component_configer(configuration(tmp_path, {}))
    assert (store.name, store.max_segments, store.ttl_hours) == ("custom", 17, 0)


@pytest.mark.parametrize("password", [None, "test-password"])
def test_redis_configuration_reaches_client_before_ping(tmp_path, monkeypatch, password):
    module = ModuleType("redis")
    module.Redis = Mock()
    monkeypatch.setitem(sys.modules, "redis", module)
    store = RedisContextStore(redis_password="old").initialize_by_component_configer(
        configuration(tmp_path, {
            "name": "reports", "redis_host": "redis.example", "redis_port": 6380,
            "redis_db": 4, "redis_password": password, "key_prefix": "reports:",
            "default_ttl_seconds": 120,
        }))
    module.Redis.assert_called_once_with(host="redis.example", port=6380, db=4,
                                        password=password, decode_responses=False)
    module.Redis.return_value.ping.assert_called_once_with()
    assert store.key_prefix == "reports:"
    assert store.default_ttl_seconds == 120
    assert store.name == "reports"


def test_chroma_configuration_precedes_client_and_embedding_setup(tmp_path, monkeypatch):
    module, config_module = ModuleType("chromadb"), ModuleType("chromadb.config")
    module.Client = Mock()
    config_module.Settings = lambda **kwargs: SimpleNamespace(**kwargs)
    monkeypatch.setitem(sys.modules, "chromadb", module)
    monkeypatch.setitem(sys.modules, "chromadb.config", config_module)
    seen = []
    monkeypatch.setattr(ChromaContextStore, "_setup_embedding_function",
                        lambda self: seen.append(self.embedding_model_name))
    store = ChromaContextStore().initialize_by_component_configer(configuration(tmp_path, {
        "name": "archive", "collection_name": "reports_archive",
        "persist_directory": str(tmp_path / "archive"),
        "embedding_model_name": "configured_embedding", "similarity_threshold": 0.0,
    }))
    assert module.Client.call_args.args[0].persist_directory == str(tmp_path / "archive")
    assert seen == ["configured_embedding"]
    assert module.Client.return_value.get_or_create_collection.call_args.kwargs["name"] == "reports_archive"
    assert store.similarity_threshold == 0.0


def test_unknown_yaml_fields_cannot_replace_methods_or_state(tmp_path):
    store = RamContextStore()
    original_storage = store._storage
    store.initialize_by_component_configer(configuration(tmp_path, {
        "add": "not a method", "_storage": {}, "component_type": "LLM",
        "metadata": {"type": "CONTEXT_STORE"},
    }))
    assert callable(store.add)
    assert store._storage is original_storage
    assert store.component_type.value == "CONTEXT_STORE"

"""Real manager copies, YAML loading and local FAISS integration."""
from pathlib import Path

import pytest
from pydantic import PrivateAttr

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.embedding.cached_embedding import CachedEmbedding
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class CountingEmbedding(Embedding):
    embedding_model_name: str = "fixture"
    embedding_dims: int = 2
    _calls: list = PrivateAttr(default_factory=list)

    def get_embeddings(self, texts, **kwargs):
        self._calls.append((list(texts), dict(kwargs)))
        return [[float(len(text)), 1.0] for text in texts]

    async def async_get_embeddings(self, texts, **kwargs):
        return self.get_embeddings(texts, **kwargs)


@pytest.fixture
def registered():
    apps = ApplicationConfigManager()
    manager = EmbeddingManager()
    previous_pool = dict(manager._instance_obj_map)
    try:
        previous_app = apps.app_configer
    except ValueError:
        previous_app = None
    app = Configer()
    app.value = {"BASE_INFO": {"appname": "cache-integration"}}
    apps.app_configer = AppConfiger().load_by_configer(app)
    manager._instance_obj_map.clear()
    provider = CountingEmbedding(name="openai_embedding")
    yaml_path = Path(__file__).resolve().parents[6] / "agentuniverse/agent/action/knowledge/embedding/cached_embedding.yaml"
    config = ComponentConfiger().load_by_configer(Configer(str(yaml_path)).load())
    assert config.get_component_config_type() == "EMBEDDING"
    wrapper = CachedEmbedding().initialize_by_component_configer(config)
    manager.register(provider.get_instance_code(), provider)
    manager.register(wrapper.get_instance_code(), wrapper)
    try:
        yield manager, provider, wrapper
    finally:
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(previous_pool)
        apps.app_configer = previous_app


def test_repeated_real_manager_lookups_share_cache_but_not_configuration(registered):
    manager, provider, wrapper = registered
    first = manager.get_instance_obj("cached_embedding", strict=True)
    second = manager.get_instance_obj("cached_embedding", strict=True)
    assert first is not second and first is not wrapper
    assert first.get_embeddings(["alpha"]) == [[5.0, 1.0]]
    assert second.get_embeddings(["alpha"]) == [[5.0, 1.0]]
    assert len(provider._calls) == 1
    first.cache_version = "v2"
    assert second.cache_version == "example-v1"
    first.get_embeddings(["alpha"])
    assert len(provider._calls) == 2
    second.clear_cache()
    first.get_embeddings(["alpha"])
    assert len(provider._calls) == 3


def test_real_faiss_insert_query_reopen_with_cached_embedding(registered, tmp_path):
    from agentuniverse.agent.action.knowledge.store.faiss_store import FAISSStore
    from agentuniverse.agent.action.knowledge.store.document import Document
    from agentuniverse.agent.action.knowledge.store.query import Query
    manager, provider, wrapper = registered
    options = dict(index_path=str(tmp_path / "vectors.faiss"), metadata_path=str(tmp_path / "vectors.pkl"),
                   index_config={"index_type": "IndexFlatL2", "dimension": 2}, embedding_model="cached_embedding")
    store = FAISSStore(**options)
    store._new_client()
    store.insert_document([Document(id="a", text="alpha"), Document(id="b", text="alphabetical")])
    assert len(provider._calls) == 2
    for _ in range(2):
        result = store.query(Query(query_str="alpha", similarity_top_k=1))
        assert result[0].id == "a"
    assert len(provider._calls) == 3  # document and query roles are distinct
    reopened = FAISSStore(**options)
    reopened._new_client()
    assert reopened.query(Query(query_str="alpha", similarity_top_k=1))[0].text == "alpha"
    assert len(provider._calls) == 3

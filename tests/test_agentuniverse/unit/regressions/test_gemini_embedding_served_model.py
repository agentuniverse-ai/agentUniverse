import math
from pathlib import Path
from types import SimpleNamespace

import yaml

from agentuniverse.agent.action.knowledge.embedding import gemini_embedding
from agentuniverse.agent.action.knowledge.embedding.gemini_embedding import GeminiEmbedding

# Shut down on the Gemini API (https://ai.google.dev/gemini-api/docs/deprecations):
# embedding-001 on 2025-10-30, text-embedding-004 on 2026-01-14.
SHUT_DOWN = {"text-embedding-004", "embedding-001"}


class FakeModels:
    def __init__(self):
        self.calls = []

    def embed_content(self, model, contents, config=None):
        self.calls.append({"model": model, "contents": contents, "config": config})
        dims = getattr(config, "output_dimensionality", None) or 3072
        return SimpleNamespace(embeddings=[SimpleNamespace(values=[3.0] * dims) for _ in contents])


def _embedding(**kwargs):
    models = FakeModels()
    embedding = GeminiEmbedding(client=SimpleNamespace(models=models), **kwargs)
    return embedding, models


def test_component_yaml_names_a_served_model():
    path = Path(gemini_embedding.__file__).with_suffix(".yaml")
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert config["embedding_model_name"] not in SHUT_DOWN


def test_fallback_model_is_served():
    embedding, models = _embedding()
    embedding.get_embeddings(["text"])
    assert models.calls[0]["model"] not in SHUT_DOWN


def test_default_dims_are_requested_and_normalized():
    embedding, models = _embedding()
    result = embedding.get_embeddings(["hello world", "agentUniverse"])

    assert models.calls[0]["config"].output_dimensionality == 768
    assert len(result) == 2
    for values in result:
        assert len(values) == 768
        assert math.isclose(math.sqrt(sum(v * v for v in values)), 1.0, rel_tol=1e-9)


def test_native_dims_pass_through_unchanged():
    embedding, models = _embedding(embedding_dims=3072)
    result = embedding.get_embeddings(["text"])

    assert models.calls[0]["config"].output_dimensionality == 3072
    assert result == [[3.0] * 3072]

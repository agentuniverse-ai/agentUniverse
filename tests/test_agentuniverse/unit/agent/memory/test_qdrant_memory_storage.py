import sys
import types
import unittest
from unittest.mock import patch


class _Distance:
    COSINE = "COSINE"
    EUCLID = "EUCLID"
    DOT = "DOT"
    MANHATTAN = "MANHATTAN"


class _MatchAny:
    def __init__(self, any):
        self.any = any


class _MatchValue:
    def __init__(self, value):
        self.value = value


class _FieldCondition:
    def __init__(self, key, match):
        self.key = key
        self.match = match


class _Filter:
    def __init__(self, must):
        self.must = must


def _install_qdrant_stub():
    models_module = types.SimpleNamespace(
        Distance=_Distance,
        Filter=_Filter,
        FieldCondition=_FieldCondition,
        MatchAny=_MatchAny,
        MatchValue=_MatchValue,
        NamedVector=object,
        PointStruct=object,
        VectorParams=object,
    )
    qdrant_module = types.SimpleNamespace(QdrantClient=object)
    return patch.dict(
        sys.modules,
        {
            "qdrant_client": qdrant_module,
            "qdrant_client.models": models_module,
        },
    )


class QdrantMemoryStorageTest(unittest.TestCase):

    def test_build_filter_preserves_string_type_value(self):
        with _install_qdrant_stub():
            from agentuniverse.agent.memory.memory_storage.qdrant_memory_storage import QdrantMemoryStorage

        qdrant_filter = QdrantMemoryStorage._build_filter(None, None, None, "human")

        self.assertEqual("type", qdrant_filter.must[0].key)
        self.assertIsInstance(qdrant_filter.must[0].match, _MatchValue)
        self.assertEqual("human", qdrant_filter.must[0].match.value)

    def test_build_filter_uses_match_any_for_type_lists(self):
        with _install_qdrant_stub():
            from agentuniverse.agent.memory.memory_storage.qdrant_memory_storage import QdrantMemoryStorage

        qdrant_filter = QdrantMemoryStorage._build_filter(None, None, None, ["human", "ai"])

        self.assertIsInstance(qdrant_filter.must[0].match, _MatchAny)
        self.assertEqual(["human", "ai"], qdrant_filter.must[0].match.any)


if __name__ == "__main__":
    unittest.main()

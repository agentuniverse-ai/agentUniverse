import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch


class _Distance:
    COSINE = "COSINE"
    EUCLID = "EUCLID"
    DOT = "DOT"
    MANHATTAN = "MANHATTAN"


class _BadPoint:
    @property
    def payload(self):
        raise RuntimeError("bad payload")


def _install_qdrant_stub():
    models_module = types.SimpleNamespace(
        Distance=_Distance,
        Filter=object,
        FieldCondition=object,
        MatchValue=object,
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


class QdrantMemoryLoggingTest(unittest.TestCase):

    def test_to_messages_conversion_error_does_not_print(self):
        with _install_qdrant_stub():
            from agentuniverse.agent.memory.memory_storage.qdrant_memory_storage import QdrantMemoryStorage

        storage = QdrantMemoryStorage()
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            messages = storage.to_messages([_BadPoint()])

        self.assertEqual([], messages)
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()

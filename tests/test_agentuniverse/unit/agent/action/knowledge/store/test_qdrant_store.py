import unittest

from agentuniverse.agent.action.knowledge.store.qdrant_store import QdrantStore


class TestQdrantStore(unittest.TestCase):

    def test_coerce_bool_handles_boolean_strings(self):
        self.assertFalse(QdrantStore._coerce_bool("false"))
        self.assertFalse(QdrantStore._coerce_bool("0"))
        self.assertTrue(QdrantStore._coerce_bool("true"))
        self.assertTrue(QdrantStore._coerce_bool("1"))

    def test_coerce_bool_rejects_unknown_string(self):
        with self.assertRaisesRegex(ValueError, "Invalid boolean value"):
            QdrantStore._coerce_bool("enabled")


if __name__ == "__main__":
    unittest.main()

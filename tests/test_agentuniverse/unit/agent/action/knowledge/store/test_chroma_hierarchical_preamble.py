import unittest

from agentuniverse.agent.action.knowledge.store.chroma_hierarchical_store import (
    ChromaHierarchicalStore,
)
from agentuniverse.agent.action.knowledge.store.query import Query


class FakeCollection:
    def __init__(self):
        self.filters = []

    def query(self, **kwargs):
        where = kwargs["where"]
        self.filters.append(where)
        if where == {"hierarchical_level": -1}:
            return {
                "ids": [["preamble-id"]],
                "documents": [["Introduction text"]],
                "embeddings": None,
                "metadatas": [[{
                    "hierarchical_parent": "root",
                    "hierarchical_level": -1,
                }]],
                "distances": [[0.1]],
            }
        return {
            "ids": [["chapter-id"]],
            "documents": [["Chapter one text"]],
            "embeddings": None,
            "metadatas": [[{
                "hierarchical_parent": "root",
                "hierarchical_level": 0,
            }]],
            "distances": [[0.2]],
        }


class ChromaHierarchicalPreambleTest(unittest.TestCase):
    def test_query_includes_root_preamble_documents(self):
        store = ChromaHierarchicalStore(search_depth=1)
        collection = FakeCollection()
        store.collection = collection

        documents = store.query(Query(query_str="introduction"))

        self.assertEqual(
            [document.id for document in documents],
            ["preamble-id", "chapter-id"],
        )
        self.assertIn({"hierarchical_level": -1}, collection.filters)


if __name__ == "__main__":
    unittest.main()

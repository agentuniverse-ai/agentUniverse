import unittest

from agentuniverse.agent.action.knowledge.embedding.dashscope_embedding import (
    DashscopeEmbedding,
)


class TestDashscopeEmbedding(unittest.TestCase):

    def test_extract_batch_embeddings_rejects_missing_vectors(self):
        response = {
            "output": {
                "embeddings": [
                    {"embedding": [0.1, 0.2]},
                    {"text_index": 1},
                ]
            }
        }

        with self.assertRaisesRegex(Exception, "count mismatch"):
            DashscopeEmbedding._extract_batch_embeddings(response, 2)

    def test_extract_batch_embeddings_preserves_complete_vectors(self):
        response = {
            "output": {
                "embeddings": [
                    {"embedding": [0.1, 0.2]},
                    {"embedding": [0.3, 0.4]},
                ]
            }
        }

        self.assertEqual(
            DashscopeEmbedding._extract_batch_embeddings(response, 2),
            [[0.1, 0.2], [0.3, 0.4]],
        )


if __name__ == "__main__":
    unittest.main()

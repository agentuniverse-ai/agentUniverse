#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Test for gemini_embedding print removal + exception chain fix."""

import unittest


class TestGeminiEmbeddingFix(unittest.TestCase):

    def test_no_print_in_error_handler(self):
        import inspect
        from agentuniverse.agent.action.knowledge.embedding.\
            gemini_embedding import GeminiEmbedding
        src = inspect.getsource(GeminiEmbedding.get_embeddings)
        self.assertNotIn("print(", src,
                          "gemini_embedding must not print on error")

    def test_uses_from_e_for_chain(self):
        import inspect
        from agentuniverse.agent.action.knowledge.embedding.\
            gemini_embedding import GeminiEmbedding
        src = inspect.getsource(GeminiEmbedding.get_embeddings)
        self.assertIn("from e", src,
                      "gemini_embedding must chain the original exception")
        self.assertNotIn("raise ValueError(e)", src,
                         "must not use raise ValueError(e)")


if __name__ == "__main__":
    unittest.main(verbosity=2)

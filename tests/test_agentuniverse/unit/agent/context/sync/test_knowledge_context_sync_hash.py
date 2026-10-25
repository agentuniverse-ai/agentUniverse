# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Regression tests for the knowledge-sync change detection.

`KnowledgeContextSynchronizer.sync_knowledge_to_context()` compares a hash of
the documents against the stored version and returns early when it matches.
`_compute_hash()` used to build that hash from `"".join(documents)`, which is
the same input for different document sets:

    ["ab", "c"]  ->  "abc"
    ["a", "bc"]  ->  "abc"

so a knowledge update that only moved a boundary between documents was
reported as "No content changes detected" and the sync was dropped.
"""

import unittest
from unittest.mock import MagicMock

from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    KnowledgeContextSynchronizer,
)


class ComputeHashTest(unittest.TestCase):
    """The hash has to distinguish document sets, not just their concatenation."""

    def setUp(self):
        self.synchronizer = KnowledgeContextSynchronizer(context_manager=MagicMock())

    def test_different_boundaries_produce_different_hashes(self):
        """The regression: these two used to collide."""
        self.assertNotEqual(
            self.synchronizer._compute_hash(["ab", "c"]),
            self.synchronizer._compute_hash(["a", "bc"]),
        )

    def test_a_document_containing_the_separator_does_not_collide(self):
        """Length prefixing keeps `["a|b"]` distinct from `["a", "b"]`."""
        self.assertNotEqual(
            self.synchronizer._compute_hash(["a|b"]),
            self.synchronizer._compute_hash(["a", "b"]),
        )

    def test_an_empty_document_is_not_indistinguishable(self):
        self.assertNotEqual(
            self.synchronizer._compute_hash(["", "abc"]),
            self.synchronizer._compute_hash(["abc", ""]),
        )

    def test_identical_input_produces_identical_hashes(self):
        """Stability: the same documents must still match, or every sync runs."""
        first = self.synchronizer._compute_hash(["a", "b", "c"])
        second = self.synchronizer._compute_hash(["a", "b", "c"])

        self.assertEqual(first, second)

    def test_order_is_significant(self):
        self.assertNotEqual(
            self.synchronizer._compute_hash(["a", "b"]),
            self.synchronizer._compute_hash(["b", "a"]),
        )

    def test_every_split_of_one_word_hashes_differently(self):
        """Exhaustive: all 8 ways to split "abcd" must be distinguishable.

        With the previous `"".join(documents)` all 8 produced a single hash, so
        every boundary change on that text looked like "no change".
        """
        word = "abcd"
        hashes = {}
        for mask in range(1 << (len(word) - 1)):
            parts, prev = [], 0
            for i in range(len(word) - 1):
                if mask >> i & 1:
                    parts.append(word[prev:i + 1])
                    prev = i + 1
            parts.append(word[prev:])
            hashes.setdefault(self.synchronizer._compute_hash(parts), []).append(parts)

        self.assertEqual(len(hashes), 1 << (len(word) - 1))
        self.assertTrue(all(len(v) == 1 for v in hashes.values()))

    def test_a_document_that_looks_like_the_length_prefix_does_not_collide(self):
        """The prefix format itself must not become the new collision surface."""
        self.assertNotEqual(
            self.synchronizer._compute_hash(["3:abc"]),
            self.synchronizer._compute_hash(["abc"]),
        )

    def test_the_hash_is_a_sha256_hex_digest(self):
        digest = self.synchronizer._compute_hash(["anything"])

        self.assertEqual(len(digest), 64)
        int(digest, 16)  # raises if it is not hexadecimal


class SyncChangeDetectionTest(unittest.TestCase):
    """End-to-end behaviour of the early return that depends on the hash."""

    def setUp(self):
        self.context_manager = MagicMock()
        self.context_manager.get_context.return_value = []
        self.synchronizer = KnowledgeContextSynchronizer(context_manager=self.context_manager)

    def test_a_boundary_change_is_not_skipped(self):
        """The user-visible consequence: stale context used to survive this."""
        self.synchronizer.sync_knowledge_to_context("kb1", ["ab", "c"], "s1")

        result = self.synchronizer.sync_knowledge_to_context("kb1", ["a", "bc"], "s1")

        self.assertNotIn("skipped", result.details)
        self.assertEqual(result.segments_added, 2)

    def test_an_unchanged_payload_is_still_skipped(self):
        """The opposite direction must not regress: no change, no work."""
        self.synchronizer.sync_knowledge_to_context("kb1", ["x", "y"], "s1")

        result = self.synchronizer.sync_knowledge_to_context("kb1", ["x", "y"], "s1")

        self.assertEqual(result.details.get("skipped"), "No content changes detected")
        self.assertEqual(result.segments_added, 0)

    def test_force_update_bypasses_the_check(self):
        self.synchronizer.sync_knowledge_to_context("kb1", ["x", "y"], "s1")

        result = self.synchronizer.sync_knowledge_to_context(
            "kb1", ["x", "y"], "s1", force_update=True
        )

        self.assertNotIn("skipped", result.details)
        self.assertEqual(result.segments_added, 2)

    def test_a_real_content_change_is_not_skipped(self):
        self.synchronizer.sync_knowledge_to_context("kb1", ["a", "b"], "s1")

        result = self.synchronizer.sync_knowledge_to_context("kb1", ["a", "bcd"], "s1")

        self.assertNotIn("skipped", result.details)


if __name__ == "__main__":
    unittest.main()

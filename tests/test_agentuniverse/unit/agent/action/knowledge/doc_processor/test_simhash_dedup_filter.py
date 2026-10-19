# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_simhash_dedup_filter.py

import random
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.simhash_dedup_filter import SimHashDedupFilter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A 143-word news-like paragraph used as the deduplication base text.
BASE_TEXT = (
    "the central bank raised its benchmark interest rate by a quarter "
    "point on tuesday citing persistent inflation pressure in the services "
    "sector and a tight labour market policymakers voted eight to one in "
    "favor of the move with the dissenting member preferring a larger half "
    "point increase officials signalled that further tightening would "
    "depend on incoming data over the coming months particularly the pace "
    "of wage growth and rental costs financial markets reacted quickly "
    "with two year yields rising several basis points while equity "
    "indices gave up early gains economists polled by the wire services "
    "had expected the smaller move after last month softer consumer price "
    "report the statement dropped previous language describing policy as "
    "accommodative and instead emphasised a balanced approach to both "
    "sides of the mandate analysts said the shift suggests the committee "
    "is nearing the end of its tightening cycle"
)

# One word swapped ("persistent" -> "ongoing"): Hamming distance 3 from
# BASE_TEXT under the default configuration — inside the default threshold.
NEAR_WORD_SWAP = BASE_TEXT.replace("persistent", "ongoing")

# One typographic error ("benchmark" -> "benchhmark"): distance 3 as well.
NEAR_TYPO = BASE_TEXT.replace("benchmark", "benchhmark")

# Punctuation-only rewrite: distance 4 — one bit outside the default
# threshold, which makes it a deterministic boundary probe.
NEAR_PUNCT = BASE_TEXT.replace(" tuesday citing", " tuesday, citing")

# Unrelated prose of similar length: dozens of bits away from BASE_TEXT.
OTHER_TEXT = (
    "quantum computers use qubits that can exist in superposition "
    "which allows certain algorithms to run exponentially faster than "
    "classical machines for factoring large integers and searching "
    "unstructured databases error correction remains the central obstacle "
    "because decoherence destroys delicate quantum states before a "
    "computation finishes recent breakthroughs in logical qubits built "
    "from bundles of physical ones have pushed error rates low enough "
    "that researchers now discuss early commercial applications in "
    "chemistry simulation and materials science with cautious optimism"
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestSimHashDedupFilter(unittest.TestCase):
    """Comprehensive test suite for SimHashDedupFilter."""

    def setUp(self):
        self.filter = SimHashDedupFilter()
        self.query = Query(query_str="deduplication")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: distance 3, bigram shingles, keep_first, insensitive,
        'simhash' / 'dedup_of' metadata keys."""
        f = SimHashDedupFilter()
        self.assertEqual(f.hamming_threshold, 3)
        self.assertEqual(f.shingle_size, 2)
        self.assertEqual(f.keep_policy, "first")
        self.assertFalse(f.case_sensitive)
        self.assertEqual(f.simhash_key, "simhash")
        self.assertEqual(f.dedup_of_key, "dedup_of")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'simhash_dedup_filter',
            'description': 'simhash dedup filter',
            'hamming_threshold': 6,
            'shingle_size': 3,
            'keep_policy': 'longest',
            'case_sensitive': True,
            'simhash_key': 'fingerprint',
            'dedup_of_key': 'duplicate_of',
        })
        f = SimHashDedupFilter()
        f._initialize_by_component_configer(configer)
        self.assertEqual(f.hamming_threshold, 6)
        self.assertEqual(f.shingle_size, 3)
        self.assertEqual(f.keep_policy, "longest")
        self.assertTrue(f.case_sensitive)
        self.assertEqual(f.simhash_key, "fingerprint")
        self.assertEqual(f.dedup_of_key, "duplicate_of")
        self.assertEqual(f.name, "simhash_dedup_filter")

    def test_invalid_configuration_raises(self):
        """Out-of-range threshold / shingle size, non-integer values, bad
        keep_policy and non-string metadata keys all fail at load time."""
        base = {
            'name': 'f', 'description': 'd',
            'hamming_threshold': 3, 'shingle_size': 2,
            'keep_policy': 'first', 'case_sensitive': False,
            'simhash_key': 'simhash', 'dedup_of_key': 'dedup_of',
        }
        for key, value in (
            ('hamming_threshold', -1),
            ('hamming_threshold', 65),
            ('hamming_threshold', 2.5),
            ('hamming_threshold', True),
            ('shingle_size', 0),
            ('shingle_size', -2),
            ('shingle_size', 1.5),
            ('keep_policy', 'random'),
            ('simhash_key', 5),
            ('dedup_of_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                SimHashDedupFilter()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Fingerprint math tests ==========

    def test_shingle_hash_is_stable_md5_slice(self):
        """The shingle hash is the first 8 MD5 digest bytes, big-endian —
        a stable value independent of PYTHONHASHSEED (unlike hash())."""
        import hashlib
        expected = int.from_bytes(hashlib.md5(b"a b").digest()[:8], "big")
        self.assertEqual(SimHashDedupFilter._shingle_hash("a b"), expected)
        self.assertEqual(expected, 921493332900466999)

    def test_simhash_of_single_token_is_md5_slice(self):
        """A document of one token has one shingle whose unanimous votes
        reproduce the shingle hash itself; 'hello' pins MD5 exactly."""
        fingerprint = self.filter._simhash("hello")
        self.assertEqual(fingerprint, 0x5d41402abc4b2a76)

    def test_simhash_deterministic_and_64_bit(self):
        """Identical inputs yield identical fingerprints across instances,
        and every fingerprint fits in 64 bits; one long-text vector is
        pinned for regression stability."""
        other = SimHashDedupFilter()
        for text in (BASE_TEXT, OTHER_TEXT, "two tokens only", ""):
            self.assertEqual(self.filter._simhash(text),
                             other._simhash(text), text[:30])
            self.assertTrue(0 <= self.filter._simhash(text) < 2 ** 64)
        self.assertEqual(self.filter._simhash(BASE_TEXT),
                         0x11184ae749190af6)

    def test_hamming_distance_correctness(self):
        """Hand-checked values plus randomized agreement with popcount."""
        hamming = SimHashDedupFilter._hamming
        self.assertEqual(hamming(0, 0), 0)
        self.assertEqual(hamming(0b1010, 0b0110), 2)
        self.assertEqual(hamming(0, (1 << 64) - 1), 64)
        self.assertEqual(hamming(0x11184ae749190af6, 0x7a24ae03187ff3cf),
                         bin(0x11184ae749190af6 ^ 0x7a24ae03187ff3cf)
                         .count("1"))
        rng = random.Random(258)
        for _ in range(200):
            a, b = rng.getrandbits(64), rng.getrandbits(64)
            self.assertEqual(hamming(a, b), bin(a ^ b).count("1"))

    def test_similar_texts_close_and_distinct_texts_far(self):
        """Real near-rewrites land within the default threshold while
        unrelated texts of similar length sit dozens of bits away."""
        f = self.filter
        distance = lambda a, b: f._hamming(f._simhash(a), f._simhash(b))
        self.assertEqual(distance(BASE_TEXT, BASE_TEXT), 0)
        self.assertEqual(distance(BASE_TEXT, NEAR_WORD_SWAP), 3)
        self.assertEqual(distance(BASE_TEXT, NEAR_TYPO), 3)
        self.assertEqual(distance(BASE_TEXT, NEAR_PUNCT), 4)
        self.assertGreater(distance(BASE_TEXT, OTHER_TEXT), 20)
        self.assertGreater(distance(BASE_TEXT, NEAR_WORD_SWAP), -1)
        self.assertGreaterEqual(distance(BASE_TEXT, OTHER_TEXT),
                                f.hamming_threshold + 1)

    # ========== Deduplication behavior tests ==========

    def test_exact_duplicates_removed(self):
        """Byte-identical texts (regardless of metadata) collapse to the
        single first document."""
        docs = [
            _doc(BASE_TEXT, source="feed-a"),
            _doc(OTHER_TEXT, source="feed-a"),
            _doc(BASE_TEXT, source="feed-b"),
            _doc(BASE_TEXT, source="feed-c"),
        ]
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].metadata["source"], "feed-a")
        self.assertEqual(result[1].text, OTHER_TEXT)

    def test_near_duplicates_with_small_edits_removed(self):
        """A word swap and a typo variant of the base text are removed at
        the default threshold (distance 3)."""
        docs = [_doc(BASE_TEXT), _doc(NEAR_WORD_SWAP),
                _doc(NEAR_TYPO), _doc(OTHER_TEXT)]
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [BASE_TEXT, OTHER_TEXT])

    def test_distinct_documents_all_kept(self):
        """Unrelated documents survive; nothing is marked as a duplicate."""
        docs = [_doc(BASE_TEXT), _doc(OTHER_TEXT),
                _doc("quarterly revenue grew twelve percent year over year")]
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual(len(result), 3)
        for doc in result:
            self.assertNotIn("dedup_of", doc.metadata)

    def test_threshold_boundary_inclusive(self):
        """At distance exactly 4: threshold 4 removes (inclusive), while
        the default threshold 3 keeps the pair."""
        self.assertEqual(
            self.filter._hamming(self.filter._simhash(BASE_TEXT),
                                 self.filter._simhash(NEAR_PUNCT)), 4)
        docs = [_doc(BASE_TEXT), _doc(NEAR_PUNCT)]

        self.filter.hamming_threshold = 4
        self.assertEqual(len(self.filter.process_docs(docs, self.query)), 1)

        self.filter.hamming_threshold = 3
        self.assertEqual(len(self.filter.process_docs(docs, self.query)), 2)

    def test_zero_threshold_only_exact_duplicates(self):
        """Threshold 0 collapses identical texts (case folding included)
        but keeps any rewrite, even one a single bit-distance away."""
        self.filter.hamming_threshold = 0
        docs = [_doc(BASE_TEXT), _doc(BASE_TEXT.upper()),
                _doc(NEAR_PUNCT)]
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual(len(result), 2)
        self.assertIn(NEAR_PUNCT, [d.text for d in result])

    def test_case_insensitive_by_default_and_case_sensitive_option(self):
        """Case-only rewrites deduplicate by default; with
        case_sensitive=True the same pair is kept apart."""
        docs = [_doc("The Central Bank Raised Rates Again This Morning"),
                _doc("the central bank raised rates again this morning")]
        self.assertEqual(
            len(self.filter.process_docs(docs, self.query)), 1)

        self.filter.case_sensitive = True
        self.assertEqual(
            len(self.filter.process_docs(docs, self.query)), 2)

    def test_shingle_size_change_recalculates_fingerprints(self):
        """Shingle width is a real knob: trigram shingles move the base
        fingerprint away from the bigram vector."""
        f = SimHashDedupFilter()
        bigram = f._simhash(BASE_TEXT)
        f.shingle_size = 3
        trigram = f._simhash(BASE_TEXT)
        self.assertNotEqual(bigram, trigram)
        self.assertGreaterEqual(f._hamming(bigram, trigram), 0)

    def test_blank_and_empty_documents(self):
        """Empty input yields empty output; blank texts share fingerprint
        0 and collapse together, yet never swallow a non-blank document;
        None text is tolerated by the fingerprinting itself."""
        self.assertEqual(self.filter.process_docs([], self.query), [])

        self.assertEqual(self.filter._simhash(None), 0)
        docs = [_doc(""), _doc("   "), _doc(OTHER_TEXT)]
        for blank in ("", "   "):
            self.assertEqual(self.filter._simhash(blank), 0)
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].text, "")
        self.assertEqual(result[1].text, OTHER_TEXT)

    # ========== Metadata bookkeeping tests ==========

    def test_metadata_recorded_for_kept_and_removed(self):
        """Kept documents carry the 16-hex fingerprint; removed document
        objects carry the representative's id under 'dedup_of'."""
        base, other, dup = _doc(BASE_TEXT), _doc(OTHER_TEXT), \
            _doc(NEAR_WORD_SWAP)
        result = self.filter.process_docs([base, other, dup], self.query)

        self.assertEqual(result[0].metadata["simhash"],
                         format(self.filter._simhash(BASE_TEXT), "016x"))
        self.assertEqual(len(result[0].metadata["simhash"]), 16)
        self.assertNotIn("dedup_of", result[0].metadata)

        self.assertNotIn("dedup_of", other.metadata)
        self.assertEqual(dup.metadata["dedup_of"], base.id)

    def test_keep_policy_longest_keeps_most_content(self):
        """keep_policy='longest' swaps the representative to the member
        with more text (a one-word insertion whose fingerprint distance is
        0), placed at the cluster's first-occurrence position; the
        earlier, shorter copy is marked as its duplicate."""
        short = _doc(BASE_TEXT)
        longer = _doc(BASE_TEXT.replace(" rate", " lending rate"))
        self.assertGreater(len(longer.text), len(short.text))
        self.assertEqual(self.filter._hamming(
            self.filter._simhash(short.text),
            self.filter._simhash(longer.text)), 0)

        self.filter.keep_policy = "longest"
        result = self.filter.process_docs([short, longer], self.query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, longer.text)
        self.assertEqual(short.metadata["dedup_of"], longer.id)

    def test_keep_policy_first_ignores_later_longer_copy(self):
        """Under the default 'first' policy the first occurrence survives
        even when a near-duplicate carries more content."""
        first = _doc(BASE_TEXT)
        longer = _doc(BASE_TEXT.replace(" rate", " lending rate"))
        result = self.filter.process_docs([first, longer], self.query)
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], first)
        self.assertEqual(longer.metadata["dedup_of"], first.id)

    def test_disabled_metadata_keys_stamp_nothing(self):
        """Empty simhash_key / dedup_of_key disable both stamps."""
        self.filter.simhash_key = ""
        self.filter.dedup_of_key = ""
        base = _doc(BASE_TEXT, source="wire")
        dup = _doc(NEAR_TYPO, source="mirror")
        result = self.filter.process_docs([base, dup], self.query)
        self.assertEqual(len(result), 1)
        self.assertEqual(base.metadata, {"source": "wire"})
        self.assertEqual(dup.metadata, {"source": "mirror"})

    # ========== Pipeline-shape tests ==========

    def test_order_preserved_by_first_occurrence(self):
        """Survivors appear in the order their clusters were first seen,
        keeping the input's relative order."""
        docs = [_doc(OTHER_TEXT), _doc(BASE_TEXT), _doc(NEAR_WORD_SWAP),
                _doc("an isolated short note about nothing in particular"),
                _doc(NEAR_TYPO)]
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [OTHER_TEXT, BASE_TEXT,
                          "an isolated short note about nothing in "
                          "particular"])

    def test_input_documents_not_corrupted(self):
        """Text and id are untouched; pre-existing metadata entries
        survive on kept and removed documents alike; and stamping writes
        through a copy rather than mutating the original mapping."""
        base = _doc(BASE_TEXT, source="wire", rank=1)
        dup = _doc(NEAR_TYPO, source="mirror", rank=2)
        base_meta_ref = base.metadata
        dup_meta_ref = dup.metadata

        result = self.filter.process_docs([base, dup], self.query)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, BASE_TEXT)
        self.assertEqual(result[0].id, base.id)
        self.assertEqual(base.metadata["source"], "wire")
        self.assertEqual(base.metadata["rank"], 1)
        self.assertEqual(dup.text, NEAR_TYPO)
        self.assertEqual(dup.metadata["source"], "mirror")
        self.assertEqual(dup.metadata["rank"], 2)
        # Stamp went through a copied mapping: the caller's original dict
        # objects did not gain the new keys in place.
        self.assertNotIn("simhash", base_meta_ref)
        self.assertNotIn("dedup_of", dup_meta_ref)
        self.assertIsNot(base.metadata, base_meta_ref)

    def test_duplicates_across_multiple_clusters(self):
        """Two independent near-duplicate pairs reduce to exactly two
        documents in first-occurrence order."""
        docs = [_doc(BASE_TEXT), _doc(NEAR_WORD_SWAP),
                _doc(OTHER_TEXT), _doc(OTHER_TEXT.upper())]
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [BASE_TEXT, OTHER_TEXT])
        self.assertEqual(docs[1].metadata["dedup_of"], docs[0].id)
        self.assertEqual(docs[3].metadata["dedup_of"], docs[2].id)


if __name__ == '__main__':
    unittest.main()

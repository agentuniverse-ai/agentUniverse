# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: simhash_dedup_filter.py

import hashlib
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Width of the SimHash fingerprint in bits.
_FINGERPRINT_BITS = 64


class SimHashDedupFilter(DocProcessor):
    """Remove near-duplicate documents via SimHash fingerprints.

    Ingested corpora are rarely clean: the same story is picked up by
    several feeds with a rewritten word or two, mirror sites republish
    articles verbatim, and crawls overlap between runs. Feeding such
    near-duplicates into a knowledge base wastes embedding budget and lets
    duplicate chunks crowd out distinct hits at recall time. This processor
    fingerprints every document with a 64-bit SimHash — a locality-sensitive
    sketch with the property that texts differing only slightly produce
    fingerprints differing in only a few bits — and drops documents whose
    fingerprint is within ``hamming_threshold`` bits of one already kept in
    the same batch.

    The fingerprint pipeline is pure Python, deterministic and offline:

    1. the text is tokenized on whitespace (lowercased unless
       ``case_sensitive``);
    2. consecutive tokens are grouped into word shingles (n-grams) of
       ``shingle_size`` tokens (default 2) — a document shorter than the
       window yields a single whole-sequence shingle;
    3. every shingle is hashed with MD5 (first 8 digest bytes, big-endian)
       — deliberately NOT Python's built-in ``hash()``, which is salted per
       process and would make fingerprints non-reproducible;
    4. each of the 64 fingerprint bits collects a +1/-1 vote per shingle
       depending on the corresponding hash bit; the majority sign wins.

    Two documents are treated as near-duplicates when the Hamming distance
    between their fingerprints is at most ``hamming_threshold`` (default 3).
    Each cluster of near-duplicates is reduced to a single representative:
    the first occurrence under ``keep_policy='first'``, or the member with
    the longest text under ``keep_policy='longest'`` (ties go to the
    earliest). Note that near-duplication is not transitive; matching is a
    single greedy pass against each cluster's current representative, and
    survivors keep the order of their cluster's first occurrence.

    Bookkeeping lands in document metadata: every kept document carries its
    fingerprint in ``metadata[simhash_key]`` (16 hex chars), and every
    removed document object is marked with the representative's id in
    ``metadata[dedup_of_key]`` so callers holding the original list can see
    why a document vanished. Metadata mappings are copied before mutation,
    and text / id / other metadata fields are never modified. This makes the
    component complementary to ``SemanticDeduplicator``: that one needs an
    embedding model for semantic similarity, while this one is dependency-
    free, deterministic and fast — suited to pre-insertion cleanup where
    near-identical text is the problem.

    Comparison cost is quadratic in the batch size (each document against
    each cluster representative), which is the right trade-off for the
    bounded batches processed at knowledge-insertion time.

    Attributes:
        hamming_threshold: Maximum Hamming distance between fingerprints
            for two documents to count as near-duplicates, in [0, 64].
        shingle_size: Number of tokens per word shingle; must be >= 1.
            The default 2 (bigrams) pairs well with the default Hamming
            threshold: on prose-length documents a single-word rewrite
            lands within 3 bits while unrelated texts sit dozens of bits
            apart.
        keep_policy: Which member of a near-duplicate cluster survives —
            ``first`` (default) or ``longest`` (most content; earliest wins
            ties).
        case_sensitive: When false (default), tokens are lowercased before
            shingling so case-only rewrites deduplicate.
        simhash_key: Metadata key the fingerprint hex string is written to
            on kept documents; an empty value disables stamping.
        dedup_of_key: Metadata key the representative's id is written to on
            removed document objects; an empty value disables stamping.
    """

    hamming_threshold: int = 3
    shingle_size: int = 2
    keep_policy: str = "first"
    case_sensitive: bool = False
    simhash_key: str = "simhash"
    dedup_of_key: str = "dedup_of"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Drop near-duplicate documents from the batch.

        Args:
            origin_docs: Documents to deduplicate, in batch order.
            query: Query object (unused; deduplication depends only on the
                documents' own text).

        Returns:
            List[Document]: One representative per near-duplicate cluster,
            in order of each cluster's first occurrence, each stamped with
            its SimHash fingerprint.
        """
        if not origin_docs:
            return []

        texts = [doc.text or "" for doc in origin_docs]
        fingerprints = [self._simhash(text) for text in texts]

        # Greedy single-pass clustering: each document joins the first
        # cluster whose current representative is within the Hamming
        # threshold, otherwise it opens a new cluster. Clusters are kept in
        # first-seen order so the output preserves batch order.
        clusters: List[dict] = []
        for idx, fingerprint in enumerate(fingerprints):
            for cluster in clusters:
                rep = cluster["rep"]
                if self._hamming(fingerprint, fingerprints[rep]) <= \
                        self.hamming_threshold:
                    cluster["members"].append(idx)
                    # 'longest' lets a later, more substantial copy take
                    # over the cluster; '>=' is deliberately avoided so the
                    # earliest member wins ties.
                    if self.keep_policy == "longest" and \
                            len(texts[idx]) > len(texts[rep]):
                        cluster["rep"] = idx
                    break
            else:
                clusters.append({"rep": idx, "members": [idx]})

        kept: List[Document] = []
        for cluster in clusters:
            rep_idx = cluster["rep"]
            rep_doc = origin_docs[rep_idx]
            if self.simhash_key:
                self._stamp(rep_doc, self.simhash_key,
                            self._format(fingerprints[rep_idx]))
            if self.dedup_of_key:
                for member in cluster["members"]:
                    if member != rep_idx:
                        self._stamp(origin_docs[member], self.dedup_of_key,
                                    rep_doc.id)
            kept.append(rep_doc)
        return kept

    # ------------------------------------------------------------------ #
    # Fingerprinting helpers
    # ------------------------------------------------------------------ #

    def _simhash(self, text: str) -> int:
        """Compute the 64-bit SimHash fingerprint of one text.

        Args:
            text: Document text (None treated as empty).

        Returns:
            int: 64-bit fingerprint; 0 for text without any shingle.
        """
        shingles = self._shingles(self._tokenize(text))
        if not shingles:
            return 0

        votes = [0] * _FINGERPRINT_BITS
        for shingle in shingles:
            value = self._shingle_hash(shingle)
            for bit in range(_FINGERPRINT_BITS):
                votes[bit] += 1 if (value >> bit) & 1 else -1

        fingerprint = 0
        for bit, vote in enumerate(votes):
            if vote > 0:
                fingerprint |= 1 << bit
        return fingerprint

    def _tokenize(self, text: str) -> List[str]:
        """Split text into whitespace tokens, optionally lowercased.

        Args:
            text: Raw document text.

        Returns:
            List[str]: Token list; empty for blank text.
        """
        value = text or ""
        if not self.case_sensitive:
            value = value.lower()
        return value.split()

    def _shingles(self, tokens: List[str]) -> List[str]:
        """Group tokens into word shingles (n-grams).

        A token sequence shorter than the window degrades to one shingle
        covering the whole sequence, so short documents still receive a
        meaningful fingerprint instead of none.

        Args:
            tokens: Token list.

        Returns:
            List[str]: Space-joined shingles of ``shingle_size`` tokens.
        """
        size = self.shingle_size
        if not tokens:
            return []
        if len(tokens) <= size:
            return [" ".join(tokens)]
        return [" ".join(tokens[i:i + size])
                for i in range(len(tokens) - size + 1)]

    @staticmethod
    def _shingle_hash(shingle: str) -> int:
        """Hash one shingle to a stable unsigned 64-bit integer.

        MD5's first 8 digest bytes are read big-endian. MD5 is used purely
        as a stable bit mixer — not for security — and unlike Python's
        built-in ``hash()`` its output is identical across processes,
        interpreters and PYTHONHASHSEED values, which keeps fingerprints
        reproducible in stored metadata.

        Args:
            shingle: Space-joined token shingle.

        Returns:
            int: Unsigned 64-bit hash value.
        """
        digest = hashlib.md5(shingle.encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big")

    @staticmethod
    def _hamming(value: int, other: int) -> int:
        """Count differing bits between two 64-bit fingerprints.

        Args:
            value: First fingerprint.
            other: Second fingerprint.

        Returns:
            int: Hamming distance in [0, 64].
        """
        return bin(value ^ other).count("1")

    @staticmethod
    def _format(fingerprint: int) -> str:
        """Render a fingerprint as a 16-character lowercase hex string.

        Args:
            fingerprint: 64-bit fingerprint.

        Returns:
            str: Zero-padded hex representation.
        """
        return format(fingerprint, "016x")

    def _stamp(self, doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            key: Metadata key.
            value: Metadata value.
        """
        meta = dict(doc.metadata or {})
        meta[key] = value
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'SimHashDedupFilter':
        """Initialize and validate the filter from component configuration.

        Validation happens eagerly at load time: a misconfigured dedup
        filter that silently kept every duplicate would be far harder to
        notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            SimHashDedupFilter: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "hamming_threshold") and \
                doc_processor_configer.hamming_threshold is not None:
            threshold = doc_processor_configer.hamming_threshold
            if isinstance(threshold, bool) or not isinstance(threshold, int):
                raise ValueError("hamming_threshold must be an integer")
            self.hamming_threshold = threshold
            if not 0 <= self.hamming_threshold <= _FINGERPRINT_BITS:
                raise ValueError(
                    "hamming_threshold must be in [0, "
                    f"{_FINGERPRINT_BITS}]")

        if hasattr(doc_processor_configer, "shingle_size") and \
                doc_processor_configer.shingle_size is not None:
            size = doc_processor_configer.shingle_size
            if isinstance(size, bool) or not isinstance(size, int):
                raise ValueError("shingle_size must be an integer")
            self.shingle_size = size
            if self.shingle_size < 1:
                raise ValueError("shingle_size must be >= 1")

        if hasattr(doc_processor_configer, "keep_policy") and \
                doc_processor_configer.keep_policy is not None:
            self.keep_policy = doc_processor_configer.keep_policy
            if self.keep_policy not in ("first", "longest"):
                raise ValueError(
                    "keep_policy must be 'first' or 'longest', got "
                    f"'{self.keep_policy}'")

        if hasattr(doc_processor_configer, "case_sensitive") and \
                doc_processor_configer.case_sensitive is not None:
            self.case_sensitive = bool(doc_processor_configer.case_sensitive)

        if hasattr(doc_processor_configer, "simhash_key") and \
                doc_processor_configer.simhash_key is not None:
            key = doc_processor_configer.simhash_key
            if not isinstance(key, str):
                raise ValueError("simhash_key must be a string")
            self.simhash_key = key

        if hasattr(doc_processor_configer, "dedup_of_key") and \
                doc_processor_configer.dedup_of_key is not None:
            key = doc_processor_configer.dedup_of_key
            if not isinstance(key, str):
                raise ValueError("dedup_of_key must be a string")
            self.dedup_of_key = key

        return self

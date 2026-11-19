# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: duplicate_sentence_filter.py

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Terminal punctuation (Latin and CJK): a run of these characters followed
# by whitespace, end-of-text or any non-ASCII-alphanumeric character closes
# a sentence. Runs allow "!!!" and "?!".
_TERMINAL_CHARS = frozenset(".!?…。！？")

# Punctuation stripped from the tail of a normalized sentence key, so
# "Hello." / "hello!" / 'Hello..."' share one key.
_TRAILING_PUNCT = ".,!?:;'\"`”’)]}»›*…。！？；：）》〉】』」・·〜～"

# Edge punctuation also stripped from both ends of each token before
# token-set comparison in near mode (openers plus the trailing set).
_TOKEN_EDGE_PUNCT = _TRAILING_PUNCT + "([{«‹（《〈【『「"

# Maximum number of per-sentence entries kept in
# metadata['duplicate_sentences']; duplicate_count always reports the full
# total.
_MAX_REMOVAL_ENTRIES = 50

# Two sentences are compared in near mode only when their distinct-token
# counts differ by at most this window (see class docstring for the exact
# guarantee this buys).
_BUCKET_WINDOW = 2


def _closes_sentence(char: str) -> bool:
    """Report whether the character after a terminal punctuation run
    ends the current sentence.

    ASCII letters and digits glue the run to the current word ("3.14",
    "e.g."); whitespace, end-of-text is handled by the caller, and any
    non-ASCII character (CJK ideographs, closing quotes, brackets)
    closes the sentence.

    Args:
        char: The character following a terminal run.

    Returns:
        bool: True when the terminal run closes the sentence.
    """
    return not (char.isascii() and char.isalnum())


class DuplicateSentenceFilter(DocProcessor):
    """Remove repeated sentences within each document.

    Texts arriving at a knowledge base repeat themselves at the sentence
    level far more often than at the document level: scraped pages staple
    the same disclaimer or navigation blurb onto every section, legal
    documents restate the same clause in every exhibit, and LLM-generated
    text loops on a sentence when it runs out of things to say. A splitter
    downstream then emits several identical chunks, wasting embedding
    budget and letting the repeated sentence crowd out distinct hits at
    recall time. This processor segments each document into sentences,
    keeps one occurrence per repeated sentence and rebuilds the text
    without the others.

    Segmentation is deliberately conservative: a sentence ends only at a
    run of terminal punctuation (``. ! ? … 。 ！ ？``) followed by
    whitespace, end-of-text or any character that is not an ASCII
    letter/digit — CJK sentences split at ``。`` with no intervening
    space, while a period glued to ASCII alphanumerics never splits, so
    decimals (``3.14``) and dotted abbreviations (``e.g.``) stay intact.
    An abbreviation that happens to end with a period followed by a
    space (``Mr.``) does split; no abbreviation dictionary is attempted.
    Whitespace-only separators (blank lines without punctuation) never
    split.

    Each sentence is identified by a normalized key: casefolded,
    internal whitespace collapsed to single spaces, and trailing
    punctuation (including closing quotes/brackets) stripped — so
    ``"Hello world."``, ``hello   world!`` and ``HELLO WORLD...`` share
    one key. Leading punctuation is deliberately kept so quoted and
    unquoted sentences are only merged when their trailing form matches.

    Two modes decide what counts as a repeat:

    * ``mode='exact'`` (default): a later sentence whose key equals an
      earlier kept key is a duplicate (similarity 1.0).
    * ``mode='near'``: additionally, sentences whose token sets (casefolded
      words, edge punctuation stripped) reach Jaccard similarity
      ``|A ∩ B| / |A ∪ B| >= jaccard_threshold`` (default 0.9, inclusive)
      count as near-duplicates — catching "The report is final today."
      against "The report is final now.".

    Near-mode comparison is bucketed to stay linear in practice: kept
    sentences are indexed by their number of *distinct* tokens, and a
    candidate is compared only against kept sentences whose count differs
    by at most 2 (a "sliding length-class bucket"). The guarantee this
    buys: because Jaccard is bounded by ``min/max`` token-set sizes, two
    sentences at threshold >= 0.9 with count difference <= 2 are always
    compared — bucketing never misses such true duplicates. Pairs whose
    counts differ by 3 or more are intentionally not compared; at the
    default 0.9 threshold such a pair can only reach the threshold when
    the smaller sentence already has >= 27 distinct tokens (a gap of 3
    forces ``min >= 3t/(1-t) = 27``), so the window trades that corner
    case for short comparison lists. Exact-normalized equals always share
    one token-set size and are therefore always caught.

    By default the FIRST occurrence is kept and later ones dropped (the
    canonical reading order); ``keep_last=True`` flips this to keep the
    LAST occurrence — useful when later repeats reflect the most recent
    wording, e.g. re-issued boilerplate. Every removal is stamped into
    metadata: ``duplicate_sentences`` (capped at 50 entries, each
    ``{index, length, span, similarity}`` — sentence ordinal, character
    length, ``[start, end]`` offsets in the ORIGINAL text, and 1.0 for
    exact / the Jaccard value for near), plus the uncapped
    ``duplicate_count`` and the active ``duplicate_mode``. Metadata
    mappings are copied before mutation.

    The rebuilt text joins the kept sentences with their ORIGINAL
    inter-sentence whitespace (the exact gap bytes between two adjacent
    kept sentences are preserved): each dropped sentence takes its
    preceding separator with it, the rebuilt text never starts with the
    separator of a removed leading sentence, and a trailing gap is kept
    only when the final sentence survives. When nothing is removed the
    text is returned byte-identical. Punctuation-only sentences
    (normalizing to an empty key, e.g. lone ``!`` or ``。``) are never
    treated as duplicates of each other.

    The component is pure Python, deterministic (no salted ``hash()``, no
    randomness, insertion-ordered iteration only) and fully offline. It
    operates WITHIN one document, which makes it complementary to
    ``SimHashDedupFilter`` / ``SemanticDeduplicator`` — those drop
    near-identical whole DOCUMENTS across a batch — and to line-level
    boilerplate removal across a corpus: this filter cleans the inside of
    a single text.

    Attributes:
        mode: ``'exact'`` (normalized-key equality, default) or ``'near'``
            (adds token-set Jaccard comparison).
        jaccard_threshold: Minimum token-set Jaccard similarity for two
            sentences to count as near-duplicates, in (0, 1]; default 0.9,
            compared with ``>=``. Only used in near mode.
        keep_last: When false (default) keep the first occurrence of a
            repeated sentence; when true keep the last occurrence and
            drop the earlier ones.
    """

    mode: str = "exact"
    jaccard_threshold: float = 0.9
    keep_last: bool = False

    def _process_docs(self, origin_docs: list[Document],
                      query: Query = None) -> list[Document]:
        """Rewrite each document with repeated sentences removed.

        Args:
            origin_docs: Documents whose texts are cleaned sentence by
                sentence; every document is kept in the output.
            query: Query object (unused; deduplication depends only on
                the documents' own text).

        Returns:
            List[Document]: The same documents, in batch order, each with
            duplicate sentences removed from its text and removal
            bookkeeping stamped into metadata.
        """
        for doc in origin_docs:
            self._process_one(doc)
        return origin_docs

    def _process_one(self, doc: Document) -> None:
        """Deduplicate the sentences of one document, in place.

        Args:
            doc: Document whose text is rewritten and whose metadata
                receives the removal record.
        """
        original = doc.text
        text = original or ""
        spans = self._segment(text)
        if not spans:
            # No sentences at all (empty / whitespace-only text): nothing
            # to deduplicate; text is left exactly as it was.
            self._stamp(doc, [], self.mode)
            return

        sentences = [text[s:e] for s, e in spans]
        keys = [self._normalize(sentence) for sentence in sentences]
        kept = [True] * len(sentences)
        removals: list[dict] = []

        if self.mode == "near":
            self._dedup_near(keys, spans, kept, removals)
        else:
            self._dedup_exact(keys, spans, kept, removals)

        rebuilt = self._rebuild(text, spans, kept)
        doc.text = rebuilt if removals else original
        self._stamp(doc, removals, self.mode)

    # ------------------------------------------------------------------ #
    # Deduplication strategies
    # ------------------------------------------------------------------ #

    def _dedup_exact(self, keys: list[str], spans: list[tuple[int, int]],
                     kept: list[bool], removals: list[dict]) -> None:
        """Drop later sentences whose normalized key was already kept.

        ``keep_last`` flips the direction: an earlier occurrence is
        dropped in favour of the later one that replaces it as the
        group's representative.

        Args:
            keys: Normalized sentence keys, in sentence order.
            spans: Sentence [start, end) offsets in the original text.
            kept: Per-sentence keep flags, mutated in place.
            removals: Removal record list, appended in sentence order.
        """
        seen: dict[str, int] = {}
        for idx, key in enumerate(keys):
            if not key:
                # Punctuation-only sentence: never a duplicate.
                continue
            if key in seen:
                if self.keep_last:
                    prev = seen[key]
                    kept[prev] = False
                    removals.append(self._entry(prev, spans, 1.0))
                    seen[key] = idx
                else:
                    kept[idx] = False
                    removals.append(self._entry(idx, spans, 1.0))
            else:
                seen[key] = idx

    def _dedup_near(self, keys: list[str], spans: list[tuple[int, int]],
                    kept: list[bool], removals: list[dict]) -> None:
        """Drop sentences near-duplicate to an already-kept sentence.

        Kept sentences are bucketed by distinct-token count; a candidate
        is compared only against kept sentences whose count lies within
        ``_BUCKET_WINDOW`` of its own (see the class docstring for the
        completeness guarantee and the deliberately unmatched corner).
        The best (highest-Jaccard, earliest on ties) surviving match
        above the threshold decides the outcome.

        Args:
            keys: Normalized sentence keys, in sentence order.
            spans: Sentence [start, end) offsets in the original text.
            kept: Per-sentence keep flags, mutated in place.
            removals: Removal record list, appended in sentence order.
        """
        buckets: dict[int, list[dict]] = {}
        for idx, key in enumerate(keys):
            tokens = self._token_set(key)
            if not tokens:
                # Punctuation-only sentence: never a duplicate.
                continue
            count = len(tokens)
            best = None
            best_similarity = -1.0
            for offset in range(-_BUCKET_WINDOW, _BUCKET_WINDOW + 1):
                for record in buckets.get(count + offset, ()):
                    if not record["alive"]:
                        continue
                    similarity = self._jaccard(tokens, record["tokens"])
                    if similarity >= self.jaccard_threshold and \
                            similarity > best_similarity:
                        best = record
                        best_similarity = similarity
            if best is not None:
                if self.keep_last:
                    # The later occurrence replaces the earlier one as
                    # the group's representative.
                    best["alive"] = False
                    kept[best["idx"]] = False
                    removals.append(
                        self._entry(best["idx"], spans, best_similarity))
                else:
                    kept[idx] = False
                    removals.append(
                        self._entry(idx, spans, best_similarity))
                    continue
            record = {"tokens": tokens, "idx": idx, "alive": True}
            buckets.setdefault(count, []).append(record)

    # ------------------------------------------------------------------ #
    # Segmentation, normalization and comparison helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _segment(text: str) -> list[tuple[int, int]]:
        """Split text into sentence spans, conservatively.

        A sentence closes at a run of terminal punctuation followed by
        whitespace, end-of-text or a non-ASCII-alphanumeric character
        (so CJK text splits at ``。`` without spaces while ``3.14`` and
        ``e.g.`` stay intact); spans exclude the surrounding whitespace
        and include their closing punctuation. Text without any boundary
        yields one whole-text sentence.

        Args:
            text: Document text (None already normalized to "").

        Returns:
            List[Tuple[int, int]]: [start, end) character offsets of each
            sentence, in document order.
        """
        spans: list[tuple[int, int]] = []
        length = len(text)
        i = 0
        while i < length and text[i].isspace():
            i += 1
        start = i
        while i < length:
            if text[i] in _TERMINAL_CHARS:
                end = i + 1
                while end < length and text[end] in _TERMINAL_CHARS:
                    end += 1
                if end >= length or _closes_sentence(text[end]):
                    spans.append((start, end))
                    i = end
                    while i < length and text[i].isspace():
                        i += 1
                    start = i
                    continue
                # Terminal run glued to ASCII letters/digits ("3.14",
                # "e.g."): keep scanning from the end of the run.
                i = end
                continue
            i += 1
        if start < length:
            spans.append((start, length))
        return spans

    @staticmethod
    def _normalize(sentence: str) -> str:
        """Compute the normalized key of one sentence.

        Casefold, collapse all internal whitespace runs to single spaces
        and strip trailing punctuation (including closing quotes and
        brackets). Leading punctuation is kept on purpose — see the class
        docstring.

        Args:
            sentence: Sentence text with its closing punctuation.

        Returns:
            str: Normalized key; empty for punctuation-only sentences.
        """
        collapsed = " ".join(sentence.split())
        return collapsed.casefold().rstrip(_TRAILING_PUNCT)

    @staticmethod
    def _token_set(key: str) -> set[str]:
        """Build the comparison token set of a normalized key.

        Tokens are the whitespace-split words of the key with edge
        punctuation stripped, so "quick, brown" and "quick brown" share
        their set.

        Args:
            key: Normalized sentence key.

        Returns:
            Set[str]: Distinct tokens; empty for punctuation-only keys.
        """
        tokens: set[str] = set()
        for raw in key.split():
            token = raw.strip(_TOKEN_EDGE_PUNCT)
            if token:
                tokens.add(token)
        return tokens

    @staticmethod
    def _jaccard(first: set[str], second: set[str]) -> float:
        """Token-set Jaccard similarity |A ∩ B| / |A ∪ B|.

        Args:
            first: First token set.
            second: Second token set.

        Returns:
            float: Similarity in [0.0, 1.0]; 0.0 when either set is
            empty (never called with empty sets by the caller).
        """
        if not first or not second:
            return 0.0
        intersection = len(first & second)
        if not intersection:
            return 0.0
        return intersection / (len(first) + len(second) - intersection)

    @staticmethod
    def _entry(idx: int, spans: list[tuple[int, int]],
               similarity: float) -> dict:
        """Build one removal-record entry for the metadata stamp.

        Args:
            idx: Sentence ordinal of the removed occurrence.
            spans: Sentence [start, end) offsets in the original text.
            similarity: 1.0 for exact matches, the Jaccard value
                otherwise.

        Returns:
            dict: ``{index, length, span, similarity}`` where length is
            the character length and span the original-text offsets.
        """
        start, end = spans[idx]
        return {"index": idx, "length": end - start, "span": [start, end],
                "similarity": similarity}

    @staticmethod
    def _rebuild(text: str, spans: list[tuple[int, int]],
                 kept: list[bool]) -> str:
        """Rejoin the kept sentences with their original separators.

        Each dropped sentence takes the whitespace gap preceding it with
        it, so two adjacent kept sentences keep exactly the gap bytes
        that separated them in the original. The rebuilt text never
        starts with the separator of a removed leading sentence, and the
        trailing gap is emitted only when the final sentence survives.

        Args:
            text: Original document text.
            spans: Sentence [start, end) offsets.
            kept: Per-sentence keep flags.

        Returns:
            str: Rebuilt text. With no removals this is byte-identical
            to the original.
        """
        parts: list[str] = []
        prev_end = 0
        emitted = False
        for position, ((start, end), is_kept) in enumerate(
                zip(spans, kept, strict=True)):
            if not is_kept:
                prev_end = end
                continue
            gap = text[prev_end:start]
            if not emitted and position > 0:
                # First kept sentence after removed leading ones: do not
                # begin the rebuilt text with their separator.
                gap = ""
            parts.append(gap + text[start:end])
            emitted = True
            prev_end = end
        if kept[-1]:
            parts.append(text[spans[-1][1]:])
        return "".join(parts)

    def _stamp(self, doc: Document, removals: list[dict], mode: str) -> None:
        """Write the removal record into document metadata.

        The metadata mapping is copied before mutation so a mapping
        shared with other pipeline stages never observes surprising
        in-place edits. ``duplicate_sentences`` is capped at
        ``_MAX_REMOVAL_ENTRIES`` entries (document order preserved);
        ``duplicate_count`` always carries the uncapped total.

        Args:
            doc: Document to stamp.
            removals: Full removal record, in sentence order.
            mode: Active deduplication mode, 'exact' or 'near'.
        """
        meta = dict(doc.metadata or {})
        meta["duplicate_sentences"] = removals[:_MAX_REMOVAL_ENTRIES]
        meta["duplicate_count"] = len(removals)
        meta["duplicate_mode"] = mode
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'DuplicateSentenceFilter':
        """Initialize and validate the filter from component configuration.

        Validation happens eagerly at load time: a misconfigured filter
        that silently kept every duplicate would be far harder to notice
        in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            DuplicateSentenceFilter: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "mode") and \
                doc_processor_configer.mode is not None:
            self.mode = doc_processor_configer.mode
            if self.mode not in ("exact", "near"):
                raise ValueError(
                    "mode must be 'exact' or 'near', got "
                    f"'{self.mode}'")

        if hasattr(doc_processor_configer, "jaccard_threshold") and \
                doc_processor_configer.jaccard_threshold is not None:
            threshold = doc_processor_configer.jaccard_threshold
            if isinstance(threshold, bool) or \
                    not isinstance(threshold, (int, float)):
                raise ValueError("jaccard_threshold must be a number")
            self.jaccard_threshold = float(threshold)
            if not 0.0 < self.jaccard_threshold <= 1.0:
                raise ValueError(
                    "jaccard_threshold must be in (0, 1], got "
                    f"{self.jaccard_threshold}")

        if hasattr(doc_processor_configer, "keep_last") and \
                doc_processor_configer.keep_last is not None:
            self.keep_last = bool(doc_processor_configer.keep_last)

        return self

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: social_tag_extractor.py

import re
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Social markers are recognized in a single scan of one alternation, so hits
# come out in document order and their spans never overlap. Each branch has
# a left guard (the marker must not be glued to a preceding ASCII word
# character) and a right guard (no mid-word truncation of overlong runs).
#
# hashtag: '#' followed first by a letter / underscore / CJK character and
#   then by word characters. Digits are allowed only after the first
#   character, which rejects pure-digit markers such as issue references
#   ('#123') while accepting '#WorldCup2026', camelCase tags and CJK tags
#   ('#人工智能'). CJK text may directly precede '#' because Chinese prose
#   has no spaces; ASCII-word prefixes ('C#', 'foo#bar') do not match.
# mention: '@' starting a handle of 2-30 [A-Za-z0-9_] characters. An '@'
#   glued to a preceding word is an e-mail separator ('user@example.com'),
#   not a mention; handles longer than 30 characters are ignored rather
#   than truncated mid-word.
# cashtag: '$' followed by 1-10 uppercase ASCII letters, per ticker
#   convention. Prices ('$5.50') are rejected because a digit can never
#   follow '$', and lowercase spellings ('$aapl') do not match; all-caps
#   runs longer than 10 characters and underscored identifiers
#   ('$PRICE_HIGH') are ignored rather than cut into a fake ticker, since
#   tickers never contain underscores.
_TAG_PATTERN = re.compile(
    r'(?P<hashtag>(?<![A-Za-z0-9_#])#[^\W\d]\w*)'
    r'|(?P<mention>(?<![A-Za-z0-9_@])@[A-Za-z0-9_]{2,30}(?![A-Za-z0-9_]))'
    r'|(?P<cashtag>(?<![A-Za-z0-9_$])\$[A-Z]{1,10}(?![A-Za-z0-9_]))'
)

# Kinds in reporting order; matches the named groups of _TAG_PATTERN.
_KINDS = ("hashtag", "mention", "cashtag")


class SocialTagExtractor(DocProcessor):
    """Extract social-media markers into document metadata.

    Social-listening knowledge bases ingest posts whose most valuable
    structure lives in platform markers: ``#hashtags`` carry campaign and
    topic signals, ``@mentions`` identify conversations between accounts,
    and ``$cashtags`` name the tickers a post talks about. Left as plain
    text, those markers are invisible to retrieval filters and analytics;
    recorded as metadata they become first-class filters ("posts mentioning
    ``#人工智能``", "posts about ``$AAPL``"). This processor scans each
    document once and stamps every recognized marker into its metadata,
    addressing the knowledge-extraction direction of issue #258.

    Recognition is pure-``re``, deterministic and offline — one compiled
    alternation scanned left to right, no model, no network, no extra
    dependency. It is complementary to ``JiebaKeywordExtractor``: that
    component ranks a text's top terms statistically, while this one
    recognizes marker-prefixed tags with exact character spans, per-kind
    counts and frequency rankings.

    Three marker kinds are recognized:

    - ``#hashtag`` — ``#`` followed first by a letter, underscore or CJK
      character, then by word characters (digits only after the first
      character). Accepts camelCase (``#MachineLearning``), embedded digits
      (``#WorldCup2026``) and CJK (``#人工智能``); rejects pure-digit
      markers (``#123``), markers glued to a preceding ASCII word (``C#``)
      and doubled markers (``##tag``).
    - ``@mention`` — a leading ``@`` (not an e-mail separator) starting a
      handle of 2-30 ``[A-Za-z0-9_]`` characters; longer runs are ignored
      rather than truncated mid-word.
    - ``$cashtag`` — ``$`` followed by 1-10 uppercase ASCII letters, so
      prices (``$5.50``) and lowercase spellings (``$aapl``) never match,
      and all-caps runs longer than 10 characters or underscored
      identifiers (``$PRICE_HIGH``) do not yield fake tickers.

    Trailing punctuation sits outside the word span by construction
    (``#AI,`` records ``#AI``; ``#人工智能。`` records ``#人工智能``).

    Every hit is recorded as ``{"kind", "text", "span"}`` — ``text`` keeps
    its marker and ``span`` is the exact ``(start, end)`` character range —
    in document order. Bookkeeping lands in three metadata entries, each
    written through a copied mapping so shared metadata dicts never see
    in-place edits, while text / id / other fields are never modified:

    - ``social_tags``: the hit list, capped at ``max_tags`` entries;
    - ``tag_counts``: ``{"hashtag": n, "mention": n, "cashtag": n}``
      covering every hit found, even beyond the cap;
    - ``top_hashtags``: the ``top_n`` most frequent hashtags as
      ``{"text", "count"}`` entries, ties broken alphabetically. Counting
      is over exact tag text (``#AI`` and ``#ai`` are distinct), so
      callers keep full control over case normalization.

    Documents containing no marker pass through completely untouched (no
    metadata entry is added), and the output list is the input list — this
    is an enrichment processor, not a filter.

    Attributes:
        max_tags: Maximum number of hits kept in the ``social_tags``
            metadata entry; must be >= 1. Counts and rankings always cover
            every hit, even past the cap.
        top_n: Number of most frequent hashtags written to
            ``top_hashtags``; must be >= 0, where 0 disables the entry.
        tags_key: Metadata key the capped hit list is written to; an empty
            value disables stamping.
        counts_key: Metadata key the per-kind totals are written to; an
            empty value disables stamping.
        top_hashtags_key: Metadata key the hashtag ranking is written to;
            an empty value disables stamping.
    """

    max_tags: int = 200
    top_n: int = 10
    tags_key: str = "social_tags"
    counts_key: str = "tag_counts"
    top_hashtags_key: str = "top_hashtags"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp social-media markers of every document into its metadata.

        Args:
            origin_docs: Documents to enrich, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents in the same order. Each
            document containing at least one marker carries the
            ``social_tags`` / ``tag_counts`` / ``top_hashtags`` metadata
            entries; documents without markers are returned untouched.
        """
        for doc in origin_docs or []:
            hits = self._extract(doc.text or "")
            if not hits:
                continue

            counts = dict.fromkeys(_KINDS, 0)
            hashtag_freq = {}
            for hit in hits:
                counts[hit["kind"]] += 1
                if hit["kind"] == "hashtag":
                    hashtag_freq[hit["text"]] = \
                        hashtag_freq.get(hit["text"], 0) + 1

            meta = dict(doc.metadata or {})
            if self.tags_key:
                meta[self.tags_key] = hits[:self.max_tags]
            if self.counts_key:
                meta[self.counts_key] = counts
            if self.top_hashtags_key and self.top_n > 0:
                ranked = sorted(hashtag_freq.items(),
                                key=lambda item: (-item[1], item[0]))
                meta[self.top_hashtags_key] = [
                    {"text": text, "count": count}
                    for text, count in ranked[:self.top_n]
                ]
            doc.metadata = meta
        return origin_docs

    # ------------------------------------------------------------------ #
    # Extraction helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract(text: str) -> List[dict]:
        """Find every social-media marker in one deterministic scan.

        Args:
            text: Document text (empty or None yields no hits).

        Returns:
            List[dict]: Hits in document order, each
            ``{"kind": hashtag|mention|cashtag, "text": <with marker>,
            "span": (start, end)}``.
        """
        return [
            {"kind": match.lastgroup, "text": match.group(),
             "span": match.span()}
            for match in _TAG_PATTERN.finditer(text or "")
        ]

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'SocialTagExtractor':
        """Initialize and validate the extractor from component config.

        Validation happens eagerly at load time: a silently ignored
        typo in the cap or a non-integer key would corrupt the metadata
        contract for every downstream consumer, which is far easier to
        catch at startup.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            SocialTagExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_tags") and \
                doc_processor_configer.max_tags is not None:
            value = doc_processor_configer.max_tags
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("max_tags must be an integer")
            self.max_tags = value
            if self.max_tags < 1:
                raise ValueError("max_tags must be >= 1")

        if hasattr(doc_processor_configer, "top_n") and \
                doc_processor_configer.top_n is not None:
            value = doc_processor_configer.top_n
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("top_n must be an integer")
            self.top_n = value
            if self.top_n < 0:
                raise ValueError("top_n must be >= 0")

        for attr in ("tags_key", "counts_key", "top_hashtags_key"):
            value = getattr(doc_processor_configer, attr, None)
            if value is not None:
                if not isinstance(value, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, value)

        return self

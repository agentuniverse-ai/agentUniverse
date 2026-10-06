# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/06
# @FileName: source_credibility_scorer.py

from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# ---------------------------------------------------------------------------
# Built-in credibility tables.
#
# The scores are deliberately coarse priors, not verdicts about individual
# sites: institutional TLDs lean authoritative (.gov/.edu), community
# encyclopedias are broadly reliable but self-inconsistent, major news and
# reference outlets sit in the middle, and unreviewed personal pages sit at
# the bottom. Users are expected to refine them through `credibility_map`.
# ---------------------------------------------------------------------------

# Suffix patterns matched against the end of the registered domain, e.g.
# ".gov" matches "cdc.gov" and "nih.gov"; ".edu.cn" matches "tsinghua.edu.cn".
DEFAULT_DOMAIN_SUFFIX_SCORES: Dict[str, float] = {
    ".gov": 0.95,
    ".gov.cn": 0.95,
    ".gov.uk": 0.95,
    ".edu": 0.9,
    ".edu.cn": 0.9,
    ".edu.au": 0.9,
    ".ac.uk": 0.9,
    ".ac.jp": 0.9,
    ".org": 0.75,
    ".int": 0.85,
    ".mil": 0.95,
}

# Exact registered domains (the last two labels, e.g. "wikipedia.org").
DEFAULT_EXACT_DOMAIN_SCORES: Dict[str, float] = {
    # Community encyclopedias / dictionaries
    "wikipedia.org": 0.7,
    "wikimedia.org": 0.7,
    "britannica.com": 0.8,
    "merriam-webster.com": 0.8,
    "dictionary.cambridge.org": 0.8,
    "oxfordreference.com": 0.85,
    # Long-standing news / wire outlets
    "reuters.com": 0.85,
    "apnews.com": 0.85,
    "bbc.com": 0.8,
    "bbc.co.uk": 0.8,
    "nytimes.com": 0.75,
    "theguardian.com": 0.75,
    "economist.com": 0.8,
    "ft.com": 0.8,
    "bloomberg.com": 0.8,
    "wsj.com": 0.75,
    "xinhuanet.com": 0.75,
    "people.com.cn": 0.7,
    # Technical / standards references
    "python.org": 0.9,
    "docs.python.org": 0.9,
    "developer.mozilla.org": 0.9,
    "w3.org": 0.9,
    "ietf.org": 0.9,
    "arxiv.org": 0.75,
    "nih.gov": 0.95,
    "who.int": 0.95,
    "nature.com": 0.85,
    "science.org": 0.85,
    "springer.com": 0.8,
    "sciencedirect.com": 0.8,
    "ieee.org": 0.85,
    "acm.org": 0.85,
    # Q&A / forum / user-generated content
    "stackoverflow.com": 0.6,
    "stackexchange.com": 0.6,
    "github.com": 0.6,
    "reddit.com": 0.4,
    "quora.com": 0.4,
    "zhihu.com": 0.4,
    "csdn.net": 0.4,
    "medium.com": 0.4,
    "blogspot.com": 0.35,
    "wordpress.com": 0.35,
    "substack.com": 0.4,
    "weibo.com": 0.35,
    "twitter.com": 0.35,
    "x.com": 0.35,
    # Aggregators with mixed provenance
    "baidu.com": 0.5,
    "bing.com": 0.5,
    "cnnic.cn": 0.7,
}

# Non-domain source identifiers matched exactly (case-insensitive), used when
# pipelines label sources by name rather than by URL.
DEFAULT_SOURCE_NAME_SCORES: Dict[str, float] = {
    "official": 0.9,
    "government": 0.9,
    "internal": 0.85,
    "research": 0.8,
    "news": 0.7,
    "media": 0.7,
    "wiki": 0.7,
    "blog": 0.4,
    "forum": 0.4,
    "social_media": 0.35,
    "rumor": 0.1,
    "unverified": 0.3,
    "unknown": 0.5,
}


class SourceCredibilityScorer(DocProcessor):
    """Score and filter recalled documents by the credibility of their source.

    Recall quality is not only about topical relevance: documents scraped from
    personal blogs, social media or content farms carry a higher risk of being
    wrong, and in regulated scenarios (medical, financial, legal) mixing them
    with institutional sources without any signal is a liability. This
    post-processor attaches a credibility score in [0, 1] to every recalled
    document, optionally dropping documents whose source is not trusted
    enough, so that later rerankers / generation stages can account for *how
    trustworthy* a piece of evidence is, not just how on-topic it is.

    The source of a document is read from ``metadata[source_key]`` (e.g. a URL
    like ``https://www.cdc.gov/...``, a bare domain ``cdc.gov``, or a source
    label like ``official``). Scoring proceeds in priority order:

    1. exact match in the user's ``credibility_map`` (URLs and domains are
       normalized first; entries may also be wildcard patterns such as
       ``*.gov`` or plain source labels);
    2. exact match in the built-in domain / source-name tables;
    3. longest built-in domain-suffix match (``.edu.cn`` beats ``.cn`` if both
       were configured);
    4. ``default_score`` for everything unrecognized.

    Wildcard entries (``*.gov``, ``*.edu.*``) are supported in both the custom
    map and — via the suffix table — effectively in the built-ins. Matching is
    case-insensitive and scheme/path-insensitive throughout.

    Attributes:
        source_key: Metadata field holding the document's source (URL, domain
            or source label).
        credibility_map: Custom ``{pattern: score}`` overrides checked before
            the built-in tables. Patterns may be exact domains, URLs,
            wildcard domains (``*.gov``) or source labels.
        min_score: Documents scoring below this threshold are dropped. Set to
            ``0`` (default) to keep everything and only attach scores.
        score_key: Metadata key the credibility score is written to; an empty
            value disables score stamping.
        default_score: Score assigned to sources not found in any table.
        keep_no_source: When true, documents with no source metadata are kept
            unstamped; when false they are dropped.
    """

    source_key: str = "source"
    credibility_map: Optional[Dict[str, float]] = None
    min_score: float = 0.0
    score_key: str = "credibility_score"
    default_score: float = 0.5
    keep_no_source: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Attach credibility scores and drop untrusted documents.

        Args:
            origin_docs: Recalled documents to score.
            query: Query object (unused; credibility is query-independent).

        Returns:
            List[Document]: Documents meeting the credibility threshold, in
            their original order, each stamped with its score.
        """
        if not origin_docs:
            return []

        kept: List[Document] = []
        for doc in origin_docs:
            source = self._extract_source(doc)
            if source is None:
                if self.keep_no_source:
                    kept.append(doc)
                continue

            score, matched = self._score_source(source)
            if score < self.min_score:
                continue
            self._stamp_score(doc, score, matched)
            kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Source extraction
    # ------------------------------------------------------------------ #

    def _extract_source(self, doc: Document) -> Optional[str]:
        """Read and normalize the source identifier from document metadata.

        URLs are reduced to a lowercase bare domain (scheme, userinfo,
        port, path, query and fragment stripped) so that
        ``https://CDC.gov:443/x?y=1`` and ``cdc.gov`` compare equal. Values
        that are not strings (or are empty) are treated as absent.

        Args:
            doc: Document whose metadata is inspected.

        Returns:
            Optional[str]: Normalized source identifier, or None if absent.
        """
        if not doc.metadata:
            return None
        value = doc.metadata.get(self.source_key)
        if not isinstance(value, str):
            return None
        text = value.strip().lower()
        if not text:
            return None
        if "://" in text:
            # Strip everything around the authority component of a URL.
            rest = text.split("://", 1)[1]
            host = rest.split("/", 1)[0]
            host = host.split("?", 1)[0].split("#", 1)[0]
            # Drop userinfo and port but keep IPv6 brackets usable.
            if "@" in host:
                host = host.rsplit("@", 1)[1]
            host = host.strip("[]")
            host = host.split(":", 1)[0]
            text = host
        return text

    # ------------------------------------------------------------------ #
    # Scoring
    # ------------------------------------------------------------------ #

    def _score_source(self, source: str) -> Tuple[float, Optional[str]]:
        """Resolve one source identifier to a credibility score.

        Lookup order (first hit wins):

        1. user ``credibility_map`` — exact key, then wildcard patterns
           sorted longest-first so ``*.edu.cn`` outranks ``*.cn``;
        2. built-in exact domain table (registered domain of the source);
        3. built-in source-name table (non-domain labels such as ``news``);
        4. built-in domain-suffix table, longest suffix first;
        5. ``default_score``.

        Args:
            source: Normalized source identifier (bare domain or label).

        Returns:
            Tuple[float, Optional[str]]: The score and the matched pattern
            (None when the default was used).
        """
        custom = self.credibility_map or {}

        # 1a. Exact custom entry — on the full source, then on its
        #     registered domain, so an override for "wikipedia.org" also
        #     governs "en.wikipedia.org".
        if source in custom:
            return float(custom[source]), source
        registered = _registered_domain(source)
        if registered is not None and registered in custom:
            return float(custom[registered]), registered

        # 1b. Custom wildcards, longest pattern first for predictable overlap.
        for pattern in sorted(
                (p for p in custom if "*" in p),
                key=len, reverse=True):
            if _wildcard_domain_match(pattern, source):
                return float(custom[pattern]), pattern

        # 2. Built-in exact-domain lookup, on the full domain first then on
        #    its last two labels, so multi-label entries such as
        #    "docs.python.org" are reachable.
        if source in DEFAULT_EXACT_DOMAIN_SCORES:
            return DEFAULT_EXACT_DOMAIN_SCORES[source], source
        if registered is not None and registered in DEFAULT_EXACT_DOMAIN_SCORES:
            return DEFAULT_EXACT_DOMAIN_SCORES[registered], registered

        # 3. Built-in source-name lookup (labels, not domains).
        if source in DEFAULT_SOURCE_NAME_SCORES:
            return DEFAULT_SOURCE_NAME_SCORES[source], source

        # 4. Built-in domain-suffix lookup, longest suffix first. This pass
        #    runs against the *full* domain so multi-label suffixes such as
        #    ".edu.cn" still match "tsinghua.edu.cn", whose last-two-label
        #    reduction is the suffix itself.
        suffix_hits = [s for s in DEFAULT_DOMAIN_SUFFIX_SCORES
                       if source.endswith(s)]
        if suffix_hits:
            suffix = max(suffix_hits, key=len)
            return DEFAULT_DOMAIN_SUFFIX_SCORES[suffix], suffix

        # 5. Unrecognized source.
        return float(self.default_score), None

    def _stamp_score(self, doc: Document, score: float,
                     matched: Optional[str]) -> None:
        """Write the credibility score (and matched rule) into metadata.

        The metadata mapping is copied before mutation so documents shared
        with other pipeline stages never observe surprising in-place edits.

        Args:
            doc: Document to stamp.
            score: Resolved credibility score.
            matched: Pattern that produced the score, if any.
        """
        if not self.score_key:
            return
        meta = dict(doc.metadata or {})
        meta[self.score_key] = round(float(score), 4)
        if matched is not None:
            meta[f"{self.score_key}_matched"] = matched
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'SourceCredibilityScorer':
        """Initialize and validate the scorer from component configuration.

        Validation happens eagerly: a credibility filter whose map contained
        out-of-range scores would otherwise silently re-rank recall results.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            SourceCredibilityScorer: The initialized instance.

        Raises:
            ValueError: On invalid parameter values or map entries.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "source_key"):
            self.source_key = doc_processor_configer.source_key
            if not self.source_key:
                raise ValueError("source_key must be a non-empty string")

        if hasattr(doc_processor_configer, "credibility_map") and \
                doc_processor_configer.credibility_map is not None:
            raw_map = doc_processor_configer.credibility_map
            if not isinstance(raw_map, dict):
                raise ValueError("credibility_map must be a mapping of "
                                 "{pattern: score}")
            validated: Dict[str, float] = {}
            for pattern, score in raw_map.items():
                if not isinstance(pattern, str) or not pattern.strip():
                    raise ValueError(
                        f"credibility_map keys must be non-empty strings, "
                        f"got: {pattern!r}")
                if isinstance(score, bool) or not isinstance(score, (int, float)):
                    raise ValueError(
                        f"credibility_map['{pattern}'] must be numeric, "
                        f"got: {score!r}")
                if not 0 <= float(score) <= 1:
                    raise ValueError(
                        f"credibility_map['{pattern}'] must be in [0, 1], "
                        f"got: {score}")
                validated[pattern.strip().lower()] = float(score)
            self.credibility_map = validated

        if hasattr(doc_processor_configer, "min_score"):
            self.min_score = doc_processor_configer.min_score
            if not 0 <= self.min_score <= 1:
                raise ValueError("min_score must be in [0, 1]")

        if hasattr(doc_processor_configer, "score_key"):
            self.score_key = doc_processor_configer.score_key

        if hasattr(doc_processor_configer, "default_score"):
            self.default_score = doc_processor_configer.default_score
            if not 0 <= self.default_score <= 1:
                raise ValueError("default_score must be in [0, 1]")

        if hasattr(doc_processor_configer, "keep_no_source"):
            self.keep_no_source = doc_processor_configer.keep_no_source

        return self


# ----------------------------------------------------------------------- #
# Module-level helpers (pure functions, kept out of the class for testability)
# ----------------------------------------------------------------------- #

def _wildcard_domain_match(pattern: str, domain: str) -> bool:
    """Match a domain against a wildcard pattern such as ``*.gov``.

    A pattern with a single leading ``*`` matches any number of leading
    labels: ``*.gov`` matches ``cdc.gov`` and ``a.b.gov`` but not ``gov``
    itself. Patterns without ``*`` are compared for equality after
    normalization.

    Args:
        pattern: Wildcard domain pattern (lowercase, may contain one ``*``).
        domain: Normalized bare domain to test.

    Returns:
        bool: Whether the domain matches the pattern.
    """
    if "*" not in pattern:
        return pattern == domain
    head, _, tail = pattern.partition("*")
    if "*" in tail:
        # Multiple wildcards: fall back to per-label globbing via fnmatch
        # semantics implemented on labels to stay dependency-light.
        from fnmatch import fnmatchcase
        return fnmatchcase(domain, pattern)
    return domain.endswith(tail) and domain != tail and (
        not head or domain.startswith(head))


def _registered_domain(source: str) -> Optional[str]:
    """Return the last two labels of a domain, for exact-table lookup.

    ``a.b.cdc.gov`` -> ``cdc.gov``. This intentionally ignores public-suffix
    subtleties (``.co.uk``): the suffix table already carries explicit
    multi-label suffixes such as ``.edu.cn``, so precision loss here is
    recovered by the suffix pass. Non-domain labels (``official``, ``news``)
    yield None-ish results that simply miss the domain tables.

    Args:
        source: Normalized bare domain or source label.

    Returns:
        Optional[str]: The two-label domain, or None when there are fewer
        than two labels.
    """
    labels = [label for label in source.split(".") if label]
    if len(labels) < 2:
        return None
    return ".".join(labels[-2:])


def _describe_tables() -> Dict[str, Any]:
    """Return the built-in scoring tables (exposed for tests and debugging).

    Returns:
        Dict[str, Any]: Copy of the three built-in tables.
    """
    return {
        "domain_suffix_scores": dict(DEFAULT_DOMAIN_SUFFIX_SCORES),
        "exact_domain_scores": dict(DEFAULT_EXACT_DOMAIN_SCORES),
        "source_name_scores": dict(DEFAULT_SOURCE_NAME_SCORES),
    }

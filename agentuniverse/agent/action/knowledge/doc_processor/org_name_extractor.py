# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: org_name_extractor.py

import re
from typing import List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# English organizational suffixes. Each is matched exactly as spelled (the
# canonical legal-form capitalization, so a lowercase mid-sentence "inc" or
# "corp" is not a trigger) or in its fully upper-cased variant for headline
# prose ("BAYER AG"). The trailing suffix is kept INSIDE the extracted name.
EN_SUFFIXES = (
    "Inc", "Inc.", "Corp", "Corporation", "Company", "Co.", "Ltd",
    "LLC", "LLP", "PLC", "GmbH", "AG", "SA", "NV", "Group", "Holdings",
    "Partners", "Labs", "Technologies", "Industries",
)

# Chinese organizational suffixes. Longer entries are tried first so that
# e.g. 股份有限公司 wins over the 有限公司 it contains, and 集团 inside a
# name like 华为集团有限公司 stays part of the name rather than the suffix.
ZH_SUFFIXES = (
    "股份有限公司", "有限公司", "研究院", "研究所", "集团", "公司",
    "银行", "证券", "基金", "大学", "学院",
)

# Characters that commonly continue a Chinese word PAST a suffix without
# being part of any organization name: 大学生 (university student),
# 证券化 (securitization), 基金会 (foundation), 银行卡 (bank card),
# 银行业 (banking industry), 大学城 (college town), 银行家 (banker).
# A suffix followed by one of these is rejected; sentence particles such
# as 的 are deliberately absent so 公司的 keeps matching.
ZH_COMPOUND_TAILS = "生化会卡业城家"

# One capitalized Latin name word: an optional leading digit run ("3M"),
# an uppercase letter, then letters/digits/apostrophes/hyphens, optionally
# chained with '&' inside the token ("AT&T", "Johnson&Johnson").
_EN_WORD = r"\d*[A-Z][A-Za-z0-9'’\-]*(?:&[A-Za-z0-9'’\-]+)*"

# A name is a sequence of such words joined by whitespace, possibly over
# the connectors '&', 'of' and 'the' ("Bank of America", "Johnson &
# Johnson"), and may end with a dangling connector ("McKinsey &" +
# suffix "Company"). The sequence must START with a capitalized word.
_EN_NAME = (_EN_WORD
            + r"(?:\s+(?:&|of|the)\s+" + _EN_WORD
            + r"|\s+" + _EN_WORD + r")*"
            + r"(?:\s+(?:&|of|the))?")

# Leading articles trimmed from an English name ("The ACME Widget &
# Tool Corporation" -> "ACME Widget & Tool Corporation"). The all-caps
# form covers headline prose, where the suffix is upper-cased too.
_LEADING_ARTICLE = re.compile(r"^(?:The|THE|A)\s+")

_CJK_CLASS = r"\u3400-\u4dbf\u4e00-\u9fff"

# URLs and emails are blanked out (with a same-length placeholder, so
# character offsets are preserved) before matching, because "Bayer AG"
# inside "https://example.com/files/Bayer AG report.pdf" or a path
# segment like /wiki/大众集团 is part of an address, not a mention. The
# character class stops the URL at whitespace, quotes, brackets and
# CJK/full-width punctuation, so adjacent prose survives.
_URL_MASK = re.compile(
    r"https?://[^\s<>\"'{}\[\]\u3000-\u303f\uff00-\uffef]+"
    r"|www\.[^\s<>\"'{}\[\]\u3000-\u303f\uff00-\uffef]+")
_EMAIL_MASK = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")

# Placeholder replacing masked characters: same length as the blanked
# region (spans stay valid) but neither whitespace (so it cannot glue a
# capitalized word to a suffix across a masked URL) nor a character any
# name pattern accepts.
_MASK_CHAR = "\x00"


def _suffix_alternation(suffixes) -> str:
    """Build a regex alternation of suffixes, longest first.

    Longest-first ordering makes the engine prefer the longest legal-form
    suffix at a given position; each suffix also admits its fully
    upper-cased variant for all-caps prose.

    Args:
        suffixes: Iterable of suffix strings.

    Returns:
        str: An alternation usable inside a regex group.
    """
    parts = []
    for suffix in sorted(set(suffixes), key=len, reverse=True):
        parts.append(re.escape(suffix))
        if suffix.upper() != suffix:
            parts.append(re.escape(suffix.upper()))
    return "|".join(parts)


# Full English pattern: a capitalized name sequence, whitespace, a
# suffix, then a boundary that is not a letter (so "Corp" inside
# "Corporation" or "Company" inside "Companies" never fires) and a left
# boundary that is not alphanumeric (so mid-word capitals are ignored).
EN_ORG_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])" + _EN_NAME
    + r"\s+(?P<suffix>" + _suffix_alternation(EN_SUFFIXES) + r")(?![A-Za-z])")

# Full Chinese pattern: a CJK run (optionally joined by the interpuncts
# U+00B7 / U+2022 used in transliterated names such as 路威·酩轩, with
# optional parenthesized region segments like （中国） between runs),
# followed by a suffix and a guard rejecting common word-continuation
# characters (大学生 / 证券化 / 基金会 / 银行卡 are not organizations).
_ZH_SEG = "[" + _CJK_CLASS + r"]+"
_ZH_REGION = r"[（(][^（）()]{1,12}[）)]"
ZH_ORG_PATTERN = re.compile(
    _ZH_SEG + r"(?:[\u00b7\u2022]" + _ZH_SEG + r"|" + _ZH_REGION + _ZH_SEG + r"?)*"
    + r"(?P<suffix>" + _suffix_alternation(ZH_SUFFIXES) + r")"
    + r"(?![" + ZH_COMPOUND_TAILS + r"])")


class OrgNameExtractor(DocProcessor):
    """Extract organization names into document metadata.

    Supply-chain and business knowledge graphs are built out of
    organization entities: which suppliers a contract binds, which banks
    financed a deal, which universities co-authored a paper. Those
    entities usually live inside prose as proper names terminated by a
    legal-form or institutional suffix — "Siemens AG", "华为技术有限公司"
    — and are invisible to retrieval until somebody lifts them out. This
    processor scans every document with suffix-anchored regular
    expressions and stamps the organization mentions it finds into
    document metadata, leaving the text itself untouched.

    Extraction is context-free and suffix-driven, deterministic and
    offline:

    1. URLs and emails are blanked out of a working copy (replaced by a
       same-length placeholder so spans into the original text stay
       valid) — "Bayer AG" inside a pasted link is an address, not a
       mention;
    2. candidate names are located by suffix anchors. English suffixes
       (Inc, Corp, Corporation, Company, Co., Ltd, LLC, LLP, PLC, GmbH,
       AG, SA, NV, Group, Holdings, Partners, Labs, Technologies,
       Industries, each capitalization-sensitive) and Chinese suffixes
       (股份有限公司, 有限公司, 集团, 公司, 银行, 证券, 基金, 研究院,
       研究所, 大学, 学院) are matched longest-first;
    3. each match is extended LEFT over a name pattern. English names
       are capitalized word sequences, possibly joined by '&', 'of' or
       'the' and hyphens ("Bank of America Corp", "Johnson & Johnson
       Inc.", "AT&T Inc"); Chinese names are contiguous CJK runs joined
       by the interpuncts used in transliteration and interleaved with
       parenthesized region segments ("甲骨文（中国）软件系统有限公司");
    4. leading articles are trimmed ("The ACME Widget & Tool
       Corporation" is stamped as "ACME Widget & Tool Corporation"),
       and the suffix is kept INSIDE the stamped name.

    Guards keep precision high without any context model: a suffix needs
    at least one leading name character (a bare "Inc." or "公司" never
    matches), a name consisting of nothing but the article is rejected
    ("The Corporation announced..." yields nothing), English suffixes
    must be capitalized as written (a lowercase mid-sentence "inc"
    never fires, matching only "Inc" or "INC"), suffixes must end at a
    word boundary ("Incorporated" / "Companies" do not contain triggers)
    and Chinese suffixes followed by a word-continuation character are
    rejected (一名大学生, 资产证券化, 银行卡 are not organizations).

    Results land in metadata: ``metadata[organizations_key]`` holds a
    list of ``{"name": str, "span": (start, end)}`` entries in order of
    first occurrence — ``text[span[0]:span[1]] == name`` always holds
    against the original text — deduplicated case-insensitively (the
    first spelling wins) and capped at ``max_orgs``;
    ``metadata[count_key]`` holds the number of distinct organizations
    found before capping, so a value above ``max_orgs`` signals
    truncation. Empty lists are stamped on purpose: a caller can
    distinguish "extraction ran and found nothing" from "extraction
    never ran". Metadata mappings are copied before mutation, text / id
    / other metadata fields are never modified, and every document
    survives processing — extraction adds structure, it does not filter.

    Being context-free is what makes the component cheap and
    deterministic, and it is also the boundary of what it can see.
    Known trade-offs, all deliberate: an organization without any listed
    suffix ("Apple", "Google", "摩根大通") is not extracted; in scripts
    without word separators the Chinese run extends to the previous
    non-CJK boundary, so a mention directly abutting other prose
    absorbs it ("清华大学与中国科学院物理研究所" is one long run, and
    "与中信证券" keeps its leading conjunction) — running the extractor
    after a splitter that inserts punctuation materially helps; and a
    sentence-initial capitalized common noun before a generic suffix
    ("Study Group") can match. This positions the component against its
    siblings: ``ContactEntityExtractor`` (#3441) lifts emails, URLs and
    phone numbers — contact points, never organization names — while
    ``SupplyChainEntityExtractor`` needs role context around each
    mention (a "supplier: X" line) and misses organizations stated in
    plain prose. This extractor needs neither contacts nor roles: any
    suffix-terminated mention in any document qualifies, which is
    exactly what graph construction over heterogeneous corpora needs.

    Attributes:
        max_orgs: Maximum number of organizations stamped into
            metadata; must be >= 1. The pre-cap distinct count is still
            reported in the count key.
        organizations_key: Metadata key the ``[{name, span}]`` list is
            written to; an empty value disables stamping.
        count_key: Metadata key the distinct-organization count is
            written to; an empty value disables stamping.
    """

    max_orgs: int = 50
    organizations_key: str = "organizations"
    count_key: str = "org_count"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp organization mentions into every document's metadata.

        Args:
            origin_docs: Documents to process, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents in the same order, each
            carrying the extracted organizations in its metadata.
        """
        for doc in origin_docs:
            organizations, distinct = self._extract(doc.text or "")
            metadata = dict(doc.metadata or {})
            if self.organizations_key:
                metadata[self.organizations_key] = organizations
            if self.count_key:
                metadata[self.count_key] = distinct
            doc.metadata = metadata
        return origin_docs

    # ------------------------------------------------------------------ #
    # Extraction helpers
    # ------------------------------------------------------------------ #

    def _extract(self, text: str) -> Tuple[List[dict], int]:
        """Extract capped organization entries plus the distinct count.

        Args:
            text: Document text (None treated as empty).

        Returns:
            Tuple[List[dict], int]: A pair of the ``[{"name", "span"}]``
            list — deduplicated case-insensitively, ordered by first
            span, capped at ``max_orgs`` — and the number of distinct
            organizations found before capping.
        """
        found = []
        for pattern in (EN_ORG_PATTERN, ZH_ORG_PATTERN):
            for match in pattern.finditer(self._mask(text or "")):
                entry = self._condition(match)
                if entry is not None:
                    found.append(entry)

        # Order by first span (English and Chinese patterns run
        # separately, so merge here), then keep the first spelling of
        # each case-insensitively distinct name.
        found.sort(key=lambda entry: entry["span"])
        organizations: List[dict] = []
        seen = set()
        for entry in found:
            key = entry["name"].casefold()
            if key in seen:
                continue
            seen.add(key)
            organizations.append(entry)
        return organizations[:self.max_orgs], len(organizations)

    @staticmethod
    def _mask(text: str) -> str:
        """Blank out URLs and emails with a same-length placeholder.

        Masked characters are replaced by NUL rather than a space: a
        space would let the English pattern bridge a capitalized word to
        a suffix across the blanked region ("Download <url> AG ..."),
        while NUL matches nothing and keeps every remaining offset
        identical to the original text.

        Args:
            text: Original document text.

        Returns:
            str: Text with URL/email regions neutralized.
        """
        blank = lambda m: _MASK_CHAR * (m.end() - m.start())
        text = _URL_MASK.sub(blank, text)
        return _EMAIL_MASK.sub(blank, text)

    @staticmethod
    def _condition(match: re.Match) -> "dict | None":
        """Normalize one raw pattern match into a stamped entry.

        The leading article ("The ACME ...") is trimmed when what
        remains still starts like a name; a head that consisted of
        nothing but the article ("The Corporation", "A Corp") is
        rejected outright; a trimmed head that would start with a
        connector ("A & B Corp" -> "& B Corp") falls back to the
        untrimmed spelling. Chinese matches pass through untouched —
        Chinese has no articles.

        Args:
            match: A successful EN or ZH pattern match.

        Returns:
            dict | None: ``{"name": str, "span": (start, end)}`` with
            ``text[span] == name`` on the original text, or None when
            the match is rejected by a guard.
        """
        name = match.group(0)
        start, end = match.span()
        suffix = match.group("suffix")

        if match.re is EN_ORG_PATTERN:
            trimmed = _LEADING_ARTICLE.sub("", name, count=1)
            if len(trimmed) != len(name):
                head = trimmed[:-len(suffix)] \
                    if len(trimmed) > len(suffix) else ""
                if not head.strip():
                    # "The Corporation" — the article was the only name.
                    return None
                if head[0].isalpha():
                    start += len(name) - len(trimmed)
                    name = trimmed
                # else "A & B Corp": keep the article, a connector must
                # not open the name.
        return {"name": name, "span": (start, end)}

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'OrgNameExtractor':
        """Initialize and validate the extractor from component config.

        Validation happens eagerly at load time: an extractor silently
        stamping a truncated or malformed organization list would be far
        harder to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            OrgNameExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_orgs") and \
                doc_processor_configer.max_orgs is not None:
            max_orgs = doc_processor_configer.max_orgs
            if isinstance(max_orgs, bool) or not isinstance(max_orgs, int):
                raise ValueError("max_orgs must be an integer")
            self.max_orgs = max_orgs
            if self.max_orgs < 1:
                raise ValueError("max_orgs must be >= 1")

        if hasattr(doc_processor_configer, "organizations_key") and \
                doc_processor_configer.organizations_key is not None:
            key = doc_processor_configer.organizations_key
            if not isinstance(key, str):
                raise ValueError("organizations_key must be a string")
            self.organizations_key = key

        if hasattr(doc_processor_configer, "count_key") and \
                doc_processor_configer.count_key is not None:
            key = doc_processor_configer.count_key
            if not isinstance(key, str):
                raise ValueError("count_key must be a string")
            self.count_key = key

        return self

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: bounded_query_paraphraser.py

"""Bounded query paraphraser: HyDE passages and multi-query variants, one component.

Supersedes the two competing paraphraser additions #3322 (HyDE) and #3325
(multi-query) in a single add/add-occupying implementation:

* strategy ``"hyde"`` -- answer-space: ``num_docs`` (1-5) hypothetical passages,
  one LLM call each so a single failing call cannot take down the others,
  joined by blank lines;
* strategy ``"multi"`` -- question-space: ONE LLM call returning one variant
  per line; numbering (``1.``/``1)``/``1、``/``1:``), bullets (``-``/``*``/``•``)
  and wrapping quotes are stripped, folded duplicates and lines equal to the
  original are dropped, and the result is capped at ``num_queries`` (1-10).

Both strategies honour the framework contract: the final items are appended to
``query_text_bundles`` (exact duplicates skipped), ``query_str`` is rewritten
(``append`` keeps the original query first, ``replace`` uses the generated text
only), the untouched original is recorded under ``ext_info[origin_query_key]``
(first expansion wins) and the final list under ``ext_info[documents_key]`` /
``ext_info[variants_key]``. Every item is truncated (``max_doc_chars`` /
``max_query_chars``) before it can reach an embedding.

Expansion is best effort by contract: an unset ``llm_model``, a failing call,
an empty query, or unusable output degrades to pass-through with a warning.
Configuration errors fail loudly: they raise ValueError quoting the offending
value, eagerly at component-load time and again on first use.

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003
"""

import logging
import re
from typing import List, Optional

from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import (
    QueryParaphraser,
)
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

_VALID_STRATEGIES = ("hyde", "multi")
_VALID_MODES = ("append", "replace")
_MIN_NUM_DOCS, _MAX_NUM_DOCS = 1, 5
_MIN_NUM_QUERIES, _MAX_NUM_QUERIES = 1, 10

_DEFAULT_SYSTEM_PROMPT = (
    "You are a retrieval assistant. You output only the requested search text, "
    "one item per requested item, with no preface and no explanations."
)
_HYDE_USER_TEMPLATE = (
    "Write one short, self-contained passage that would directly answer or "
    "address the following query. Write the passage in the same language as "
    "the query. Output only the passage itself: no preface, no explanation, "
    "no markdown.\n\nQuery: {query}"
)
_MULTI_USER_TEMPLATE = (
    "Generate {num} different search queries that express the same intent as "
    "the following query, using varied wording. Write them in the same "
    "language as the query. Output exactly one query per line, numbered from "
    "1, with no explanations and no empty lines.\n\nQuery: {query}"
)

# Leading list decoration emitted by LLMs: "1.", "1)", "1、", "1:", "1：", "-", "*", "•".
# The punctuation after the number is required, so ISO dates like 2026-01-01 survive.
_BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+\s*[.)、:：])\s*")
# Wrapping quotes, ASCII and CJK.
_WRAPPING_QUOTES = "\"'“”‘’「」『』《》"


class BoundedQueryParaphraser(QueryParaphraser):
    """One bounded, typed, deterministic paraphraser with both public strategies.

    Attributes:
        strategy: ``"hyde"`` (hypothetical passages) or ``"multi"`` (reformulated
            queries); anything else raises ValueError quoting the value.
        llm_model: Registered LLM component name; empty means best-effort
            pass-through (with a warning) so the shipped yaml stays loadable.
        mode: ``"append"`` rewrites ``query_str`` to the original followed by
            the expansion; ``"replace"`` uses the expansion only.
        num_docs: Passage count for the ``hyde`` strategy, in [1, 5].
        num_queries: Variant cap for the ``multi`` strategy, in [1, 10].
        max_doc_chars: Truncation bound per generated passage.
        max_query_chars: Truncation bound per parsed variant.
        prompt_template: Custom user-prompt template; must contain the literal
            ``{query}`` placeholder, may contain ``{num}`` (replaced first, so
            any other braces are safe). ``None`` selects the strategy default.
        origin_query_key: ``ext_info`` key under which the untouched original
            ``query_str`` is recorded (first expansion wins).
        documents_key: ``ext_info`` key under which the passage list (hyde) is
            recorded.
        variants_key: ``ext_info`` key under which the variant list (multi) is
            recorded.
    """

    strategy: str = "hyde"
    llm_model: str = ""
    mode: str = "append"
    num_docs: int = 1
    num_queries: int = 3
    max_doc_chars: int = 2000
    max_query_chars: int = 512
    prompt_template: Optional[str] = None
    origin_query_key: str = "paraphrase_origin_query_str"
    documents_key: str = "paraphrase_hyde_documents"
    variants_key: str = "paraphrase_multi_variants"

    def query_paraphrase(self, origin_query: Query) -> Query:
        """Rewrite the query (best effort); see the module docstring.

        Raises:
            ValueError: On invalid static configuration (unknown strategy or
                mode, out-of-range counts, non-positive char bounds, custom
                template without ``{query}``, empty ext_info keys).
        """
        self._validate_config()
        query_str = (origin_query.query_str or "").strip()
        if not query_str:
            return origin_query
        if not self.llm_model:
            logger.warning(
                "BoundedQueryParaphraser %r has no llm_model configured; the "
                "original query is used unchanged.", self.name)
            return origin_query
        try:
            items = self._generate(query_str)
        except Exception as exc:  # enhancement failures never break retrieval
            logger.warning("Query expansion failed (%s); the original query is "
                           "used unchanged.", exc)
            return origin_query
        if not items:
            logger.warning("LLM returned no usable expansion; the original "
                           "query is used unchanged.")
            return origin_query
        if origin_query.ext_info is None:
            origin_query.ext_info = {}
        origin_query.ext_info.setdefault(self.origin_query_key, origin_query.query_str)
        if self.strategy == "hyde":
            origin_query.ext_info[self.documents_key] = items
        else:
            origin_query.ext_info[self.variants_key] = items
        bundles = origin_query.query_text_bundles
        if bundles is None:
            bundles = []
            origin_query.query_text_bundles = bundles
        for item in items:
            if item not in bundles:
                bundles.append(item)
        joined = ("\n\n" if self.strategy == "hyde" else "\n").join(items)
        if self.mode == "replace":
            origin_query.query_str = joined
        else:
            origin_query.query_str = f"{query_str}\n{joined}"
        return origin_query

    def _generate(self, query_str: str) -> List[str]:
        if self.strategy == "hyde":
            template = (self.prompt_template if self.prompt_template is not None
                        else _HYDE_USER_TEMPLATE)
            prompt = template.replace("{num}", str(self.num_docs)).replace("{query}", query_str)
            messages = [{"role": "system", "content": _DEFAULT_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}]
            llm = self._get_llm()
            items: List[str] = []
            seen = set()
            for index in range(self.num_docs):
                # One call per passage: a failing call cannot take down the others.
                try:
                    output = llm.call(messages=messages, streaming=False)
                except Exception as exc:
                    logger.warning("HyDE passage %d failed (%s); continuing with "
                                   "the remaining calls.", index + 1, exc)
                    continue
                passage = _clean(getattr(output, "text", ""), self.max_doc_chars)
                folded = passage.casefold()
                if not passage or folded == _fold(query_str) or folded in seen:
                    continue
                seen.add(folded)
                items.append(passage)
            return items
        template = (self.prompt_template if self.prompt_template is not None
                    else _MULTI_USER_TEMPLATE)
        prompt = template.replace("{num}", str(self.num_queries)).replace("{query}", query_str)
        messages = [{"role": "system", "content": _DEFAULT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}]
        output = self._get_llm().call(messages=messages, streaming=False)
        raw = getattr(output, "text", "")
        items = []
        seen = set()
        original = _fold(query_str)
        for line in raw.splitlines():
            variant = _clean(line, self.max_query_chars)
            folded = variant.casefold()
            if not variant or folded == original or folded in seen:
                continue
            seen.add(folded)
            items.append(variant)
            if len(items) >= self.num_queries:
                break
        return items

    def _get_llm(self):
        # Imported lazily: the LLMManager patch seam in the tests (and the
        # manager's own import graph) requires it.
        from agentuniverse.llm.llm_manager import LLMManager

        component = LLMManager().get_instance_obj(self.llm_model)
        if component is None:
            raise ValueError(f"unknown llm_model {self.llm_model!r}: no registered "
                             "LLM component with that name")
        return component

    def _validate_config(self) -> None:
        if self.strategy not in _VALID_STRATEGIES:
            raise ValueError(f"unknown strategy {self.strategy!r}; expected one of "
                             f"{list(_VALID_STRATEGIES)}")
        if self.mode not in _VALID_MODES:
            raise ValueError(f"unknown mode {self.mode!r}; expected one of "
                             f"{list(_VALID_MODES)}")
        for attr, minimum, maximum in (
                ("num_docs", _MIN_NUM_DOCS, _MAX_NUM_DOCS),
                ("num_queries", _MIN_NUM_QUERIES, _MAX_NUM_QUERIES),
                ("max_doc_chars", 1, None),
                ("max_query_chars", 1, None),
        ):
            bound = getattr(self, attr)
            if not isinstance(bound, int) or isinstance(bound, bool):
                raise ValueError(f"{attr} must be an int, got {bound!r}")
            if bound < minimum or (maximum is not None and bound > maximum):
                range_note = (f"greater than or equal to {minimum!r}" if maximum is None
                              else f"in [{minimum!r}, {maximum!r}]")
                raise ValueError(f"{attr} must be {range_note}, got {bound!r}")
        if (self.prompt_template is not None
                and (not isinstance(self.prompt_template, str)
                     or "{query}" not in self.prompt_template)):
            raise ValueError(f"prompt_template must be a string containing the "
                             f"literal '{{query}}' placeholder, got "
                             f"{self.prompt_template!r}")
        for attr in ("origin_query_key", "documents_key", "variants_key"):
            if not getattr(self, attr):
                raise ValueError(f"{attr} must be a non-empty string, got "
                                 f"{getattr(self, attr)!r}")

    def _initialize_by_component_configer(
            self, query_paraphraser_config: ComponentConfiger) -> "BoundedQueryParaphraser":
        super()._initialize_by_component_configer(query_paraphraser_config)
        for attr in ("strategy", "llm_model", "mode", "num_docs", "num_queries",
                     "max_doc_chars", "max_query_chars", "prompt_template",
                     "origin_query_key", "documents_key", "variants_key"):
            if hasattr(query_paraphraser_config, attr):
                setattr(self, attr, getattr(query_paraphraser_config, attr))
        # Validate eagerly so a misconfiguration fails at component-load time
        # rather than on the first query.
        self._validate_config()
        return self


def _fold(text: str) -> str:
    return " ".join(text.split()).casefold()


def _clean(text: str, limit: int) -> str:
    stripped = _BULLET_RE.sub("", str(text).strip())
    stripped = stripped.strip(_WRAPPING_QUOTES)
    return " ".join(stripped.split())[:limit]

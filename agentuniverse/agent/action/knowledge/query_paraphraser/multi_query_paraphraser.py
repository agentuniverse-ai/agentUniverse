# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: multi_query_paraphraser.py

"""
Multi-query expansion paraphraser.

A single user question rarely covers the vocabulary of every relevant
document: the corpus may phrase the same intent as a synonym, a
reformulation, or the other side of the question ("how do I reset X" vs
"X reset procedure"). This paraphraser asks an LLM for several *query
reformulations* of the original question and retrieves with all of them,
widening recall without changing what the user asked about.

It is the question-side counterpart of ``HyDEQueryParaphraser`` (which
generates answer-shaped hypothetical passages): multi-query stays in
question space and is one cheap LLM call, while HyDE writes document-space
passages. The two compose naturally in a ``query_paraphrasers`` chain.

Integration follows the framework contract — the paraphraser receives and
returns the same :class:`Query` object:

* variants are appended to ``query_text_bundles`` ("multiple rewritten
  query text segments" in the Query contract);
* ``query_str`` is rewritten (``append`` mode keeps the original query and
  adds the variants; ``replace`` mode uses the variants only), so stores
  embedding ``query_str`` at query time benefit with no further wiring;
* the untouched original query and the final variant list are recorded
  under ``ext_info`` keys for later stages (fusion, rerankers, logging).

Generation is a single LLM call returning one variant per line; the parser
tolerates the usual decoration (``1.`` / ``1)`` / ``1、`` numbering, ``-``/``*``
bullets, wrapping quotes), drops empty lines, lines equal to the original
query, and duplicates, then caps the result at ``num_queries`` and
truncates each variant to ``max_query_chars``.

Expansion is best-effort by design: an empty query, an unset ``llm_model``,
a failing LLM call, or output without any usable variant degrades to
pass-through with a logged warning — retrieval must never break because an
*enhancement* failed. Configuration errors fail loudly at component-load
time instead, because they mean the component is not doing what the
operator believes.
"""

import logging
import re

from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import QueryParaphraser
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

_VALID_MODES = ("append", "replace")
_MIN_NUM_QUERIES = 1
_MAX_NUM_QUERIES = 10

_DEFAULT_SYSTEM_PROMPT = (
    "You are a retrieval assistant. You reformulate search queries so that "
    "dense retrieval recalls more relevant documents. You output only the "
    "reformulated queries, one per line."
)
_DEFAULT_USER_TEMPLATE = (
    "Generate {num} different search queries that express the same intent as "
    "the following query, using varied wording. Write them in the same "
    "language as the query. Output exactly one query per line, numbered from "
    "1, with no explanations and no empty lines.\n\nQuery: {query}"
)

# Leading list decoration emitted by LLMs: "1.", "1)", "1、", "-", "*", "•".
# The fullwidth CJK markers are intentional: they are exactly what Chinese
# model output contains, not confusable typos.
_LINE_PREFIX_RE = re.compile(r"^\s*(?:\d+\s*[.)、:：]|[-*•])\s*")  # noqa: RUF001
# Wrapping quotes around a whole variant; CJK curly quotes included on purpose.
_QUOTE_PAIRS = (('"', '"'), ("'", "'"), ("“", "”"), ("‘", "’"))  # noqa: RUF001


def _normalize_variant(line: str) -> str:
    """Strip list numbering, bullets and wrapping quotes from one output line."""
    text = _LINE_PREFIX_RE.sub("", line).strip()
    if len(text) >= 2:
        for open_quote, close_quote in _QUOTE_PAIRS:
            if text.startswith(open_quote) and text.endswith(close_quote):
                text = text[len(open_quote) : -len(close_quote)].strip()
                break
    return text


class MultiQueryParaphraser(QueryParaphraser):
    """Expand a retrieval query with LLM-generated question reformulations.

    Attributes:
        llm_model: Name of the registered LLM component used to generate the
            variants. When empty, the paraphraser passes queries through
            unchanged (with a warning) so the shipped yaml stays loadable
            without any model credentials.
        num_queries: Maximum number of variants to keep, in [1, 10]; the LLM
            is asked for exactly this many in one call.
        mode: ``"append"`` (default) rewrites ``query_str`` to the original
            query followed by the variants; ``"replace"`` uses the variants
            only.
        max_query_chars: Hard truncation bound applied to every variant.
        prompt_template: Custom user-prompt template; must contain the
            literal ``{query}`` placeholder and may contain ``{num}``.
            Substitution uses ``str.replace`` (``{num}`` first), so any other
            braces in the template or query are safe.
        origin_query_key: ``ext_info`` key recording the untouched original
            ``query_str`` (first expansion wins).
        variants_key: ``ext_info`` key recording the final variant list.
    """

    llm_model: str = ""
    num_queries: int = 3
    mode: str = "append"
    max_query_chars: int = 512
    prompt_template: str = _DEFAULT_USER_TEMPLATE
    origin_query_key: str = "multi_query_origin_query_str"
    variants_key: str = "multi_query_variants"

    def query_paraphrase(self, origin_query: Query) -> Query:
        """Rewrite the query with generated reformulations (best effort).

        Args:
            origin_query: The query being retrieved with. Its ``query_str``,
                ``query_text_bundles`` and ``ext_info`` are updated in place
                when expansion succeeds.

        Returns:
            The same Query object: expanded when the LLM produced usable
            variants, untouched (with a logged warning) when the query is
            empty, no ``llm_model`` is configured, generation fails, or the
            output contains no usable variant.

        Raises:
            ValueError: On invalid static configuration (unknown mode,
                out-of-range num_queries/max_query_chars, custom template
                without ``{query}``, empty ext_info keys).
        """
        self._validate_config()
        query_str = (origin_query.query_str or "").strip()
        if not query_str:
            return origin_query
        if not self.llm_model:
            logger.warning(
                "MultiQueryParaphraser %r has no llm_model configured; the query passes through unchanged.",
                self.name or self.__class__.__name__,
            )
            return origin_query
        try:
            variants = self._generate_variants(query_str)
        except Exception as exc:
            logger.warning("Multi-query expansion failed (%s); the original query is used unchanged.", exc)
            return origin_query
        if not variants:
            logger.warning("Multi-query expansion produced no usable variant; the original query is used unchanged.")
            return origin_query

        # Provenance: keep the untouched original and the generated variants
        # visible to later stages (fusion, rerankers, observability).
        origin_query.ext_info.setdefault(self.origin_query_key, origin_query.query_str)
        origin_query.ext_info[self.variants_key] = variants
        for variant in variants:
            if variant not in origin_query.query_text_bundles:
                origin_query.query_text_bundles.append(variant)
        joined = "\n".join(variants)
        if self.mode == "replace":
            origin_query.query_str = joined
        else:
            origin_query.query_str = f"{origin_query.query_str}\n{joined}"
        return origin_query

    # ------------------------------------------------------------------ #
    # Generation
    # ------------------------------------------------------------------ #
    def _generate_variants(self, query_str: str) -> list[str]:
        """One LLM call, parsed into a clean, capped, de-duplicated list.

        Raises:
            Whatever the underlying LLM call raises; the caller degrades to
            pass-through, since expansion is best-effort by contract.
        """
        llm = self._get_llm()
        user_prompt = self.prompt_template.replace("{num}", str(self.num_queries)).replace("{query}", query_str)
        messages = [
            {"role": "system", "content": _DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        output = llm.call(messages=messages, streaming=False)
        text = (getattr(output, "text", "") or "").strip()
        if not text:
            return []
        return self._parse_variants(text, query_str)

    def _parse_variants(self, text: str, query_str: str) -> list[str]:
        """Turn raw LLM output lines into the final variant list.

        Drops empty lines and lines equal to the original query
        (whitespace-folded, case-insensitive — a reformulation identical to
        the question adds no recall), de-duplicates while preserving order,
        caps at ``num_queries``, and truncates each variant to
        ``max_query_chars``.
        """
        original_folded = " ".join(query_str.split()).casefold()
        variants: list[str] = []
        seen: set[str] = set()
        for line in text.splitlines():
            variant = _normalize_variant(line)[: self.max_query_chars].strip()
            if not variant:
                continue
            folded = " ".join(variant.split()).casefold()
            if folded == original_folded or folded in seen:
                continue
            seen.add(folded)
            variants.append(variant)
            if len(variants) >= self.num_queries:
                break
        return variants

    def _get_llm(self):
        """Resolve the referenced LLM component lazily to avoid import cycles."""
        from agentuniverse.llm.llm_manager import LLMManager

        llm = LLMManager().get_instance_obj(self.llm_model)
        if llm is None:
            raise ValueError(
                f"MultiQueryParaphraser: llm '{self.llm_model}' not found. Register the LLM "
                "component, or leave llm_model empty to pass queries through."
            )
        return llm

    # ------------------------------------------------------------------ #
    # Configuration validation
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        """Fail loudly on configuration that contradicts the operator's intent.

        Raises:
            ValueError: On an unknown mode, ``num_queries`` outside [1, 10], a
                non-positive ``max_query_chars``, a custom ``prompt_template``
                without the literal ``{query}`` placeholder, or empty
                ``ext_info`` keys.
        """
        if self.mode not in _VALID_MODES:
            raise ValueError(f"Unknown multi-query mode {self.mode!r}. Known modes: {list(_VALID_MODES)}.")
        if not isinstance(self.num_queries, int) or not (_MIN_NUM_QUERIES <= self.num_queries <= _MAX_NUM_QUERIES):
            raise ValueError(
                f"num_queries must be an integer in [{_MIN_NUM_QUERIES}, {_MAX_NUM_QUERIES}], got {self.num_queries!r}."
            )
        if not isinstance(self.max_query_chars, int) or self.max_query_chars < 1:
            raise ValueError(f"max_query_chars must be a positive integer, got {self.max_query_chars!r}.")
        if not isinstance(self.prompt_template, str) or "{query}" not in self.prompt_template:
            raise ValueError("prompt_template must be a string containing the literal '{query}' placeholder.")
        if not self.origin_query_key or not self.variants_key:
            raise ValueError("origin_query_key and variants_key must be non-empty strings.")

    def _initialize_by_component_configer(self, query_paraphraser_config: ComponentConfiger) -> "MultiQueryParaphraser":
        """Initialize the paraphraser from its component config."""
        super()._initialize_by_component_configer(query_paraphraser_config)
        for attr in (
            "llm_model",
            "num_queries",
            "mode",
            "max_query_chars",
            "prompt_template",
            "origin_query_key",
            "variants_key",
        ):
            if hasattr(query_paraphraser_config, attr):
                setattr(self, attr, getattr(query_paraphraser_config, attr))
        # Validate eagerly so a misconfiguration fails at component-load time
        # rather than on the first query.
        self._validate_config()
        return self

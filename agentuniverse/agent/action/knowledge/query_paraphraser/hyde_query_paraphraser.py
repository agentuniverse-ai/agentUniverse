# !/usr/bin/env python3

# @Time    : 2026/10/02
# @FileName: hyde_query_paraphraser.py

"""
HyDE (Hypothetical Document Embeddings) query paraphraser.

Dense retrieval matches a short user query against document-shaped text,
which is a known asymmetry: the query is a question, the corpus is answers.
HyDE closes that gap by asking an LLM to write one or more short
*hypothetical passages* that would answer the query, and retrieving with
those passages instead of (or in addition to) the bare question, so the
embedding sits in the region of the corpus where real answers live.

Integration follows the framework contract — the paraphraser receives and
returns the same :class:`Query` object:

* ``query_str`` is rewritten (``append`` mode keeps the original query and
  adds the passages; ``replace`` mode uses the passages only, the classical
  HyDE form). Stores that embed ``query_str`` at query time pick this up
  with no further wiring.
* every passage is also appended to ``query_text_bundles`` ("multiple
  rewritten query text segments" in the Query contract) and recorded, with
  the untouched original query, under ``ext_info`` keys so later stages
  (fusion, rerankers, logging) can see both sides.

Expansion is best-effort by design: a missing or failing LLM, an empty
generation, or an empty query degrades to pass-through with a logged
warning — retrieval must never break because an *enhancement* failed.
Configuration errors, in contrast, fail loudly (unknown mode, out-of-range
num_docs, a custom template without the ``{query}`` placeholder), because
they mean the component is not doing what the operator believes.

Generation is bounded: ``num_docs`` passages (1-5) with one LLM call each
(so a single failing call cannot take down the others), every passage
truncated to ``max_doc_chars`` before it can reach an embedding model, and
duplicate passages de-duplicated. The LLM output is treated strictly as
retrieval text — it is never executed, parsed as structured data, or
shown to the user by this component.
"""

import logging

from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import QueryParaphraser
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

_VALID_MODES = ("append", "replace")
_MIN_NUM_DOCS = 1
_MAX_NUM_DOCS = 5

_DEFAULT_SYSTEM_PROMPT = (
    "You are a retrieval assistant. You write short, plausible passages that "
    "are used only as search text to improve dense retrieval (HyDE). You "
    "output nothing but the passage itself."
)
_DEFAULT_USER_TEMPLATE = (
    "Write one short, self-contained passage that would directly answer or "
    "address the following query. Write the passage in the same language as "
    "the query. Output only the passage itself: no preface, no explanation, "
    "no markdown.\n\nQuery: {query}"
)


class HyDEQueryParaphraser(QueryParaphraser):
    """Expand a retrieval query with LLM-generated hypothetical passages.

    Attributes:
        llm_model: Name of the registered LLM component used to generate
            hypothetical passages. When empty, the paraphraser passes queries
            through unchanged (with a warning) so the shipped yaml stays
            loadable without any model credentials.
        num_docs: Number of passages to generate, in [1, 5]; one LLM call per
            passage. Duplicates are removed before use.
        mode: ``"append"`` (default) rewrites ``query_str`` to the original
            query followed by the passages; ``"replace"`` uses the passages
            only (classical HyDE).
        max_doc_chars: Hard truncation bound applied to every generated
            passage before it reaches the query or an embedding model.
        prompt_template: Custom user-prompt template; must contain the
            literal ``{query}`` placeholder. Substitution uses
            ``str.replace``, so any other braces in the template are safe.
        origin_query_key: ``ext_info`` key under which the untouched original
            ``query_str`` is recorded (first expansion wins).
        documents_key: ``ext_info`` key under which the generated passages
            are recorded.
    """

    llm_model: str = ""
    num_docs: int = 1
    mode: str = "append"
    max_doc_chars: int = 2000
    prompt_template: str = _DEFAULT_USER_TEMPLATE
    origin_query_key: str = "hyde_origin_query_str"
    documents_key: str = "hyde_documents"

    def query_paraphrase(self, origin_query: Query) -> Query:
        """Rewrite the query with hypothetical passages (best effort).

        Args:
            origin_query: The query being retrieved with. Its ``query_str``,
                ``query_text_bundles`` and ``ext_info`` are updated in place
                when expansion succeeds.

        Returns:
            The same Query object: expanded when the LLM produced usable
            passages, untouched (with a logged warning) when the query is
            empty, no ``llm_model`` is configured, generation fails, or the
            model returns nothing usable.

        Raises:
            ValueError: On invalid static configuration (unknown mode,
                out-of-range num_docs/max_doc_chars, custom template without
                ``{query}``, empty ext_info keys).
        """
        self._validate_config()
        query_str = (origin_query.query_str or "").strip()
        if not query_str:
            return origin_query
        if not self.llm_model:
            logger.warning(
                "HyDEQueryParaphraser %r has no llm_model configured; the query passes through unchanged.",
                self.name or self.__class__.__name__,
            )
            return origin_query
        try:
            passages = self._generate_passages(query_str)
        except Exception as exc:
            logger.warning("HyDE expansion failed (%s); the original query is used unchanged.", exc)
            return origin_query
        if not passages:
            logger.warning("HyDE expansion produced no usable passage; the original query is used unchanged.")
            return origin_query

        # Provenance: keep the untouched original and the generated passages
        # visible to later stages (fusion, rerankers, observability).
        origin_query.ext_info.setdefault(self.origin_query_key, origin_query.query_str)
        origin_query.ext_info[self.documents_key] = passages
        for passage in passages:
            if passage not in origin_query.query_text_bundles:
                origin_query.query_text_bundles.append(passage)
        joined = "\n\n".join(passages)
        if self.mode == "replace":
            origin_query.query_str = joined
        else:
            origin_query.query_str = f"{origin_query.query_str}\n\n{joined}"
        return origin_query

    # ------------------------------------------------------------------ #
    # Generation
    # ------------------------------------------------------------------ #
    def _generate_passages(self, query_str: str) -> list[str]:
        """Generate up to ``num_docs`` truncated, de-duplicated passages.

        One LLM call per passage keeps failure isolation simple: a call that
        raises aborts the expansion (handled by the caller's fallback), while
        a call that returns empty text only loses that passage.
        """
        llm = self._get_llm()
        user_prompt = self.prompt_template.replace("{query}", query_str)
        messages = [
            {"role": "system", "content": _DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        passages: list[str] = []
        for _ in range(self.num_docs):
            output = llm.call(messages=messages, streaming=False)
            text = (getattr(output, "text", "") or "").strip()
            if text:
                passages.append(text[: self.max_doc_chars])
        # Order-preserving de-duplication: with a low-temperature model the
        # same passage can come back twice; retrieving with it twice adds
        # nothing.
        return list(dict.fromkeys(passages))

    def _get_llm(self):
        """Resolve the referenced LLM component lazily to avoid import cycles."""
        from agentuniverse.llm.llm_manager import LLMManager

        llm = LLMManager().get_instance_obj(self.llm_model)
        if llm is None:
            raise ValueError(
                f"HyDEQueryParaphraser: llm '{self.llm_model}' not found. Register the LLM "
                "component, or leave llm_model empty to pass queries through."
            )
        return llm

    # ------------------------------------------------------------------ #
    # Configuration validation
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        """Fail loudly on configuration that contradicts the operator's intent.

        Raises:
            ValueError: On an unknown mode, ``num_docs`` outside [1, 5], a
                non-positive ``max_doc_chars``, a custom ``prompt_template``
                without the literal ``{query}`` placeholder, or empty
                ``ext_info`` keys.
        """
        if self.mode not in _VALID_MODES:
            raise ValueError(f"Unknown HyDE mode {self.mode!r}. Known modes: {list(_VALID_MODES)}.")
        if not isinstance(self.num_docs, int) or not (_MIN_NUM_DOCS <= self.num_docs <= _MAX_NUM_DOCS):
            raise ValueError(
                f"num_docs must be an integer in [{_MIN_NUM_DOCS}, {_MAX_NUM_DOCS}], got {self.num_docs!r}."
            )
        if not isinstance(self.max_doc_chars, int) or self.max_doc_chars < 1:
            raise ValueError(f"max_doc_chars must be a positive integer, got {self.max_doc_chars!r}.")
        if not isinstance(self.prompt_template, str) or "{query}" not in self.prompt_template:
            raise ValueError("prompt_template must be a string containing the literal '{query}' placeholder.")
        if not self.origin_query_key or not self.documents_key:
            raise ValueError("origin_query_key and documents_key must be non-empty strings.")

    def _initialize_by_component_configer(self, query_paraphraser_config: ComponentConfiger) -> "HyDEQueryParaphraser":
        """Initialize the paraphraser from its component config."""
        super()._initialize_by_component_configer(query_paraphraser_config)
        for attr in (
            "llm_model",
            "num_docs",
            "mode",
            "max_doc_chars",
            "prompt_template",
            "origin_query_key",
            "documents_key",
        ):
            if hasattr(query_paraphraser_config, attr):
                setattr(self, attr, getattr(query_paraphraser_config, attr))
        # Validate eagerly so a misconfiguration fails at component-load time
        # rather than on the first query.
        self._validate_config()
        return self

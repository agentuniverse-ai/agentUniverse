"""Bounded literal glossary expansion at the existing RAG routing boundary."""
import re
from copy import deepcopy

from pydantic import Field, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.rag_router.rag_router import RagRouter
from agentuniverse.agent.action.knowledge.store.query import Query


class AliasQueryRouter(RagRouter):
    """Route original text and explicit one-step alias variants to each store.

    No model calls, inferred equivalence, cascading replacements or Cartesian
    expansion. Store filters/top-k survive; stale keywords/vectors are cleared on
    rewritten queries so the store can derive representations for the new text.
    """
    aliases: dict = Field(default_factory=dict)
    boundary: StrictStr = "word"
    max_variants: StrictInt = Field(default=4, ge=1, le=32)
    max_routes: StrictInt = Field(default=32, ge=1, le=256)
    max_query_chars: StrictInt = Field(default=4096, ge=1, le=65536)

    def _validate(self):
        if self.boundary not in ("word", "substring"):
            raise ValueError("boundary must be word or substring")
        for name, maximum in (("max_variants", 32), ("max_routes", 256), ("max_query_chars", 65536)):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(name + " is outside supported bounds")
        if type(self.aliases) is not dict or len(self.aliases) > 128:
            raise ValueError("aliases must be a mapping of at most 128 terms")
        characters = 0
        for term, replacements in self.aliases.items():
            if type(term) is not str or not term.strip() or len(term) > 128 or "\x00" in term:
                raise ValueError("glossary terms must be nonblank literals up to 128 characters")
            if type(replacements) is not list or not 1 <= len(replacements) <= 16:
                raise ValueError("each glossary term needs 1 to 16 alias strings")
            if any(type(alias) is not str or not alias.strip() or len(alias) > 256 or "\x00" in alias for alias in replacements):
                raise ValueError("aliases must be nonblank literals up to 256 characters")
            characters += len(term) + sum(map(len, replacements))
        if characters > 32768:
            raise ValueError("glossary exceeds 32768 characters")

    @staticmethod
    def _word(character):
        return character.isalnum() or character == "_"

    def _variants(self, text):
        if not self.aliases or self.max_variants == 1 or not text:
            return [text]
        # Escaped literals, leftmost match first, longest term wins overlapping
        # alternatives at the same position. Original glossary order breaks ties.
        terms = sorted(self.aliases, key=len, reverse=True)
        pattern = re.compile("|".join(re.escape(term) for term in terms))
        matches = []
        for match in pattern.finditer(text):
            start, end = match.span()
            term = match.group()
            if self.boundary == "word":
                if start and self._word(term[0]) and self._word(text[start - 1]):
                    continue
                if end < len(text) and self._word(term[-1]) and self._word(text[end]):
                    continue
            matches.append((start, end, term))
        variants, seen = [text], {text}
        for term in dict.fromkeys(item[2] for item in matches):
            for alias in self.aliases[term]:
                pieces, previous = [], 0
                for start, end, matched in matches:
                    if matched == term:
                        pieces.extend([text[previous:start], alias])
                        previous = end
                pieces.append(text[previous:])
                rewritten = "".join(pieces)
                if len(rewritten) > self.max_query_chars:
                    raise ValueError("alias-expanded query exceeds max_query_chars")
                if rewritten in seen:
                    continue
                seen.add(rewritten)
                variants.append(rewritten)
                if len(variants) == self.max_variants:
                    return variants
        return variants

    def _rag_route(self, query, store_list):
        self._validate()
        if not isinstance(query, Query):
            raise TypeError("query must be a Query")
        if type(store_list) is not list or any(type(name) is not str or not name.strip() or len(name) > 256 for name in store_list):
            raise ValueError("store_list must contain nonblank store names up to 256 characters")
        if len(store_list) > self.max_routes:
            raise ValueError("store list exceeds max_routes")
        text = query.query_str
        if text is not None and (type(text) is not str or len(text) > self.max_query_chars or "\x00" in text):
            raise ValueError("query_str must be bounded text without NUL")
        variants = self._variants(text)
        if len(variants) > 1 and (query.query_image_bundles or query.query_text_bundles):
            raise ValueError("alias rewriting of image/text-bundle queries is unsupported")
        if len(variants) * len(store_list) > self.max_routes:
            raise ValueError("expanded query/store product exceeds max_routes; reduce variants or stores")
        output = []
        for index, variant in enumerate(variants):
            for store in store_list:
                routed = deepcopy(query)
                if index:
                    routed.query_str = variant
                    routed.keywords = set()
                    routed.embeddings = []
                output.append((routed, store))
        return output

    def _initialize_by_component_configer(self, config):
        names = ("aliases", "boundary", "max_variants", "max_routes", "max_query_chars")
        checked = AliasQueryRouter(**{name: deepcopy(getattr(config, name, getattr(self, name))) for name in names})
        checked._validate()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(checked, name))
        return self

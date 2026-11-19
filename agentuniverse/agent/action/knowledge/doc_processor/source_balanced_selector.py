"""Select ranked evidence with an explicit per-source cap."""

from collections import Counter
from typing import List, Optional

from pydantic import StrictBool, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class SourceBalancedSelector(DocProcessor):
    """Keep the earliest ranked occurrences subject to a source quota.

    Source identifiers are exact, nonblank metadata strings, not store/channel
    identifiers. Missing/None/blank identifiers use document identity, so
    unrelated unlabelled documents do not share one artificial source.
    Selection preserves input order and never changes document fields.

    Attributes:
        source_key: Top-level metadata key containing a source identifier.
        max_per_source: Positive maximum occurrences per source in strict mode.
        top_n: Nonnegative output limit; None selects all quota-eligible items.
        refill: When True and top_n is set, relax quotas to fill unused slots
            with the earliest rejected occurrences, then restore input order.
    """

    source_key: StrictStr = "source"
    max_per_source: StrictInt = 1
    top_n: Optional[StrictInt] = None
    refill: StrictBool = False

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_options()

    def _validate_options(self) -> None:
        """Validate construction, configuration, and subsequent field updates."""
        if not isinstance(self.source_key, str) or not self.source_key.strip():
            raise ValueError("source_key must be a nonblank string")
        if type(self.max_per_source) is not int or self.max_per_source <= 0:
            raise ValueError("max_per_source must be a positive integer")
        if self.top_n is not None and (type(self.top_n) is not int or self.top_n < 0):
            raise ValueError("top_n must be a nonnegative integer or None")
        if type(self.refill) is not bool:
            raise ValueError("refill must be a boolean")

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Apply the cap to an already ranked list without reranking or deduping.

        Raises:
            ValueError: Options are invalid or a source value is not a string
                or None. No partial result or metadata mutation occurs.
        """
        self._validate_options()
        if not origin_docs or self.top_n == 0:
            return []

        keys = []
        for index, doc in enumerate(origin_docs):
            value = (doc.metadata or {}).get(self.source_key)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"source_key {self.source_key!r} must contain a string or None (document index {index})")
            if value is None or not value.strip():
                keys.append(("document", doc.id if doc.id is not None else index))
            else:
                keys.append(("source", value))

        counts = Counter()
        selected = []
        rejected = []
        limit = len(origin_docs) if self.top_n is None else self.top_n
        for index, key in enumerate(keys):
            if counts[key] < self.max_per_source:
                selected.append(index)
                counts[key] += 1
                if len(selected) == limit:
                    break
            elif self.refill:
                rejected.append(index)

        if self.refill and self.top_n is not None and len(selected) < limit:
            selected.extend(rejected[:limit - len(selected)])
            selected.sort()
        return [origin_docs[index] for index in selected]

    def _initialize_by_component_configer(self, config: ComponentConfiger) -> 'SourceBalancedSelector':
        """Load and validate options before replacing the configured values."""
        names = ("source_key", "max_per_source", "top_n", "refill")
        values = {name: getattr(config, name, getattr(self, name)) for name in names}
        validated = SourceBalancedSelector(**values)
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        return self

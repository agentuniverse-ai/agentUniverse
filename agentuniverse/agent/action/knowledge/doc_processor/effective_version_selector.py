"""Select the latest effective recalled version without discarding its chunks."""
import re
from datetime import datetime, timezone
from typing import List

from pydantic import StrictStr

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def _timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)", value):
        raise ValueError("timestamps require ISO date, time and explicit timezone")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc)


class EffectiveVersionSelector(DocProcessor):
    """Opt-in candidate filtering using [valid_from, valid_to) intervals.

    Requires query.ext_info[as_of_key]. Select the latest active start per
    logical document, preserving all recalled chunks of that version in their
    incoming relevance order. No history lookup or missing-chunk recovery.
    """
    document_key: StrictStr = "logical_document_id"
    version_key: StrictStr = "document_version"
    start_key: StrictStr = "valid_from"
    end_key: StrictStr = "valid_to"
    as_of_key: StrictStr = "as_of"
    missing: StrictStr = "exclude"

    def _validate_options(self):
        keys = (self.document_key, self.version_key, self.start_key, self.end_key)
        if any(not isinstance(key, str) or not key.strip() for key in keys + (self.as_of_key,)):
            raise ValueError("metadata keys must be nonblank strings")
        if len(set(keys)) != len(keys):
            raise ValueError("document metadata keys must be distinct")
        if self.missing not in ("exclude", "error"):
            raise ValueError("missing must be exclude or error")

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        self._validate_options()
        if query is None or self.as_of_key not in query.ext_info:
            raise ValueError("query.ext_info must provide an as-of timestamp")
        as_of = _timestamp(query.ext_info[self.as_of_key])
        records = []
        intervals = {}
        selected = {}
        for doc in origin_docs:
            metadata = doc.metadata or {}
            identity = metadata.get(self.document_key)
            version = metadata.get(self.version_key)
            start_text = metadata.get(self.start_key)
            if identity is None or version is None or start_text is None:
                if self.missing == "error":
                    raise ValueError("missing document/version/start metadata")
                continue
            if not isinstance(identity, str) or not identity or not isinstance(version, str) or not version:
                raise ValueError("logical document and version IDs must be nonempty strings")
            start = _timestamp(start_text)
            end_text = metadata.get(self.end_key)
            end = _timestamp(end_text) if end_text is not None else None
            if end is not None and end <= start:
                raise ValueError("valid_to must be later than valid_from")
            key = (identity, version)
            if key in intervals and intervals[key] != (start, end):
                raise ValueError("chunks of one version have inconsistent validity intervals")
            intervals[key] = (start, end)
            records.append((doc, key, start, end))
        # Inspect all versions before selecting, avoiding order-dependent ties.
        active_starts = {}
        for (identity, version), (start, end) in intervals.items():
            if start <= as_of and (end is None or as_of < end):
                start_key = (identity, start)
                if start_key in active_starts and active_starts[start_key] != version:
                    raise ValueError("multiple active versions have the same start")
                active_starts[start_key] = version
                current = selected.get(identity)
                if current is None or start > current[0]:
                    selected[identity] = (start, version)
        return [doc for doc, (identity, version), start, end in records
                if selected.get(identity) == (start, version)]

    def _initialize_by_component_configer(self, config):
        names = ("document_key", "version_key", "start_key", "end_key", "as_of_key", "missing")
        validated = EffectiveVersionSelector(**{name: getattr(config, name, getattr(self, name)) for name in names})
        validated._validate_options()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        return self

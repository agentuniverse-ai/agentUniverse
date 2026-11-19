"""Explicit Reader adapter for verified offline Document bundles."""

from typing import Optional

from pydantic import Field

from agentuniverse.agent.action.knowledge.corpus_bundle import load_bundle
from agentuniverse.agent.action.knowledge.reader.reader import Reader


class CorpusBundleReader(Reader):
    """Verify all members before returning any Documents to Knowledge."""

    name: str = "corpus_bundle_reader"
    description: str = "Verified offline Document bundle reader"
    max_bytes: int = Field(default=64 * 1024 * 1024, gt=0, strict=True)
    max_documents: int = Field(default=10_000, gt=0, strict=True)
    max_sources: int = Field(default=1000, gt=0, strict=True)
    expected_sha256: Optional[str] = None

    def _load_data(self, file, **kwargs):
        return load_bundle(
            file,
            expected_sha256=self.expected_sha256,
            max_bytes=self.max_bytes,
            max_documents=self.max_documents,
            max_sources=self.max_sources,
        )

    def _initialize_by_component_configer(self, config):
        values = config.configer.value
        parsed = type(self)(**{key: values[key] for key in type(self).model_fields if key in values})
        for key in ("name", "description", "max_bytes", "max_documents", "max_sources", "expected_sha256"):
            setattr(self, key, getattr(parsed, key))
        return self

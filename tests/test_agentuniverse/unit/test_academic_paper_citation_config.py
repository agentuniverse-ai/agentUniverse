"""Verify citation extraction settings through the document processing API."""

import inspect
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.academic_paper_fragmenter import AcademicPaperFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

PAPER_TEXT = "Prior research supports this conclusion [1] and (Smith, 2020)."


def assert_citation_result(processor: AcademicPaperFragmenter, enabled: bool) -> None:
    """Check emitted metadata while preserving source text and provenance."""
    original = Document(text=PAPER_TEXT, metadata={"paper_id": "paper-1"})
    fragments = processor.process_docs([original])

    assert len(fragments) == 1
    fragment = fragments[0]
    assert fragment.text == PAPER_TEXT
    assert fragment.metadata["source_document_id"] == original.id
    assert fragment.metadata["original_metadata"] == {"paper_id": "paper-1"}
    if enabled:
        assert fragment.metadata["citations"] == ["1", "Smith, 2020"]
        assert fragment.metadata["citation_count"] == 2
    else:
        assert "citations" not in fragment.metadata
        assert "citation_count" not in fragment.metadata


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("link_evidence", [False, True])
def test_citation_setting_with_evidence_linking(enabled: bool, link_evidence: bool) -> None:
    """Disabling extraction suppresses citation metadata with either linking setting."""
    processor = AcademicPaperFragmenter(
        name="citation_config_test",
        detect_sections=False,
        extract_citations=enabled,
        link_evidence=link_evidence,
    )
    assert_citation_result(processor, enabled)


@pytest.mark.parametrize("enabled", [False, True])
def test_citation_setting_from_component_config(enabled: bool) -> None:
    """The shipped component configuration honors an explicit extraction flag."""
    config_path = Path(inspect.getfile(AcademicPaperFragmenter)).with_suffix(".yaml")
    config = Configer(str(config_path)).load()
    config.set("extract_citations", enabled)
    config.set("detect_sections", False)
    processor = AcademicPaperFragmenter().initialize_by_component_configer(ComponentConfiger(config).load())

    assert_citation_result(processor, enabled)

"""Resolve references to whole clause headings, not prefixes or body mentions."""

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter import (
    ClauseNode,
    ContractClauseFragmenter,
)
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize(
    "reference,headings,expected",
    [
        ("Section 1", ["Section 1 Scope", "Section 10 Other", "Section 1.1 Child"], ["0"]),
        ("section 1.1", ["Section 1.10 Other", "Section 1.1 Scope"], ["1"]),
        ("Article I", ["Article II Other", "Article IV Other", "Article I Scope"], ["2"]),
        ("ARTICLE 1", ["Article 10 Other", "Article 1 Scope"], ["1"]),
        ("clause 1.2", ["1.2 Scope", "1.20 Other"], ["0"]),
        ("第十二条", ["第十二条 付款", "第一百十二条 其他"], ["0"]),
        ("Section 9", ["Section 1 See Section 9 for details", "Section 2 No match"], []),
        ("Section 1.1.", ["Section 1 Scope", "Section 1.1 Child"], ["1"]),
        ("Section 1", [" \tSECTION 1. Scope", "Article 1 Other"], ["0"]),
        ("clause 1.2", ["clause 1.2 Scope", "1.2.1 Child", "1.20 Other"], ["0"]),
        ("Article IX", ["Article IX Scope", "Article IXI Other"], ["0"]),
        ("Section 1a", ["Section 1 Scope"], []),
        ("Subsection 1", ["Section 1 Scope"], []),
        ("Article XIV", ["Article X Scope", "Article XIV Scope"], ["1"]),
        ("Section 1", ["Section 1a Other", "Section 1.2 Child"], []),
        ("Section 1.10", ["Section 1.1 Child", "Section 1.10 Scope"], ["1"]),
    ],
)
def test_reference_uses_complete_target_heading(reference, headings, expected):
    clauses = [
        ClauseNode(id=str(i), text=heading, clause_type="fixture", hierarchy_level=0)
        for i, heading in enumerate(headings)
    ]
    assert ContractClauseFragmenter()._extract_references(f"See {reference}.", clauses) == expected


def test_repeated_reference_returns_target_once():
    clauses = [ClauseNode(id="one", text="Section 1 Scope", clause_type="section", hierarchy_level=1)]
    assert ContractClauseFragmenter()._extract_references("Section 1 and SECTION 1.", clauses) == ["one"]


def test_public_fragment_metadata_does_not_link_prefix_targets():
    text = "Section 1 Scope of this agreement.\nSection 10 Other obligations apply.\nSection 2 See Section 1 for the scope."
    result = ContractClauseFragmenter(skip_on_error=False).process_docs([Document(text=text)])
    source = next(doc for doc in result if doc.metadata["clause_id"] == "section_2")
    refs = source.metadata["clause_references"]
    assert "section_1" in refs
    assert "section_10" not in refs


def test_no_target_does_not_invent_a_reference():
    assert ContractClauseFragmenter()._extract_references("See Section 1.", []) == []


def test_disabled_references_preserves_document_metadata():
    doc = Document(
        text="Section 1 Scope of the agreement.\nSection 2 See Section 1 for its scope.",
        metadata={"source": "contract.pdf"},
    )
    result = ContractClauseFragmenter(extract_references=False, skip_on_error=False).process_docs([doc])
    assert len(result) == 2
    assert all("clause_references" not in item.metadata for item in result)
    assert all(item.metadata["original_metadata"] == {"source": "contract.pdf"} for item in result)

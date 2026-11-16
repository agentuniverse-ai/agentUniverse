"""Source provenance survives hierarchical chunk creation."""

from copy import deepcopy

from agentuniverse.agent.action.knowledge.doc_processor.hierarchical_regex_text_splitter import (
    HierarchicalRegexTextSplitter,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def make_splitter():
    return HierarchicalRegexTextSplitter(hierarchical_index=[
        {"reg_exp": r"Chapter \w+", "need_summary": False},
        {"reg_exp": r"Section \w+", "need_summary": False},
    ])


def test_all_heading_chunks_keep_their_source_metadata():
    sources = [
        Document(text="Chapter A\nSection A1\nBody A", metadata={
            "source": "a.txt", "tenant": "tenant-a", "page": 3,
        }),
        Document(text="Chapter B\nSection B1\nBody B", metadata={
            "source": "b.txt", "tenant": "tenant-b", "page": 7,
        }),
    ]

    chunks = make_splitter().process_docs(sources)

    assert len(chunks) == 4
    for source, offset in zip(sources, (0, 2)):
        for chunk in chunks[offset:offset + 2]:
            for key, value in source.metadata.items():
                assert chunk.metadata[key] == value
        assert chunks[offset + 1].metadata["hierarchical_parent"] == chunks[offset].id


def test_nested_metadata_is_independent_of_source_and_siblings():
    source = Document(text="Chapter A\nSection A1\nBody", metadata={
        "citation": {"pages": [1, 2]}, "tags": ["original"],
    })
    before = deepcopy(source.metadata)
    chunks = make_splitter().process_docs([source])

    chunks[1].metadata["citation"]["pages"].append(3)
    chunks[1].metadata["tags"].append("child-only")

    assert source.metadata == before
    assert chunks[0].metadata["citation"] == before["citation"]
    assert chunks[0].metadata["tags"] == before["tags"]


def test_generated_hierarchy_overrides_stale_source_fields():
    source = Document(text="Chapter A\nSection A1", metadata={
        "source": "a.txt", "hierarchical_parent": "stale",
        "hierarchical_level": 99, "hierarchical_info": "old heading",
    })
    before = deepcopy(source.metadata)

    parent, child = make_splitter().process_docs([source])

    assert parent.metadata == {
        "source": "a.txt", "hierarchical_parent": "root",
        "hierarchical_level": 0, "hierarchical_info": "Chapter A",
    }
    assert child.metadata == {
        "source": "a.txt", "hierarchical_parent": parent.id,
        "hierarchical_level": 1, "hierarchical_info": "Section A1",
    }
    assert source.metadata == before


def test_document_without_source_metadata_still_splits():
    parent, child = make_splitter().process_docs([
        Document(text="Chapter A\nSection A1\nBody", metadata=None),
    ])

    assert parent.metadata["hierarchical_level"] == 0
    assert child.metadata["hierarchical_parent"] == parent.id

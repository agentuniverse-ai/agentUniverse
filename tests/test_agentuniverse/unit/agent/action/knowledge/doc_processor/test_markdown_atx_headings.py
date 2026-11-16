"""ATX boundary regressions for the public document-processing interface.

Opening/closing marker rules: https://spec.commonmark.org/0.31.2/#atx-headings
The processor retains raw inline title markup, rather than rendering HTML.
"""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.markdown_header_text_splitter import (
    MarkdownHeaderTextSplitter,
)
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize("heading,title", [
    ("# C#", "C#"),
    ("## F#", "F#"),
    ("### release###", "release###"),
    ("# C# ###", "C#"),
    (r"# literal \#", r"literal \#"),
    (r"## literal #\##", r"literal #\##"),
    (r"### literal \###", r"literal \###"),
    ("# actual closing ### \t", "actual closing"),
    ("# hashes ### remain text", "hashes ### remain text"),
    ("#\tTabbed\tTitle\t", "Tabbed\tTitle"),
    ("# \u00a0Title\u00a0", "\u00a0Title\u00a0"),
    ("# ###", ""),
    ("##\t", ""),
    ("# " + " " * 10000 + "C#", "C#"),
])
def test_title_retains_literal_hashes_and_only_strips_closing_markers(heading, title):
    doc, = MarkdownHeaderTextSplitter().process_docs([
        Document(text=heading + "\nsection body", metadata={"source": "guide.md"}),
    ])
    assert doc.text == "section body"
    assert doc.metadata == {"source": "guide.md", "header_path": title}


@pytest.mark.parametrize("level", range(1, 7))
def test_empty_heading_without_whitespace_starts_a_section(level):
    doc, = MarkdownHeaderTextSplitter(keep_preamble=False).process_docs([
        Document(text="#" * level + "\nbody after an empty heading"),
    ])
    assert doc.text == "body after an empty heading"
    assert doc.metadata["header_path"] == ""


@pytest.mark.parametrize("indent", [0, 1, 2, 3])
def test_up_to_three_spaces_indent_a_real_heading(indent):
    docs = MarkdownHeaderTextSplitter().process_docs([
        Document(text="# Parent\nintro\n" + " " * indent + "## Child\nchild body"),
    ])
    assert [(d.metadata["header_path"], d.text) for d in docs] == [
        ("Parent", "intro"), ("Parent > Child", "child body"),
    ]


@pytest.mark.parametrize("line", [
    "#NoSpace", "####### Too many", r"\# Escaped", "    # Indented code",
    "\t# Indented code", "#\u00a0Not an ASCII separator",
])
def test_non_heading_lines_remain_body_content(line):
    doc, = MarkdownHeaderTextSplitter().process_docs([
        Document(text="# Real\n" + line + "\nfollowing body"),
    ])
    assert doc.text == line + "\nfollowing body"
    assert doc.metadata["header_path"] == "Real"


def test_empty_heading_resets_previous_hierarchy():
    docs = MarkdownHeaderTextSplitter().process_docs([
        Document(text="# Old\n## Child\nold body\n#\nreset body\n## New\nnew body"),
    ])
    assert [(d.metadata["header_path"], d.text) for d in docs] == [
        ("Old > Child", "old body"), ("", "reset body"), (" > New", "new body"),
    ]


@pytest.mark.parametrize("fence", ["```", "~~~"])
def test_indented_hash_lines_inside_fences_remain_code(fence):
    docs = MarkdownHeaderTextSplitter().process_docs([
        Document(text=f"# Root\n{fence}\n  # C#\n#\n{fence}\n  ## After\nbody"),
    ])
    assert [(d.metadata["header_path"], d.text) for d in docs] == [
        ("Root", f"{fence}\n  # C#\n#\n{fence}"), ("Root > After", "body"),
    ]


def test_configured_max_level_and_metadata_contract():
    processor = MarkdownHeaderTextSplitter(
        max_header_level=1, header_path_key="section", path_separator=" / ",
        keep_preamble=False,
    )
    original = Document(text="preface\n  # C#\n## Not split\nbody", metadata={"source": "manual"})
    doc, = processor.process_docs([original])
    assert doc.text == "## Not split\nbody"
    assert doc.metadata == {"source": "manual", "section": "C#"}
    assert original.metadata == {"source": "manual"}
    assert original.text.startswith("preface\n")

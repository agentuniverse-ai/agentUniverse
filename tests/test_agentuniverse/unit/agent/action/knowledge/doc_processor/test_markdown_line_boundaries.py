"""Exercise Markdown line boundaries through real framework components.

CommonMark 0.31.2 section 2.1 defines only CRLF, CR and LF as line endings.
Python's str.splitlines() also splits the characters below, which are content
in Markdown. No parser, Document or processor method is replaced in these tests.
"""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.markdown_header_text_splitter import (
    MarkdownHeaderTextSplitter,
)
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.store.document import Document


CONTENT_SEPARATORS = ["\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"]


@pytest.mark.parametrize("separator", CONTENT_SEPARATORS)
def test_file_content_separator_does_not_start_a_heading(tmp_path, separator):
    text = "# Root\nparagraph" + separator + "# Literal\nending\n## Child\nchild body"
    path = tmp_path / "source.txt"
    path.write_text(text, encoding="utf-8")
    source_docs = TxtReader().load_data(path, ext_info={"collection": "manual"})
    assert source_docs[0].text == text

    chunks = MarkdownHeaderTextSplitter().process_docs(source_docs)

    assert [(doc.metadata["header_path"], doc.text) for doc in chunks] == [
        ("Root", "paragraph" + separator + "# Literal\nending"),
        ("Root > Child", "child body"),
    ]
    assert all(doc.metadata["file_name"] == "source.txt" for doc in chunks)
    assert all(doc.metadata["collection"] == "manual" for doc in chunks)
    assert source_docs[0].text == text
    assert source_docs[0].metadata == {"file_name": "source.txt", "collection": "manual"}


@pytest.mark.parametrize("separator", CONTENT_SEPARATORS)
@pytest.mark.parametrize("fence", ["```", "~~~"])
def test_content_separator_does_not_close_a_fence(separator, fence):
    body = fence + "text\npayload" + separator + fence + "\n# still code\n" + fence
    source = Document(text="# Root\n" + body + "\n## Real\nbody")

    chunks = MarkdownHeaderTextSplitter().process_docs([source])

    assert [(doc.metadata["header_path"], doc.text) for doc in chunks] == [
        ("Root", body), ("Root > Real", "body"),
    ]


@pytest.mark.parametrize("separator", CONTENT_SEPARATORS)
def test_content_separator_does_not_open_a_fence(separator):
    body = "payload" + separator + "```text"
    chunks = MarkdownHeaderTextSplitter().process_docs([
        Document(text="# Root\n" + body + "\n## Child\nchild body"),
    ])

    assert [(doc.metadata["header_path"], doc.text) for doc in chunks] == [
        ("Root", body), ("Root > Child", "child body"),
    ]


@pytest.mark.parametrize("separator", CONTENT_SEPARATORS)
def test_content_separator_stays_in_the_header_title(separator):
    title = "Real" + separator + "Title"
    chunk, = MarkdownHeaderTextSplitter().process_docs([
        Document(text="# " + title + "\nbody"),
    ])

    assert chunk.text == "body"
    assert chunk.metadata["header_path"] == title


@pytest.mark.parametrize("ending", ["\n", "\r", "\r\n"])
@pytest.mark.parametrize("final_ending", [False, True])
def test_markdown_line_endings_still_split_headings_and_fences(ending, final_ending):
    text = ending.join(["# Root", "```", "# Code", "```", "## Child", "body"])
    if final_ending:
        text += ending

    chunks = MarkdownHeaderTextSplitter().process_docs([Document(text=text)])

    assert [(doc.metadata["header_path"], doc.text) for doc in chunks] == [
        ("Root", "```\n# Code\n```"), ("Root > Child", "body"),
    ]

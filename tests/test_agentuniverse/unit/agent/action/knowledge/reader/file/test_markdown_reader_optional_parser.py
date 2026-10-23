"""Markdown must be readable without the optional `unstructured` package.

`MarkdownReader` is what `FileReader` routes `.md` and `.markdown` to, and
`unstructured` is not a declared dependency, so before this the default reader
raised ImportError for every markdown file. The archive readers swallowed that
ImportError, so a `.md` entry simply disappeared from the output.
"""

import builtins
import sys

import pytest

from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader
from agentuniverse.agent.action.knowledge.reader.file.markdown_reader import MarkdownReader

MARKDOWN = """# Title

Some **markdown** body.
"""


@pytest.fixture()
def markdown_file(tmp_path):
    path = tmp_path / "notes.md"
    path.write_text(MARKDOWN, encoding="utf-8")
    return path


@pytest.fixture()
def without_unstructured(monkeypatch):
    """Make the optional parser look uninstalled, as it is by default."""
    monkeypatch.setitem(sys.modules, "unstructured", None)

    real_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "unstructured" or name.startswith("unstructured."):
            raise ImportError("No module named 'unstructured'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)


def test_markdown_is_read_without_unstructured(markdown_file, without_unstructured):
    documents = MarkdownReader().load_data(markdown_file)

    assert len(documents) == 1
    assert documents[0].text == MARKDOWN


def test_markdown_keeps_file_name_and_ext_info(markdown_file, without_unstructured):
    documents = MarkdownReader().load_data(markdown_file, ext_info={"archived": True})

    assert documents[0].metadata["file_name"] == "notes.md"
    assert documents[0].metadata["archived"] is True


def test_markdown_accepts_a_string_path(markdown_file, without_unstructured):
    documents = MarkdownReader().load_data(str(markdown_file))

    assert documents[0].text == MARKDOWN


def test_file_reader_reads_markdown(markdown_file, without_unstructured):
    """`.md` is routed to MarkdownReader by the default file reader."""
    documents = FileReader().load_data([markdown_file])

    assert len(documents) == 1
    assert documents[0].text == MARKDOWN
    assert documents[0].metadata["file_name"] == "notes.md"


def test_markdown_that_is_not_utf8_is_still_readable(tmp_path, without_unstructured):
    path = tmp_path / "gbk.md"
    path.write_bytes("# 标题\n\n正文\n".encode("gbk"))

    documents = MarkdownReader().load_data(path)

    assert "正文" in documents[0].text


def test_sevenzip_does_not_drop_markdown_entries(tmp_path, without_unstructured):
    """The archive readers used to swallow the ImportError and lose the file."""
    py7zr = pytest.importorskip("py7zr")
    from agentuniverse.agent.action.knowledge.reader.file.sevenzip_reader import SevenZipReader

    source = tmp_path / "src"
    source.mkdir()
    (source / "a.txt").write_text("plain", encoding="utf-8")
    (source / "notes.md").write_text(MARKDOWN, encoding="utf-8")

    archive_path = tmp_path / "t.7z"
    with py7zr.SevenZipFile(archive_path, "w") as archive:
        archive.writeall(str(source), "")

    documents = SevenZipReader()._load_data(archive_path)

    names = sorted(document.metadata["file_name"] for document in documents)
    assert names == ["a.txt", "notes.md"]


def test_an_empty_document_list_from_the_parser_falls_back_to_text(tmp_path, monkeypatch):
    """A parser that loads no documents must not make the reader index an empty list.

    `UnstructuredMarkdownLoader.load()` returns no documents for an empty or
    whitespace-only file. Indexing `documents[0]` then raised IndexError and the
    reader crashed instead of returning the (empty) file text.
    """
    empty = tmp_path / "empty.md"
    empty.write_text("", encoding="utf-8")

    import types

    fake = types.ModuleType("langchain_community.document_loaders")

    class _Loader:
        def __init__(self, file):
            pass

        def load(self):
            return []

    fake.UnstructuredMarkdownLoader = _Loader
    monkeypatch.setitem(sys.modules, "langchain_community.document_loaders", fake)

    documents = MarkdownReader().load_data(empty)

    assert len(documents) == 1
    assert documents[0].text == ""


def test_unstructured_output_is_used_when_available(markdown_file):
    """With the parser installed the reader keeps its previous behaviour."""
    pytest.importorskip("unstructured")
    pytest.importorskip("markdown")

    documents = MarkdownReader().load_data(markdown_file)

    assert len(documents) == 1
    assert "markdown" in documents[0].text

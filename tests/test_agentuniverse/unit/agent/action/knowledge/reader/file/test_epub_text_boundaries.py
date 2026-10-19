"""Keep EPUB block boundaries without splitting words around inline markup."""

import sys

import pytest

from agentuniverse.agent.action.knowledge.reader.file.epub_reader import EpubReader


@pytest.fixture(params=["beautifulsoup", "fallback"])
def reader(request, monkeypatch):
    if request.param == "fallback":
        monkeypatch.setitem(sys.modules, "bs4", None)
    else:
        pytest.importorskip("bs4")
    return EpubReader()


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        ("<p>First paragraph</p><p>Second paragraph</p>",
         "First paragraph Second paragraph"),
        ("<div>Lead<p>Middle</p>Tail</div>", "Lead Middle Tail"),
        ("Alpha<br/>Beta<HR/>Gamma", "Alpha Beta Gamma"),
        ("<h1>Heading</h1><ul><li>One</li><li>Two</li></ul>"
         "<table><tr><td>Left</td><td>Right</td></tr></table>",
         "Heading One Two Left Right"),
        ("<p title=\"1 > 0\">First</p><p title='2 > 1'>Second</p>",
         "First Second"),
        ("co<strong>oper</strong>ation and in<p-note>line</p-note> &lt;br&gt;",
         "cooperation and inline <br>"),
        ("<p>第一段</p><p>第二段，保<strong>留</strong>行内文字</p>",
         "第一段 第二段，保留行内文字"),
    ],
)
def test_html_text_boundaries(reader, markup, expected):
    assert reader._extract_text_from_html(markup) == expected


def test_real_epub_preserves_breaks_and_mixed_block_content(reader, tmp_path):
    epub = pytest.importorskip("ebooklib.epub")
    book = epub.EpubBook()
    book.set_identifier("text-boundaries")
    book.set_title("Boundary Book")
    book.set_language("en")
    chapter = epub.EpubHtml(title="Sample", file_name="chapter.xhtml")
    chapter.content = (
        "<h1>Heading</h1><p>Alpha<br/>Beta</p>"
        "<div>Lead<p>Middle</p>Tail</div>"
        "<p>co<strong>oper</strong>ation</p>"
    )
    book.add_item(chapter)
    book.toc = (chapter,)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", chapter]
    path = tmp_path / "boundaries.epub"
    epub.write_epub(str(path), book, {})

    documents = reader.load_data(path, ext_info={"collection": "books"})
    chapters = [doc for doc in documents
                if doc.metadata["chapter_file"] == "chapter.xhtml"]

    assert len(chapters) == 1
    assert chapters[0].text.endswith(
        "Heading Alpha Beta Lead Middle Tail cooperation"
    )
    assert chapters[0].metadata["file_name"] == "boundaries.epub"
    assert chapters[0].metadata["title"] == "Boundary Book"
    assert chapters[0].metadata["collection"] == "books"

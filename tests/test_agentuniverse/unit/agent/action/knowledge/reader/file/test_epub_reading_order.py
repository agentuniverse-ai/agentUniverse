"""Regression tests for EPUB chapter ordering using real EPUB files."""

from pathlib import Path

from ebooklib import epub

from agentuniverse.agent.action.knowledge.reader.file.epub_reader import EpubReader


def _write_book(path: Path, spine):
    """Write chapters in manifest order with an independently ordered spine."""
    book = epub.EpubBook()
    book.set_identifier("reading-order-test")
    book.set_title("Reading order test")
    book.set_language("en")
    for uid in ("second", "first", "appendix"):
        chapter = epub.EpubHtml(uid=uid, title=uid, file_name=f"{uid}.xhtml")
        chapter.content = f"<p>{uid} chapter body</p>"
        book.add_item(chapter)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.toc = tuple(book.get_item_with_id(uid) for uid in ("first", "second"))
    book.spine = spine
    epub.write_epub(str(path), book)


def test_chapters_follow_spine_instead_of_manifest_order(tmp_path):
    """Chapter content and numbering must follow the declared reading order."""
    path = tmp_path / "reordered.epub"
    _write_book(path, ["first", "second", "appendix"])

    documents = EpubReader().load_data(path, ext_info={"source": "test"})

    assert [doc.metadata["chapter_id"] for doc in documents[:3]] == [
        "first", "second", "appendix"
    ]
    assert [doc.metadata["chapter_number"] for doc in documents[:3]] == [1, 2, 3]
    assert "first chapter body" in documents[0].text
    assert "second chapter body" in documents[1].text
    assert all(doc.metadata["source"] == "test" for doc in documents)


def test_non_spine_documents_are_retained_after_spine_documents(tmp_path):
    """Keep supplementary content without disrupting spine chapter order."""
    path = tmp_path / "supplement.epub"
    _write_book(path, ["first", "second"])

    documents = EpubReader().load_data(str(path))

    assert [doc.metadata["chapter_id"] for doc in documents] == [
        "first", "second", "appendix", "nav"
    ]
    assert len({doc.metadata["chapter_id"] for doc in documents}) == len(documents)


def test_empty_spine_falls_back_to_manifest_order(tmp_path):
    """An empty spine must not cause any previously readable content to vanish."""
    path = tmp_path / "empty-spine.epub"
    _write_book(path, [])

    documents = EpubReader().load_data(path)

    assert [doc.metadata["chapter_id"] for doc in documents] == [
        "second", "first", "appendix", "nav"
    ]


def test_non_linear_spine_document_keeps_its_declared_position(tmp_path):
    """Retain non-linear content while honoring its position in the spine."""
    path = tmp_path / "non-linear.epub"
    _write_book(path, ["first", ("appendix", "no"), "second"])

    documents = EpubReader().load_data(path)

    assert [doc.metadata["chapter_id"] for doc in documents[:3]] == [
        "first", "appendix", "second"
    ]

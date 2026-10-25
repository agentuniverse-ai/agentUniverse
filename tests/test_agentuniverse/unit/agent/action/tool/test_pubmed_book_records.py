"""Exercise mixed NLM record types through real HTTP and PubMedTool.execute."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree

import pytest

from agentuniverse.agent.action.tool.common_tool.pubmed_tool import PubMedTool


# Authored fixtures follow NLM's PubmedBookArticle/BookDocument content models:
# https://dtd.nlm.nih.gov/ncbi/pubmed/doc/out/190101/el-PubmedBookArticle.html
# https://dtd.nlm.nih.gov/ncbi/pubmed/doc/out/190101/el-BookDocument.html
BOOK = """<PubmedBookArticle><BookDocument>
  <PMID>222</PMID>
  <ArticleIdList><ArticleId IdType="doi">10.1000/chapter</ArticleId></ArticleIdList>
  <Book>
    <Publisher><PublisherName>Example Press</PublisherName></Publisher>
    <BookTitle>Handbook of <i>testing</i></BookTitle>
    <PubDate><Year>2020</Year><Month>May</Month><Day>12</Day></PubDate>
    <AuthorList Type="editors"><Author><LastName>Editor</LastName><ForeName>Eve</ForeName></Author></AuthorList>
    <AuthorList Type="authors"><Author><CollectiveName>Book Authors</CollectiveName></Author></AuthorList>
    <Isbn>9780000000000</Isbn>
  </Book>
  <ArticleTitle>Chapter on <i>reliable</i> parsing</ArticleTitle>
  <Language>eng</Language><Language>fra</Language>
  <AuthorList Type="authors">
    <Author><ForeName>Alice</ForeName><LastName>Writer</LastName></Author>
    <Author><CollectiveName>Chapter Group</CollectiveName></Author>
  </AuthorList>
  <PublicationType>Review</PublicationType>
  <Abstract><AbstractText Label="BACKGROUND">A <b>book</b> chapter.</AbstractText>
    <AbstractText>Second paragraph.</AbstractText></Abstract>
  <KeywordList><Keyword>structured <i>data</i></Keyword></KeywordList>
</BookDocument><PubmedBookData><ArticleIdList>
  <ArticleId IdType="doi">10.1000/secondary</ArticleId>
</ArticleIdList></PubmedBookData></PubmedBookArticle>"""

JOURNAL = """<PubmedArticle><MedlineCitation><PMID>111</PMID><Article>
  <ArticleTitle>A journal article</ArticleTitle>
  <AuthorList><Author><ForeName>Jane</ForeName><LastName>Author</LastName></Author></AuthorList>
  <Journal><Title>Example Journal</Title><ISSN>1234-5678</ISSN>
    <JournalIssue><PubDate><Year>2024</Year></PubDate></JournalIssue></Journal>
  <Language>eng</Language>
</Article></MedlineCitation><PubmedData><ArticleIdList>
  <ArticleId IdType="doi">10.1000/journal</ArticleId>
</ArticleIdList></PubmedData></PubmedArticle>"""


def modified_book(edit):
    """Return an independent XML fixture, retaining the actual record hierarchy."""
    record = ElementTree.fromstring(BOOK)
    edit(record.find("BookDocument"))
    return ElementTree.tostring(record, encoding="unicode")


@pytest.fixture
def fetch_records():
    """Serve ESearch/EFetch fixtures without mocking requests or XML parsing."""
    state = {"records": [], "requests": []}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path)
            state["requests"].append((path.path, parse_qs(path.query)))
            if path.path == "/esearch.fcgi":
                ids = [ElementTree.fromstring(record).findtext(".//PMID")
                       for record in state["records"]]
                body = json.dumps({"esearchresult": {
                    "count": str(len(ids)), "idlist": ids}}).encode()
                content_type = "application/json"
            elif path.path == "/efetch.fcgi":
                body = ("<PubmedArticleSet>" + "".join(state["records"])
                        + "</PubmedArticleSet>").encode()
                content_type = "application/xml"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
    thread.start()

    def fetch(records):
        state["records"] = records
        state["requests"] = []
        tool = PubMedTool(base_url=f"http://127.0.0.1:{server.server_port}",
                          email=None, api_key=None)
        result = tool.execute("book and journal citations", max_results=20)
        assert "error" not in result
        assert len(state["requests"]) == 2
        assert state["requests"][0][0] == "/esearch.fcgi"
        assert state["requests"][1][0] == "/efetch.fcgi"
        assert state["requests"][1][1]["db"] == ["pubmed"]
        assert state["requests"][1][1]["retmode"] == ["xml"]
        return result

    yield fetch
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    assert not thread.is_alive()


def test_book_only_query_returns_one_paper(fetch_records):
    result = fetch_records([BOOK])
    assert result["total_results"] == result["returned_results"] == 1
    assert result["papers"][0]["pmid"] == "222"


@pytest.mark.parametrize("records,expected", [
    ([JOURNAL, BOOK], ["111", "222"]),
    ([BOOK, JOURNAL], ["222", "111"]),
    ([BOOK, JOURNAL, BOOK.replace("222", "333")], ["222", "111", "333"]),
])
def test_mixed_record_order_is_preserved(fetch_records, records, expected):
    result = fetch_records(records)
    assert result["returned_results"] == len(expected)
    assert [paper["pmid"] for paper in result["papers"]] == expected


def test_chapter_fields_come_from_book_document(fetch_records):
    paper = fetch_records([BOOK])["papers"][0]
    assert paper["title"] == "Chapter on reliable parsing"
    assert paper["book_title"] == "Handbook of testing"
    assert paper["authors"] == ["Alice Writer", "Chapter Group"]
    assert paper["abstract"] == "BACKGROUND: A book chapter.\nSecond paragraph."
    assert paper["published"] == "2020-May-12"
    assert paper["publication_types"] == ["Review"]
    assert paper["languages"] == ["eng", "fra"]
    assert paper["keywords"] == ["structured data"]
    assert paper["doi"] == "10.1000/chapter"
    assert paper["entry_url"] == "https://pubmed.ncbi.nlm.nih.gov/222/"
    assert paper["journal"] == paper["journal_issn"] == ""
    assert paper["mesh_terms"] == []


def test_whole_book_uses_book_title_and_authors(fetch_records):
    def edit(document):
        document.remove(document.find("ArticleTitle"))
        document.remove(document.find("AuthorList"))
    paper = fetch_records([modified_book(edit)])["papers"][0]
    assert paper["title"] == paper["book_title"] == "Handbook of testing"
    assert paper["authors"] == ["Book Authors"]


def test_editors_are_not_returned_as_authors(fetch_records):
    def edit(document):
        document.remove(document.find("AuthorList"))
        book = document.find("Book")
        book.remove(book.find("AuthorList[@Type='authors']"))
    paper = fetch_records([modified_book(edit)])["papers"][0]
    assert paper["authors"] == []


def test_optional_book_fields_may_be_absent(fetch_records):
    record = """<PubmedBookArticle><BookDocument><PMID>444</PMID>
      <ArticleIdList/><Book><BookTitle>Minimal book</BookTitle></Book>
    </BookDocument></PubmedBookArticle>"""
    paper = fetch_records([record])["papers"][0]
    assert paper["pmid"] == "444"
    assert paper["title"] == "Minimal book"
    for key in ("authors", "publication_types", "languages", "keywords", "mesh_terms"):
        assert paper[key] == []
    for key in ("published", "abstract", "doi", "journal", "journal_issn"):
        assert paper[key] == ""


def test_medline_book_date_is_preserved(fetch_records):
    def edit(document):
        date = document.find("Book/PubDate")
        date.clear()
        ElementTree.SubElement(date, "MedlineDate").text = "2020 Spring"
    paper = fetch_records([modified_book(edit)])["papers"][0]
    assert paper["published"] == "2020 Spring"


def test_book_data_identifier_fallback_is_used(fetch_records):
    def edit(document):
        document.find("ArticleIdList").clear()
    paper = fetch_records([modified_book(edit)])["papers"][0]
    assert paper["doi"] == "10.1000/secondary"


def test_reference_metadata_cannot_replace_missing_citation_fields(fetch_records):
    def edit(document):
        document.find("ArticleIdList").clear()
        document.find("Book").remove(document.find("Book/PubDate"))
        refs = ElementTree.SubElement(document, "ReferenceList")
        reference = ElementTree.SubElement(refs, "Reference")
        ElementTree.SubElement(reference, "ArticleTitle").text = "Referenced title"
        ids = ElementTree.SubElement(reference, "ArticleIdList")
        ElementTree.SubElement(ids, "ArticleId", IdType="doi").text = "10.1000/reference"
    record = modified_book(edit).replace("10.1000/secondary", "")
    paper = fetch_records([record])["papers"][0]
    assert paper["title"] == "Chapter on reliable parsing"
    assert paper["published"] == paper["doi"] == ""


def test_journal_output_remains_unchanged_in_mixed_results(fetch_records):
    original = fetch_records([JOURNAL])["papers"][0]
    mixed = fetch_records([BOOK, JOURNAL])["papers"]
    assert next(paper for paper in mixed if paper["pmid"] == "111") == original
    assert original["journal"] == "Example Journal"
    assert original["doi"] == "10.1000/journal"
    assert "book_title" not in original

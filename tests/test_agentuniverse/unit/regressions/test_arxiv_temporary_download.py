import sys
from pathlib import Path
from types import SimpleNamespace

from agentuniverse.agent.action.tool.common_tool.arxiv_tool import ArxivTool


class SearchEngine:
    def __init__(self, paper):
        self.paper = paper

    def results(self, _search):
        return iter([self.paper])


def test_arxiv_detail_uses_and_cleans_unique_temporary_pdf(monkeypatch):
    downloaded_paths = []

    class Paper:
        def download_pdf(self, filename):
            downloaded_paths.append(filename)
            Path(filename).write_bytes(b"fake pdf")

    class PdfReader:
        def __init__(self, filename):
            assert Path(filename).exists()
            self.pages = [SimpleNamespace(extract_text=lambda: "paper text")]

    monkeypatch.setitem(sys.modules, "arxiv", SimpleNamespace(Search=lambda **kwargs: kwargs))
    monkeypatch.setitem(sys.modules, "pypdf", SimpleNamespace(PdfReader=PdfReader))

    tool = ArxivTool(sch_engine=SearchEngine(Paper()))
    result = ArxivTool.retrieve_full_paper_text.__wrapped__(tool, "paper-id")

    assert result == "paper text"
    assert len(downloaded_paths) == 1
    assert downloaded_paths[0].endswith(".pdf")
    assert not Path(downloaded_paths[0]).exists()

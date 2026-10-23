"""Search summaries retain the canonical identifier independently of PDF links."""
from datetime import datetime
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.tool.common_tool.arxiv_tool import ArxivTool

arxiv = pytest.importorskip("arxiv")


def make_result(paper_id, with_pdf=True):
    links = ([arxiv.Result.Link(f"https://arxiv.org/pdf/{paper_id}", title="pdf")]
             if with_pdf else [])
    return arxiv.Result(
        entry_id=f"http://arxiv.org/abs/{paper_id}", title="Example paper",
        authors=[arxiv.Result.Author("A. Author")],
        published=datetime(2020, 1, 2), summary="First line\nSecond line",
        links=links,
    )


@pytest.mark.parametrize("paper_id", ["2401.12345v2", "hep-th/9901001v1", "quant-ph/0201082v1"])
@pytest.mark.parametrize("with_pdf", [True, False])
def test_search_uses_result_identifier(paper_id, with_pdf):
    result = make_result(paper_id, with_pdf)
    engine = Mock()
    engine.results.return_value = iter([result])
    output = ArxivTool(sch_engine=engine).execute("quantum", mode="search")
    assert f"Paper ID: {paper_id}\n" in output
    assert "[1] Example paper" in output
    assert "Authors: A. Author" in output
    assert "Published: 2020-01-02" in output
    assert "Summary: First line Second line" in output
    assert f"PDF URL: {result.pdf_url}\n" in output
    search = engine.results.call_args.args[0]
    assert search.query == "abs:quantum"
    assert search.max_results == 10
    assert search.sort_by == arxiv.SortCriterion.Relevance


def test_distinct_archives_remain_distinct_and_ordered():
    ids = ["hep-th/9901001v1", "quant-ph/9901001v1"]
    engine = Mock()
    engine.results.return_value = iter(make_result(paper_id) for paper_id in ids)
    output = ArxivTool(sch_engine=engine).execute("quantum", mode="search")
    assert output.index(f"Paper ID: {ids[0]}") < output.index(f"Paper ID: {ids[1]}")


def test_empty_results_unchanged():
    engine = Mock()
    engine.results.return_value = iter(())
    assert ArxivTool(sch_engine=engine).execute("quantum", mode="search") == "No papers found."

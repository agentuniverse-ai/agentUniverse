import sys
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.tool.common_tool.arxiv_tool import ArxivTool


class EmptySearchEngine:
    def results(self, search):
        return iter(())


def test_missing_paper_raises_descriptive_error(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "arxiv",
        SimpleNamespace(Search=lambda **kwargs: kwargs),
    )
    tool = ArxivTool(name="arxiv", sch_engine=EmptySearchEngine())

    with pytest.raises(ValueError, match="No arXiv paper found for ID: missing"):
        ArxivTool.retrieve_full_paper_text.__wrapped__(tool, "missing")

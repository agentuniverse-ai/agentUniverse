"""Regression tests for arXiv tool input validation."""

import pytest

from agentuniverse.agent.action.tool.common_tool.arxiv_tool import ArxivTool


@pytest.mark.parametrize("query", [None, "", "   "])
def test_execute_rejects_empty_input_before_loading_dependencies(query):
    tool = ArxivTool(name="arxiv")

    with pytest.raises(ValueError, match="input must be a non-empty string"):
        tool.execute(query, mode="search")

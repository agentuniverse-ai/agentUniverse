"""Length-limited arXiv searches retain a nonempty query prefix."""
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.tool.common_tool.arxiv_tool import ArxivTool


@pytest.fixture
def arxiv_sdk():
    return pytest.importorskip('arxiv')


@pytest.mark.parametrize('query,limit,expected', [
    ('学' * 301, 300, '学' * 300),
    ('a' * 301, 300, 'a' * 300),
    ('a' * 300 + ' next', 300, 'a' * 300),
    ('a' * 299 + ' next', 300, 'a' * 299),
    ('abc def ghi', 7, 'abc def'),
    ('abc def ghi', 6, 'abc'),
    ('abcdef more', 3, 'abc'),
    ('a next', 1, 'a'),
    ('  longword next', 4, 'long'),
    ('  short text  ', 300, '  short text  '),
    ('a' * 300, 300, 'a' * 300),
])
def test_public_search_uses_correct_bounded_prefix(query, limit, expected, arxiv_sdk):
    client = Mock()
    client.results.return_value = iter([])
    tool = ArxivTool(sch_engine=client, MAX_QUERY_LENGTH=limit)
    tool.execute(query, mode='search')
    client.results.assert_called_once()
    search = client.results.call_args.args[0]
    assert isinstance(search, arxiv_sdk.Search)
    assert search.query == 'abs:' + expected
    assert len(expected) <= limit
    assert expected.strip()
    assert search.max_results == 10
    assert search.sort_by == arxiv_sdk.SortCriterion.Relevance


@pytest.mark.parametrize('limit', [0, -1])
def test_nonpositive_config_behavior_is_not_redefined(limit):
    assert ArxivTool(MAX_QUERY_LENGTH=limit)._process_query('word') == ''

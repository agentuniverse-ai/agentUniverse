import pytest

from agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool import SemanticScholarTool


@pytest.mark.parametrize(
    "url",
    [
        "https://semanticscholar.org/paper/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa?utm_source=email",
        "https://www.semanticscholar.org/paper/title/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa#abstract",
        "https://semanticscholar.org/paper/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/",
    ],
)
def test_semantic_scholar_paper_url_ignores_query_fragment_and_trailing_slash(url):
    assert SemanticScholarTool._normalize_paper_id(url) == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def test_semantic_scholar_paper_url_still_rejects_non_paper_path():
    with pytest.raises(ValueError):
        SemanticScholarTool._normalize_paper_id("https://semanticscholar.org/author/123")

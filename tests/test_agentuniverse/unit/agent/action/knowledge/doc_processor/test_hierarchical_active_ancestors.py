"""Exercise heading ancestry and aggregation using the real splitter."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.hierarchical_regex_text_splitter import (
    HierarchicalRegexTextSplitter,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def make_splitter(**kwargs):
    """Configure four exact heading levels without an external summary service."""
    return HierarchicalRegexTextSplitter(
        hierarchical_index=[
            {"reg_exp": rf"^H{level}:.*", "need_summary": False}
            for level in range(4)
        ],
        **kwargs,
    )


@pytest.mark.parametrize("levels", [
    [0, 1, 2, 0, 2],
    [0, 1, 2, 3, 0, 3],
    [0, 1, 2, 3, 1, 3],
    [0, 1, 2, 0, 3, 2, 3],
    [0, 2],
    [0, 3],
    [1, 3],
    [3, 0, 3],
    [0, 1, 2, 3],
    [0, 1, 1, 2, 2],
    [0, 0, 1],
    [2, 3, 2, 3],
])
def test_heading_parent_and_aggregated_text_follow_active_ancestors(levels):
    """Skipped levels must not reconnect to a branch already closed by a heading."""
    headings = [f"H{level}: node-{index}" for index, level in enumerate(levels)]
    bodies = [f"body-{index}" for index in range(len(levels))]
    text = "\n".join(
        line for pair in zip(headings, bodies) for line in pair
    )
    original = Document(text=text, metadata={"source": "outline"})
    result = make_splitter().process_docs([original])
    assert len(result) == len(levels)
    assert len({doc.id for doc in result}) == len(result)

    # An outline stack is independent of the production level-slot algorithm.
    stack = []
    expected_lines = [[] for _ in levels]
    for index, level in enumerate(levels):
        while stack and levels[stack[-1]] >= level:
            stack.pop()
        parent = result[stack[-1]].id if stack else "root"
        assert result[index].metadata["hierarchical_parent"] == parent
        assert result[index].metadata["hierarchical_level"] == level
        assert result[index].metadata["hierarchical_info"] == headings[index]
        stack.append(index)
        for ancestor in stack:
            expected_lines[ancestor].extend([headings[index], bodies[index]])
    for doc, lines in zip(result, expected_lines):
        assert doc.text == "\n".join(lines)
    assert original.text == text
    assert original.metadata == {"source": "outline"}


def test_each_input_document_starts_with_an_empty_heading_stack():
    """A later document cannot inherit the earlier document's active ancestors."""
    result = make_splitter().process_docs([
        Document(text="H0: first\nH1: section\nold body"),
        Document(text="H2: standalone\nnew body"),
    ])
    assert result[2].metadata["hierarchical_parent"] == "root"
    assert "new body" not in result[0].text
    assert "new body" not in result[1].text


def test_merge_first_can_close_a_branch_across_document_boundaries():
    """Merged input follows the same outline even when a chapter starts in another doc."""
    result = make_splitter(merge_first=True).process_docs([
        Document(text="H0: old\nH1: old section\nold body"),
        Document(text="H0: new\nH2: child\nnew body"),
    ])
    assert result[3].metadata["hierarchical_parent"] == result[2].id
    assert result[0].text == "H0: old\nH1: old section\nold body"
    assert result[2].text == "H0: new\nH2: child\nnew body"


def test_repeated_heading_labels_still_have_distinct_parent_ids():
    """Equal heading text does not turn separate chapter instances into one node."""
    result = make_splitter().process_docs([
        Document(text="H0: repeated\nH1: old\nH0: repeated\nH2: new")
    ])
    assert result[0].id != result[2].id
    assert result[3].metadata["hierarchical_parent"] == result[2].id
    assert result[0].text == "H0: repeated\nH1: old"
    assert result[2].text == "H0: repeated\nH2: new"


def test_summary_inputs_do_not_include_text_from_a_closed_branch():
    """The hierarchy fix must protect summary inputs, not only parent metadata."""
    splitter = make_splitter()
    splitter.hierarchical_index[0]["need_summary"] = True
    agent = Mock()
    agent.agent_model = SimpleNamespace(profile={})
    agent.run.side_effect = lambda **kwargs: SimpleNamespace(
        output="summary:" + kwargs["input"]
    )
    with patch(
        "agentuniverse.agent.action.knowledge.doc_processor."
        "hierarchical_regex_text_splitter.AgentManager"
    ) as manager:
        manager.return_value.get_instance_obj.return_value = agent
        result = splitter.process_docs([
            Document(text="H0: old\nH1: old section\nH0: new\nH2: child\nnew body")
        ])
    assert [call.kwargs["input"] for call in agent.run.call_args_list] == [
        "H0: old\nH1: old section",
        "H0: new\nH2: child\nnew body",
    ]
    assert result[3].metadata["hierarchical_parent"] == result[2].id
    assert result[2].text == "summary:H0: new\nH2: child\nnew body"


def test_empty_input_keeps_existing_behavior():
    """An empty batch must not create synthetic heading nodes."""
    splitter = make_splitter()
    assert splitter.process_docs([]) == []


def test_chinese_chapter_transition_with_skipped_section():
    """Real chapter markers must not carry an old section into the next chapter."""
    splitter = HierarchicalRegexTextSplitter(hierarchical_index=[
        {"reg_exp": r"第[一二三]+章.*", "need_summary": False},
        {"reg_exp": r"第[一二三]+节.*", "need_summary": False},
        {"reg_exp": r"第[一二三]+条.*", "need_summary": False},
    ])
    result = splitter.process_docs([Document(
        text="第一章 总则\n第一节 适用范围\n旧内容\n第二章 职责\n第一条 责任\n新内容"
    )])
    assert len(result) == 4
    assert result[3].metadata["hierarchical_parent"] == result[2].id
    assert result[0].text == "第一章 总则\n第一节 适用范围\n旧内容"
    assert result[2].text == "第二章 职责\n第一条 责任\n新内容"


def test_overlapping_patterns_keep_first_match_precedence():
    """Ancestor cleanup must not change which configured heading pattern wins."""
    splitter = HierarchicalRegexTextSplitter(hierarchical_index=[
        {"reg_exp": r"^TITLE:.*", "need_summary": False},
        {"reg_exp": r"^(TITLE|ITEM):.*", "need_summary": False},
        {"reg_exp": r"^DETAIL:.*", "need_summary": False},
    ])
    result = splitter.process_docs([Document(
        text="TITLE: old\nITEM: section\nTITLE: new\nDETAIL: child"
    )])
    assert [doc.metadata["hierarchical_level"] for doc in result] == [0, 1, 0, 2]
    assert result[2].metadata["hierarchical_parent"] == "root"
    assert result[3].metadata["hierarchical_parent"] == result[2].id
    assert result[0].text == "TITLE: old\nITEM: section"

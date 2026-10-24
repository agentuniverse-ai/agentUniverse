"""Tests for supervision result parsing."""

import pytest

from agentuniverse.agent.template.supervision_agent_template import (
    SupervisionAgentTemplate,
)


def test_feedback_extraction_preserves_original_text_casing():
    template = SupervisionAgentTemplate()
    output = "Status: Review Complete\nFeedback: Keep APIClient and UserID names\n\nScore: 90"

    assert template._extract_feedback(output) == "Keep APIClient and UserID names"


@pytest.mark.parametrize(
    "output, expected",
    [
        # The verdict line mandated by the supervision prompt wins over any
        # prose elsewhere in the reply, including the rubric text that quotes
        # the very phrases the keyword fallback looks for.
        (
            "Score: 88\n\nNeeds Correction: false\n\nFeedback: 结构完整\n\n"
            "评估详情:\n- 目标符合度: 符合要求(36/40)",
            False,
        ),
        (
            "Score: 55\n\nNeeds Correction: true\n\nFeedback: 缺少输入验证\n\n"
            "评估详情:\n- 目标符合度: 符合要求(36/40)\n- 质量完整性: 不符合要求(12/30)",
            True,
        ),
        # A passing verdict must not be flipped by soft criticism in the
        # feedback text.
        (
            "Score: 85\n\nNeeds Correction: false\n\n"
            "Feedback: solid overall, wording needs improvement",
            False,
        ),
        # Formatting variants of the same field.
        ("**Needs Correction:** **false**\n\nScore: 90", False),
        ("Needs Correction：true\n\nScore: 20", True),
        ("needs_correction: TRUE\n\nScore: 30", True),
        # An echoed template placeholder is not a verdict.
        ("Needs Correction: [true/false]\n\nScore: 80\n\nFeedback: fine", False),
    ],
)
def test_explicit_verdict_line_decides_needs_correction(output, expected):
    assert SupervisionAgentTemplate()._extract_needs_correction(output) is expected


@pytest.mark.parametrize(
    "output, expected",
    [
        # Replies that omit the verdict line still have to be read correctly:
        # negated phrasings must not be swallowed by their positive substring.
        ("Score: 40\n\nFeedback: 需要修正边界处理", True),
        ("Score: 90\n\nFeedback: 无需修正", False),
        ("Score: 30\n\nFeedback: the result is not acceptable", True),
        ("Score: 30\n\nFeedback: the result is not satisfactory", True),
        ("Score: 30\n\nFeedback: does not meet the goal", True),
        ("Score: 90\n\nFeedback: acceptable", False),
        ("Score: 90\n\nFeedback: meets requirements", False),
        ("Score: 90\n\nFeedback: no correction required", False),
        ("Score: 90\n\nFeedback: no correction needed", False),
        ("Score: 30\n\nFeedback: 不符合要求", True),
        ("Score: 90\n\nFeedback: 符合要求", False),
        ("Score: 60\n\nFeedback: 不需要修正，但后续可优化", False),
        ("Score: 30\n\nFeedback: 需要修正；其余符合要求", True),
        # Nothing to go on.
        ("", False),
        (None, False),
    ],
)
def test_keyword_fallback_reads_negations_correctly(output, expected):
    assert SupervisionAgentTemplate()._extract_needs_correction(output) is expected


def test_parse_result_reports_the_verdict_the_model_gave():
    template = SupervisionAgentTemplate()
    result = template.parse_result(
        {
            "output": (
                "Score: 55\n\nNeeds Correction: true\n\nFeedback: 缺少输入验证\n\n"
                "评估详情:\n- 目标符合度: 符合要求(36/40)\n- 质量完整性: 不符合要求(12/30)"
            ),
            "checkpoint_index": 0,
        }
    )

    assert result["needs_correction"] is True
    assert result["score"] == 55
    assert result["feedback"] == "缺少输入验证"

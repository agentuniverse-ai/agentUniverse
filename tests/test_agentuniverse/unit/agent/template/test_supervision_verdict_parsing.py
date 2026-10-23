from agentuniverse.agent.template.supervision_agent_template import SupervisionAgentTemplate


def test_structured_verdict_wins_over_rubric_phrases():
    template = SupervisionAgentTemplate()

    assert template._extract_needs_correction(
        "Score: 55\n\nNeeds Correction: true\n\nFeedback: Meets requirements in one area"
    ) is True
    assert template._extract_needs_correction(
        "Score: 85\n\nNeeds Correction: false\n\nFeedback: Needs improvement in wording"
    ) is False


def test_structured_verdict_accepts_underscore_and_chinese_labels():
    template = SupervisionAgentTemplate()

    assert template._extract_needs_correction("needs_correction: TRUE") is True
    assert template._extract_needs_correction("需要修正：否") is False


def test_legacy_fallback_handles_negated_phrases_before_positive_substrings():
    template = SupervisionAgentTemplate()

    assert template._extract_needs_correction("the result is not acceptable") is True
    assert template._extract_needs_correction("no correction required") is False
    assert template._extract_needs_correction("不符合要求") is True
    assert template._extract_needs_correction("无需修正") is False

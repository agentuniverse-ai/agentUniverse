"""Tests for supervision result parsing."""

from agentuniverse.agent.template.supervision_agent_template import (
    SupervisionAgentTemplate,
)


def test_feedback_extraction_preserves_original_text_casing():
    template = SupervisionAgentTemplate()
    output = "Status: Review Complete\nFeedback: Keep APIClient and UserID names\n\nScore: 90"

    assert template._extract_feedback(output) == "Keep APIClient and UserID names"

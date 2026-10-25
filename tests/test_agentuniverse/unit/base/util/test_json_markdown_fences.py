"""JSON fence labels must not change the parsed tool input."""

import json

import pytest

from agentuniverse.base.util.common_util import parse_and_check_json_markdown, parse_json_markdown


@pytest.mark.parametrize("label", ["JSON", "Json", "jSoN", "json", ""])
def test_json_fence_preserves_tool_input(label):
    expected = {
        "input": "JSON must stay uppercase: 中文",
        "options": {"enabled": False, "limit": 0},
    }
    source = f"Result:\n```{label}\n{json.dumps(expected)}\n```\nDone."

    assert parse_and_check_json_markdown(source, ["input", "options"]) == expected


def test_json_fence_still_validates_required_keys():
    source = '```JSON\n{"input": "value"}\n```'

    with pytest.raises(Exception, match="Expected key `result`"):
        parse_and_check_json_markdown(source, ["result"])


def test_json_fence_supports_a_custom_parser():
    source = '```JSON\n{"input": "value"}\n```'

    assert parse_json_markdown(source, parser=json.loads) == {"input": "value"}


def test_plain_json_preserves_fence_text_inside_a_value():
    expected = {"input": "Literal ```JSON must stay uppercase"}

    assert parse_json_markdown(json.dumps(expected)) == expected

"""Pydantic compatibility contracts for the LLM output models."""

import subprocess
import sys
import warnings
from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic.warnings import PydanticDeprecationWarning

from agentuniverse.llm import llm_output
from agentuniverse.llm.llm_output import FunctionCall, LLMOutput, TokenUsage


def test_import_does_not_use_deprecated_pydantic_configuration():
    """Check model construction in a fresh interpreter, even after collection."""
    script = """
import warnings
from pydantic.warnings import PydanticDeprecationWarning

warnings.simplefilter("error", PydanticDeprecationWarning)
warnings.filterwarnings("error", message="Valid config keys have changed in V2", category=UserWarning)
import agentuniverse.llm.llm_output
"""
    result = subprocess.run(  # noqa: S603 - fixed script, current interpreter, no shell.
        [sys.executable, "-c", script],
        cwd=Path(llm_output.__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("field,value", [("name", "replacement"), ("arguments", {"query": "new"})])
def test_function_call_fields_remain_frozen(field, value):
    call = FunctionCall(name="search", arguments={"query": "original"})

    with pytest.raises(ValidationError) as assignment_error:
        setattr(call, field, value)
    assert assignment_error.value.errors()[0]["type"] == "frozen_instance"

    with pytest.raises(ValidationError) as deletion_error:
        delattr(call, field)
    assert deletion_error.value.errors()[0]["type"] == "frozen_instance"
    assert call.model_dump() == {"name": "search", "arguments": {"query": "original"}}


def test_function_call_preserves_shallow_freezing_and_independent_defaults():
    first = FunctionCall(name="first")
    second = FunctionCall(name="second")

    first.arguments["query"] = "example"

    assert first.arguments == {"query": "example"}
    assert second.arguments == {}
    assert first.arguments is not second.arguments


def test_function_call_schema_and_nested_output_round_trip():
    call = FunctionCall(name="search", arguments={"queries": ["one", "two"], "limit": 2})
    output = LLMOutput(type="tool_call", function_call=call, usage=TokenUsage(text_in=3, text_out=2))

    assert output.model_dump()["function_call"] == {
        "name": "search",
        "arguments": {"queries": ["one", "two"], "limit": 2},
    }
    assert LLMOutput.model_validate_json(output.model_dump_json()) == output
    schema = FunctionCall.model_json_schema()
    assert set(schema["properties"]) == {"name", "arguments"}
    assert schema["required"] == ["name"]


def test_token_usage_in_place_addition_preserves_identity_without_deprecations():
    counters = {
        "text_in": 1,
        "image_in": 2,
        "audio_in": 3,
        "cached_in": 4,
        "text_out": 5,
        "image_out": 6,
        "audio_out": 7,
        "cached_out": 8,
        "reasoning_out": 9,
    }
    usage = TokenUsage(**counters)
    original = usage
    increment = TokenUsage(**{field: value * 2 for field, value in counters.items()})
    increment_before = increment.model_dump()

    with warnings.catch_warnings():
        warnings.simplefilter("error", PydanticDeprecationWarning)
        usage += increment

    assert usage is original
    assert usage.model_dump() == {field: value * 3 for field, value in counters.items()}
    assert increment.model_dump() == increment_before
    assert usage.prompt_tokens == 30
    assert usage.completion_tokens == 105
    assert usage.total_tokens == 135


def test_token_usage_can_still_accumulate_itself():
    usage = TokenUsage(text_in=3, cached_in=2, reasoning_out=1)
    original = usage

    with warnings.catch_warnings():
        warnings.simplefilter("error", PydanticDeprecationWarning)
        usage += usage
        usage += TokenUsage()

    assert usage is original
    assert usage == TokenUsage(text_in=6, cached_in=4, reasoning_out=2)

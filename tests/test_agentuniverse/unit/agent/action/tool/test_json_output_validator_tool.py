# -*- coding:utf-8 -*-

from agentuniverse.agent.action.tool.common_tool.json_output_validator_tool import (
    JsonOutputValidatorTool,
)


def test_json_output_validator_accepts_fenced_json_and_types():
    result = JsonOutputValidatorTool().execute(
        text='```json\n{"answer": "ok", "score": 3}\n```',
        required_keys=["answer", "score"],
        type_expectations={"answer": "string", "score": "integer"},
    )

    assert result == {
        "valid": True,
        "issues": [],
        "data": {"answer": "ok", "score": 3},
    }


def test_json_output_validator_reports_missing_and_mismatched_fields():
    result = JsonOutputValidatorTool().execute(
        text='{"score": "high"}',
        required_keys=["answer", "score"],
        type_expectations={"score": "integer"},
    )

    assert result["valid"] is False
    assert result["issues"] == [
        {"code": "missing_key", "key": "answer"},
        {"code": "type_mismatch", "key": "score", "expected": "integer"},
    ]


def test_json_output_validator_rejects_invalid_or_non_object_json():
    invalid = JsonOutputValidatorTool().execute(text="not json")
    array = JsonOutputValidatorTool().execute(text="[1, 2]")

    assert invalid["issues"][0]["code"] == "invalid_json"
    assert array["issues"][0]["code"] == "expected_object"


def test_json_output_validator_rejects_non_json_numeric_constants():
    validator = JsonOutputValidatorTool()

    for constant in ("NaN", "Infinity", "-Infinity"):
        result = validator.execute(
            text=f'{{"score": {constant}}}',
            type_expectations={"score": "number"},
        )
        assert result["valid"] is False
        assert result["issues"][0]["code"] == "invalid_json"


def test_json_output_validator_accepts_finite_json_numbers():
    result = JsonOutputValidatorTool().execute(
        text='{"zero": 0, "integer": 7, "decimal": 1.25}',
        type_expectations={
            "zero": "number",
            "integer": "integer",
            "decimal": "number",
        },
    )

    assert result["valid"] is True

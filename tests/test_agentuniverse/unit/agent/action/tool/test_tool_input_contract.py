import asyncio

import pytest
from pydantic import BaseModel, Field, ValidationError

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class SearchArgs(BaseModel):
    query: str
    limit: int = Field(default=5, ge=1, le=20)


class TypedTool(Tool):
    name: str = "typed_tool"

    def execute(self, **kwargs):
        return kwargs


class AsyncTypedTool(TypedTool):
    async def async_execute(self, **kwargs):
        return kwargs


class LegacyTypedTool(Tool):
    name: str = "legacy_typed_tool"

    def execute(self, tool_input: ToolInput):
        return tool_input.to_dict()


def typed_tool(**kwargs):
    return TypedTool(input_keys=["query"], args_model=SearchArgs, **kwargs)


def test_run_applies_pydantic_coercion_and_defaults():
    result = Tool.run.__wrapped__(typed_tool(), query="agents", limit="3")

    assert result == {"query": "agents", "limit": 3}


def test_async_run_uses_the_same_input_contract():
    result = asyncio.run(
        Tool.async_run.__wrapped__(
            AsyncTypedTool(input_keys=["query"], args_model=SearchArgs),
            query="agents",
        )
    )

    assert result == {"query": "agents", "limit": 5}


def test_validation_error_is_preserved():
    with pytest.raises(ValidationError):
        Tool.run.__wrapped__(typed_tool(), query="agents", limit=0)


def test_invalid_args_model_has_an_actionable_error():
    tool = TypedTool(input_keys=["query"], args_model=dict)

    with pytest.raises(TypeError, match="Pydantic BaseModel subclass"):
        Tool.run.__wrapped__(tool, query="agents")


def test_typed_contract_supports_legacy_tool_input_signature():
    tool = LegacyTypedTool(input_keys=["query"], args_model=SearchArgs)

    result = Tool.run.__wrapped__(tool, query="agents", limit="2")

    assert result == {"query": "agents", "limit": 2}


def test_tools_without_args_model_keep_existing_behavior():
    tool = TypedTool(input_keys=["query"], args_model=None)

    result = Tool.run.__wrapped__(tool, query="agents", extra=True)

    assert result == {"query": "agents", "extra": True}

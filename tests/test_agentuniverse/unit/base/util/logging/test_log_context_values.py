"""Regression coverage for stringable non-JSON log context values."""
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import json
from pathlib import Path
from uuid import UUID

import loguru
import pytest

from agentuniverse.base.context.framework_context import FrameworkContext
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager
from agentuniverse.base.util.logging.general_logger import GeneralLogger, get_context_prefix


class Priority(Enum):
    HIGH = 1


@pytest.fixture(autouse=True)
def isolated_log_context():
    with FrameworkContext({"LOG_CONTEXT": {}}):
        yield


def context_fields(prefix):
    """Read the existing bracket-wrapped JSON-object log prefix."""
    return json.loads("{" + prefix[1:-1] + "}")


@pytest.mark.parametrize("value", [
    datetime(2026, 10, 19, 12, 30, tzinfo=timezone.utc),
    UUID("12345678-1234-5678-1234-567812345678"),
    Path("requests") / "input.json",
    Decimal("12.50"),
    Priority.HIGH,
])
def test_public_log_context_accepts_stringable_values(value):
    FrameworkContextManager().set_log_context("request_value", value)

    fields = context_fields(get_context_prefix())

    assert fields["request_value"] == str(value)


def test_nested_values_are_converted_without_replacing_the_container():
    value = {"files": [Path("input.json")], "request": {"id": UUID(int=1)}}
    FrameworkContextManager().set_log_context("request", value)

    fields = context_fields(get_context_prefix())

    assert fields["request"] == {
        "files": ["input.json"], "request": {"id": str(UUID(int=1))},
    }


def test_json_native_values_keep_their_types():
    value = {"count": 2, "ratio": 0.5, "ok": True, "missing": None,
             "tags": ["example", 3]}
    FrameworkContextManager().set_log_context("request", value)

    fields = context_fields(get_context_prefix())

    assert fields["request"] == value
    assert isinstance(fields["request"]["count"], int)
    assert fields["request"]["ok"] is True


def test_trace_metadata_is_preserved():
    expected = AuTraceManager().get_trace_dict()
    FrameworkContextManager().set_log_context("operation", "load")

    fields = context_fields(get_context_prefix())

    assert all(fields[key] == value for key, value in expected.items())
    assert fields["operation"] == "load"


def test_formatting_does_not_mutate_original_context_values():
    manager = FrameworkContextManager()
    value = {"path": Path("input.json")}
    manager.set_log_context("request", value)
    original = manager.get_context("LOG_CONTEXT")

    get_context_prefix()

    assert manager.get_context("LOG_CONTEXT") is original
    assert original["request"] is value
    assert isinstance(value["path"], Path)


@pytest.mark.parametrize("async_call", [False, True], ids=["sync", "async"])
def test_actual_loguru_sink_receives_message_and_context(async_call):
    records = []
    logger = GeneralLogger("context-values", "", "", "", "", add_handler=False)
    sink_id = loguru.logger.add(
        lambda message: records.append(message.record),
        filter=lambda record: record["extra"].get("source") == "context-values",
        format="{extra[context_prefix]} | {message}",
    )
    try:
        FrameworkContextManager().set_log_context("request_id", UUID(int=2))
        if async_call:
            asyncio.run(logger.ainfo("request {}", "completed"))
        else:
            logger.info("request {}", "completed")
    finally:
        loguru.logger.remove(sink_id)

    assert len(records) == 1
    assert records[0]["message"] == "request completed"
    assert records[0]["level"].name == "INFO"
    fields = context_fields(records[0]["extra"]["context_prefix"])
    assert fields["request_id"] == str(UUID(int=2))

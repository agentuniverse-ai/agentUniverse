"""Monitor serialization preserves useful data around unsupported values."""

import json

from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.util.monitor.monitor import Monitor


def test_filters_unsupported_fields_from_dicts_inside_lists():
    unsupported = object()
    source = {"results": [{"text": "answer", "runtime": unsupported}]}

    result = Monitor().serialize_obj(source)

    assert result == {"results": [{"text": "answer"}]}
    assert source == {"results": [{"text": "answer", "runtime": unsupported}]}
    assert source["results"][0]["runtime"] is unsupported


def test_filters_nested_lists_before_checking_serializability():
    unsupported = object()
    source = {
        "results": [
            [{"text": "answer", "runtime": unsupported}],
            [["kept", unsupported]],
        ]
    }

    assert Monitor().serialize_obj(source) == {"results": [[{"text": "answer"}], [["kept"]]]}
    assert source["results"][0][0]["runtime"] is unsupported
    assert source["results"][1][0][1] is unsupported


def test_drops_unsupported_list_items():
    source = [object(), "kept", lambda: None, {"not", "json"}, 1]

    assert Monitor().serialize_obj(source) == ["kept", 1]


def test_preserves_json_native_falsey_values():
    source = {"values": [None, False, 0, 0.0, "", [], {}]}

    assert Monitor().serialize_obj(source) == source


def test_trace_agent_invocation_writes_filtered_nested_data(tmp_path, monkeypatch):
    monitor = Monitor()
    monkeypatch.setattr(monitor, "activate", True)
    monkeypatch.setattr(monitor, "log_activate", False)
    monkeypatch.setattr(monitor, "dir", str(tmp_path))
    agent_input = {"results": [{"text": "answer", "runtime": object()}]}

    monitor.trace_agent_invocation("serializer", agent_input, OutputObject({"output": "done"}))

    log_files = list((tmp_path / "agent_invocation").glob("agent_serializer_*.jsonl"))
    assert len(log_files) == 1
    records = [json.loads(line) for line in log_files[0].read_text(encoding="utf-8").splitlines()]
    assert len(records) == 1
    assert records[0]["source"] == "serializer"
    assert records[0]["agent_input"] == {"results": [{"text": "answer"}]}
    assert records[0]["agent_output"] == {"output": "done"}

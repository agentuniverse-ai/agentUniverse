"""Tracing temperature metadata preserves configured values and precedence."""

from types import SimpleNamespace

import pytest

from agentuniverse.base.annotation import trace


def model_call(self, **kwargs):
    """A representative decorated LLM call signature; no provider is invoked."""


@pytest.mark.parametrize(
    "model,channel,call,expected",
    [
        (0.8, {"temperature": 0.4}, {"temperature": 0}, 0),
        (0.8, {"temperature": 0.4}, {"temperature": 0.2}, 0.2),
        (0.8, {"temperature": 0}, {}, 0),
        (0.8, {"temperature": 0.4}, {}, 0.4),
        (0, {}, {}, 0),
        (0.8, {}, {}, 0.8),
        (None, {}, {}, -1),
        (0.8, {"temperature": None}, {}, 0.8),
        (0.8, {"temperature": 0.4}, {"temperature": None}, 0.4),
    ],
)
def test_trace_temperature_precedence(monkeypatch, model, channel, call, expected):
    monkeypatch.setattr(trace, "get_caller_info", lambda: {"source": "test", "type": "agent"})
    instance = SimpleNamespace(name="model", channel_name="channel", temperature=model,
                               channel_model_config=channel)
    result = trace._get_llm_info(model_call, instance, **call)
    assert result[0] is instance
    assert result[1:3] == ("model", "channel")
    assert result[4] == {"temperature": expected}
    assert result[5] == {"source": "test", "type": "agent"}
    assert instance.temperature == model
    assert instance.channel_model_config == channel


@pytest.mark.parametrize("attributes,expected", [({"temperature": 0}, 0),
                                                ({"temperature": 0.6}, 0.6), ({}, -1)])
def test_trace_temperature_without_channel_configuration(monkeypatch, attributes, expected):
    monkeypatch.setattr(trace, "get_caller_info", lambda: {})
    assert trace._get_llm_info(model_call, SimpleNamespace(**attributes))[4] == {"temperature": expected}

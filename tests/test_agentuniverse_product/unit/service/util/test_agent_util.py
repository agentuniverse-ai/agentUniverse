import pytest

from agentuniverse_product.service.util import agent_util


class RecordingLogger:
    def __init__(self):
        self.warnings = []

    def warn(self, message):
        self.warnings.append(message)


@pytest.mark.parametrize("expected_exception", [KeyError("missing"), TypeError("invalid type"), ValueError("invalid value")])
def test_assemble_peer_planner_members_returns_empty_list_and_logs_expected_errors(
    monkeypatch, expected_exception
):
    logger = RecordingLogger()
    monkeypatch.setattr(agent_util, "LOGGER", logger)

    def raise_expected_error(planner, keys):
        raise expected_exception

    monkeypatch.setattr(agent_util, "dict_does_not_contain_keys", raise_expected_error)

    result = agent_util.assemble_peer_planner_members({}, object())

    assert result == []
    assert len(logger.warnings) == 1
    assert "falling back to []" in logger.warnings[0]
    assert str(expected_exception) in logger.warnings[0]


def test_assemble_peer_planner_members_propagates_unexpected_attribute_error(monkeypatch):
    monkeypatch.setattr(agent_util, "dict_does_not_contain_keys", lambda planner, keys: True)

    class BrokenAgentModel:
        @property
        def profile(self):
            raise AttributeError

    with pytest.raises(AttributeError):
        agent_util.assemble_peer_planner_members({}, BrokenAgentModel())


def test_assemble_peer_planner_members_assembles_normal_configuration(monkeypatch):
    planner = {
        "planning": "planning-agent",
        "executing": "executing-agent",
        "expressing": "expressing-agent",
        "reviewing": "reviewing-agent",
    }
    assembled = object()
    calls = []

    monkeypatch.setattr(agent_util, "dict_does_not_contain_keys", lambda planner, keys: False)

    def assemble(planner_data, member_keys):
        calls.append((planner_data, member_keys))
        return assembled

    monkeypatch.setattr(agent_util, "assemble_planner_members", assemble)

    result = agent_util.assemble_peer_planner_members(planner, object())

    assert result is assembled
    assert calls == [(planner, ["planning", "executing", "expressing", "reviewing"])]

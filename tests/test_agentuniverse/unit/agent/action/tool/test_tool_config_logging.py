import logging

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.toolkit.toolkit import Toolkit


class DummyTool(Tool):
    def execute(self, **kwargs):
        return kwargs


class FailingConfig:
    @property
    def value(self):
        raise RuntimeError("invalid configuration")


class ComponentConfig:
    configer = FailingConfig()
    name = "demo"
    description = "demo component"
    tool_type = None
    input_keys = []
    tracing = None
    include = []


def test_tool_configuration_failure_uses_logging_without_stdout(caplog, capsys):
    with caplog.at_level(logging.ERROR):
        DummyTool().initialize_by_component_configer(ComponentConfig())

    assert capsys.readouterr().out == ""
    assert "Tool configuration initialization failed" in caplog.text


def test_toolkit_configuration_failure_uses_logging_without_stdout(caplog, capsys):
    with caplog.at_level(logging.ERROR):
        Toolkit().initialize_by_component_configer(ComponentConfig())

    assert capsys.readouterr().out == ""
    assert "Toolkit configuration initialization failed" in caplog.text

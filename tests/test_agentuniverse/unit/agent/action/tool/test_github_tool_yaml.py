"""`github_tool.yaml` must be registrable like every other shipped tool.

The framework registers components by scanning `*.yaml` under the package path
and asking each file what component it is:

    for config_file in path.rglob('*.yaml'):
        component_configer = ComponentConfiger().load_by_configer(configer)
        component_config_type = component_configer.get_component_config_type()
        if component_config_type == component_enum.value:
            component_configer_list.append(component_configer)

`get_component_config_type()` reads `metadata.type` (or falls back to the path
containing `prompt`). The shipped `github_tool.yaml` had no `metadata` block at
all -- it used `class_path`, which component YAMLs never read -- so it returned
`None` and was silently skipped. `GitHubTool` therefore existed but was not
reachable through `ToolManager`, while all six of its sibling tool YAMLs
registered normally.

    github_tool.yaml       -> config_type = None      <- skipped
    email_document_tool.yaml -> config_type = TOOL
    pdf_tool.yaml          -> config_type = TOOL
    powerpoint_tool.yaml   -> config_type = TOOL
    secure_archive_tool.yaml -> config_type = TOOL
    word_document_tool.yaml -> config_type = TOOL
    yahoo_finance_tool.yaml -> config_type = TOOL
"""

import os
import warnings

import pytest

from agentuniverse.agent.action.tool.common_tool import github_tool as github_module
from agentuniverse.agent.action.tool.common_tool.github_tool import GitHubTool
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.component_configer.configers.tool_configer import (
    ToolConfiger,
)
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(github_module.__file__), "github_tool.yaml")


@pytest.fixture(scope="module")
def component():
    return ComponentConfiger().load_by_configer(Configer(YAML_PATH).load())


def test_the_yaml_resolves_a_component_type(component):
    """`None` means the registrar skips the file without a word."""
    assert component.get_component_config_type() == ComponentEnum.TOOL.value


def test_the_yaml_names_the_real_class(component):
    assert component.metadata_module == (
        "agentuniverse.agent.action.tool.common_tool.github_tool"
    )
    assert component.metadata_class == "GitHubTool"


def test_the_named_class_exists_and_is_a_tool():
    assert issubclass(GitHubTool, Tool)


def test_the_tool_registers_and_is_retrievable_by_name():
    configer = ToolConfiger().load_by_configer(Configer(YAML_PATH).load())
    app = AppConfiger()
    app.tool_configer_map = {configer.name: configer}
    ApplicationConfigManager().app_configer = app

    tool = ToolManager().get_instance_obj(configer.name)

    assert isinstance(tool, GitHubTool)
    assert tool.name == "github_tool"


def test_the_declared_input_keys_match_execute():
    """The YAML tells an agent which arguments exist; keep it honest."""
    import inspect

    configer = ToolConfiger().load_by_configer(Configer(YAML_PATH).load())
    declared = set(configer.input_keys or [])
    accepted = set(inspect.signature(GitHubTool.execute).parameters) - {"self"}

    assert declared, "input_keys must not be empty"
    assert declared <= accepted, f"declared but not accepted: {declared - accepted}"


def test_no_sibling_tool_yaml_is_silently_unregisterable():
    """The whole directory: every yaml must resolve to a component type."""
    from pathlib import Path

    directory = Path(os.path.dirname(github_module.__file__))
    unregisterable = []
    for path in sorted(directory.glob("*.yaml")):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            loaded = ComponentConfiger().load_by_configer(Configer(str(path)).load())
        if loaded.get_component_config_type() != ComponentEnum.TOOL.value:
            unregisterable.append(path.name)

    assert unregisterable == []

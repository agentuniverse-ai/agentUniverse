"""Malformed component YAML should identify its source and invalid structure."""

import pytest

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer


@pytest.mark.parametrize("content", ["- name: example\n", "private-config-value\n", "42\n"])
@pytest.mark.parametrize("loader", [ComponentConfiger, ToolConfiger])
def test_non_mapping_yaml_root_reports_source(tmp_path, content, loader):
    path = tmp_path / "broken_component.yaml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError) as caught:
        loader(Configer(str(path)).load()).load()

    message = str(caught.value)
    assert str(path) in message
    assert "root" in message
    assert "mapping" in message
    assert "private-config-value" not in message


@pytest.mark.parametrize("metadata", ["private-config-value", ["TOOL"], 42, True, [], False, 0, ""])
def test_non_mapping_metadata_reports_field_before_loading_attributes(tmp_path, metadata):
    path = tmp_path / "broken_metadata.yaml"
    configer = Configer(str(path))
    configer.value = {"name": "example", "metadata": metadata}
    component = ComponentConfiger(configer)

    with pytest.raises(ValueError) as caught:
        component.load()

    message = str(caught.value)
    assert str(path) in message
    assert "metadata" in message
    assert "mapping" in message
    assert "private-config-value" not in message
    assert not hasattr(component, "name")


def test_in_memory_payload_reports_its_structure():
    configer = Configer()
    configer.value = ["example"]
    with pytest.raises(ValueError, match="<in-memory>.*root.*mapping"):
        ComponentConfiger(configer).load()


def test_valid_component_metadata_keeps_dynamic_attributes():
    configer = Configer()
    configer.value = {
        "name": "example",
        "timeout": 30,
        "metadata": {"type": "TOOL", "module": "example.tools", "class": "ExampleTool"},
    }

    component = ToolConfiger(configer).load()

    assert component.name == "example"
    assert component.timeout == 30
    assert component.metadata_type == "TOOL"
    assert component.metadata_module == "example.tools"
    assert component.metadata_class == "ExampleTool"


@pytest.mark.parametrize("metadata", [None, {}])
def test_prompt_without_metadata_keeps_path_inference(tmp_path, metadata):
    path = tmp_path / "prompt" / "answer.yaml"
    path.parent.mkdir()
    configer = Configer(str(path))
    configer.value = {"metadata": metadata}

    component = PromptConfiger(configer).load()

    assert component.metadata_type == "PROMPT"
    assert component.metadata_class == "Prompt"
    assert component.metadata_version == "prompt.answer"


def test_legacy_meta_class_is_still_accepted():
    configer = Configer()
    configer.value = {"meta_class": "example.tools.ExampleTool"}
    assert ComponentConfiger(configer).load().meta_class == "example.tools.ExampleTool"

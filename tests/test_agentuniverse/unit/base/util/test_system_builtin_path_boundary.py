from types import SimpleNamespace

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.system_util import is_system_builtin


def test_system_builtin_check_requires_path_component_boundaries():
    component = SimpleNamespace(
        component_type=ComponentEnum.LLM,
        component_config_path="/tmp/not-agentuniverse/llm/default/model.yaml",
    )

    assert is_system_builtin(component) is False


def test_system_builtin_check_accepts_actual_default_component_path():
    component = SimpleNamespace(
        component_type=ComponentEnum.LLM,
        component_config_path="/tmp/agentuniverse/llm/default/model.yaml",
    )

    assert is_system_builtin(component) is True

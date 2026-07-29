from types import SimpleNamespace

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


def test_unregister_removes_default_alias_for_same_component():
    manager = ComponentManagerBase(ComponentEnum.TOOL)
    component = SimpleNamespace(default_symbol=True)
    component_code = "test_app.tool.default_tool"
    manager.register(component_code, component)

    manager.unregister(component_code)

    assert manager.get_default_instance() is None
    assert manager.get_instance_name_list() == []


def test_unregister_non_default_component_preserves_default_alias():
    manager = ComponentManagerBase(ComponentEnum.TOOL)
    default_component = SimpleNamespace(default_symbol=True)
    other_component = SimpleNamespace(default_symbol=False)
    manager.register("test_app.tool.default_tool", default_component)
    manager.register("test_app.tool.other_tool", other_component)

    manager.unregister("test_app.tool.other_tool")

    assert manager.get_default_instance() is default_component

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class ExampleComponent(ComponentBase):
    component_type: ComponentEnum = ComponentEnum.DEFAULT


def test_component_base_preserves_name():
    component = ExampleComponent(name="example")

    assert component.name == "example"
    assert component.model_dump()["name"] == "example"

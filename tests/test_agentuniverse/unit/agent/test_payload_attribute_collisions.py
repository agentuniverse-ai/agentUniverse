"""Payload fields must stay data when their names collide with object APIs."""

import json

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.action.tool.tool import ToolInput

WRAPPERS = [
    (InputObject, "_InputObject__params"),
    (OutputObject, "_OutputObject__params"),
    (ToolInput, "_ToolInput__origin_params"),
]


@pytest.mark.parametrize("wrapper,storage", WRAPPERS)
@pytest.mark.parametrize("key", ["get_data", "to_dict", "to_json_str"])
def test_constructor_keeps_api_methods_callable(wrapper, storage, key):
    payload = {key: "payload value", "ordinary": "normal value"}
    obj = wrapper(payload)
    assert obj.get_data(key) == "payload value"
    assert obj.to_dict() == payload
    assert json.loads(obj.to_json_str()) == payload
    assert obj.ordinary == "normal value"


@pytest.mark.parametrize("wrapper,storage", WRAPPERS)
def test_payload_cannot_replace_backing_mapping(wrapper, storage):
    payload = {storage: {"unrelated": "not the backing dictionary"}, "ordinary": 7}
    obj = wrapper(payload)
    assert obj.to_dict() == payload
    assert obj.get_data(storage) == payload[storage]
    assert json.loads(obj.to_json_str()) == payload


@pytest.mark.parametrize("wrapper,storage", [WRAPPERS[0], WRAPPERS[2]])
@pytest.mark.parametrize("key", ["get_data", "to_dict", "to_json_str", "add_data", "storage"])
def test_add_data_does_not_replace_api_or_backing_mapping(wrapper, storage, key):
    if key == "storage":
        key = storage
    obj = wrapper({"ordinary": "original"})
    obj.add_data(key, {"nested": "payload value"})
    obj.add_data("ordinary", "updated")
    assert obj.get_data(key) == {"nested": "payload value"}
    assert obj.to_dict() == {"ordinary": "updated", key: {"nested": "payload value"}}
    assert json.loads(obj.to_json_str()) == obj.to_dict()
    assert obj.ordinary == "updated"


@pytest.mark.parametrize("wrapper,storage", WRAPPERS)
def test_subclass_methods_are_preserved(wrapper, storage):
    class Extended(wrapper):
        def custom_operation(self):
            return "method result"

    obj = Extended({"custom_operation": "payload value"})
    assert obj.custom_operation() == "method result"
    assert obj.get_data("custom_operation") == "payload value"


@pytest.mark.parametrize("wrapper,storage", WRAPPERS)
def test_non_string_mapping_keys_still_work(wrapper, storage):
    obj = wrapper({1: "numeric key", "ordinary": "attribute value"})
    assert obj.get_data(1) == "numeric key"
    assert obj.to_dict()[1] == "numeric key"
    assert obj.ordinary == "attribute value"


@pytest.mark.parametrize("wrapper,storage", WRAPPERS)
def test_ordinary_attribute_projection_is_preserved(wrapper, storage):
    obj = wrapper({"name": "payload", "_custom": "underscore value"})
    assert obj.name == "payload"
    assert obj._custom == "underscore value"

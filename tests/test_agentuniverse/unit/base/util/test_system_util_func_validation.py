import pytest

from agentuniverse.base.util.system_util import process_yaml_func


class Extension:
    def get_value(self):
        return "resolved"


def test_func_expression_requires_extension_instance():
    with pytest.raises(ValueError, match="yaml_func_extension.py is required"):
        process_yaml_func("@FUNC(get_value())", None)


def test_func_expression_rejects_attribute_chain():
    with pytest.raises(ValueError, match="simple function name"):
        process_yaml_func("@FUNC(config.get_value())", Extension())


def test_func_expression_still_resolves_simple_method():
    assert process_yaml_func("@FUNC(get_value())", Extension()) == "resolved"

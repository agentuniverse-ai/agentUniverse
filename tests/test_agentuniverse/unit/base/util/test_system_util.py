import pytest

from agentuniverse.base.util.system_util import (
    process_dict_with_funcs,
    process_yaml_func,
)


def test_process_yaml_func_requires_extension_for_function_expression():
    with pytest.raises(ValueError, match="yaml_func_extension.py is required"):
        process_yaml_func('@FUNC(load_secret("api_key"))', None)


def test_process_dict_with_funcs_rejects_nested_unresolved_expression():
    config = {"provider": {"api_key": '@FUNC(load_secret("api_key"))'}}

    with pytest.raises(ValueError, match="yaml_func_extension.py is required"):
        process_dict_with_funcs(config, None)


def test_plain_config_does_not_require_extension():
    config = {"provider": {"name": "demo"}}

    assert process_dict_with_funcs(config, None) == config
    assert process_yaml_func("literal-value", None) == "literal-value"

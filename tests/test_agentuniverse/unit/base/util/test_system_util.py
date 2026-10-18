import pytest

from agentuniverse.base.util.system_util import (
    process_dict_with_funcs,
    process_yaml_func,
)


def test_process_yaml_func_requires_extension():
    with pytest.raises(ValueError, match=r"yaml_func_extension\.py is required"):
        process_yaml_func('@FUNC(load_api_key("openai"))', None)


def test_process_dict_with_funcs_requires_extension_for_nested_values():
    config = {"llm": {"api_key": '@FUNC(load_api_key("openai"))'}}

    with pytest.raises(ValueError, match=r"yaml_func_extension\.py is required"):
        process_dict_with_funcs(config, None)


def test_process_dict_with_funcs_preserves_plain_mapping_without_extension():
    config = {"llm": {"api_key": "literal-key"}}

    assert process_dict_with_funcs(config, None) is config

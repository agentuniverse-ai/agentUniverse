# -*- coding:utf-8 -*-

from agentuniverse.base.util.system_util import process_dict_with_funcs


class _YamlFunctions:
    def secret(self, name):
        return f"resolved:{name}"


def test_process_dict_with_funcs_resolves_expressions_inside_lists_and_tuples():
    config = {
        "credentials": [
            "@FUNC(secret('primary'))",
            {"fallback": "@FUNC(secret('fallback'))"},
            ("plain", "@FUNC(secret('tuple'))"),
        ],
        "unchanged": "literal",
    }

    result = process_dict_with_funcs(config, _YamlFunctions())

    assert result == {
        "credentials": [
            "resolved:primary",
            {"fallback": "resolved:fallback"},
            ("plain", "resolved:tuple"),
        ],
        "unchanged": "literal",
    }
    assert config["credentials"][0] == "@FUNC(secret('primary'))"

from agentuniverse.base.util.system_util import process_dict_with_funcs


class _YamlFuncExtension:
    @staticmethod
    def load_api_key(model_name):
        return f"key-for-{model_name}"


def test_process_dict_with_funcs_resolves_expressions_inside_nested_lists():
    config = {
        "models": [
            "@FUNC(load_api_key(\"qwen\"))",
            {"fallback": ["@FUNC(load_api_key(model_name=\"glm\"))"]},
        ],
        "literal": 7,
    }

    processed = process_dict_with_funcs(config, _YamlFuncExtension())

    assert processed == {
        "models": [
            "key-for-qwen",
            {"fallback": ["key-for-glm"]},
        ],
        "literal": 7,
    }

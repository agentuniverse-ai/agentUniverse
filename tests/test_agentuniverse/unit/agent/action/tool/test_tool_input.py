from agentuniverse.agent.action.tool.tool import ToolInput


def test_tool_input_copies_constructor_params():
    params = {"query": "original"}
    tool_input = ToolInput(params)

    params["query"] = "changed externally"

    assert tool_input.get_data("query") == "original"


def test_tool_input_to_dict_returns_independent_mapping():
    tool_input = ToolInput({"query": "original"})

    exported = tool_input.to_dict()
    exported["query"] = "changed externally"

    assert tool_input.get_data("query") == "original"

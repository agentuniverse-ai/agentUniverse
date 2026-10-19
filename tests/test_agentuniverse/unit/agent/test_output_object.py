from agentuniverse.agent.output_object import OutputObject


def test_output_object_copies_constructor_params():
    params = {"output": "original"}
    output_object = OutputObject(params)

    params["output"] = "changed externally"

    assert output_object.get_data("output") == "original"


def test_to_dict_returns_an_independent_mapping():
    output_object = OutputObject({"output": "original"})

    exported = output_object.to_dict()
    exported["output"] = "changed externally"

    assert output_object.get_data("output") == "original"

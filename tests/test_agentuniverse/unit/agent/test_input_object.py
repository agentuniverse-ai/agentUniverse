from agentuniverse.agent.input_object import InputObject


def test_input_object_copies_constructor_params():
    """Verify InputObject copies constructor params to isolate external changes."""
    params = {"input": "original"}
    input_object = InputObject(params)

    params["input"] = "changed externally"

    assert input_object.get_data("input") == "original"


def test_to_dict_returns_an_independent_mapping():
    """Verify to_dict returns a mapping independent from the InputObject data."""
    input_object = InputObject({"input": "original"})

    exported = input_object.to_dict()
    exported["input"] = "changed externally"

    assert input_object.get_data("input") == "original"

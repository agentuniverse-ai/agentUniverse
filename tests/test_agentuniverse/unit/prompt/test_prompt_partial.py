import pytest

from agentuniverse.prompt.prompt import Prompt


def make_prompt() -> Prompt:
    return Prompt(
        prompt_template="{product}: Hello {name} from {locale}",
        input_variables=["product", "name", "locale"],
    )


def test_partial_returns_an_independent_prompt():
    prompt = make_prompt()

    bound = prompt.partial(product="agentUniverse", locale="Shanghai")

    assert prompt.partial_variables == {}
    assert prompt.input_variables == ["product", "name", "locale"]
    assert bound.input_variables == ["name"]
    assert bound.format(name="Ada") == "agentUniverse: Hello Ada from Shanghai"


def test_partial_bindings_can_be_chained_and_rebound():
    prompt = make_prompt().partial(product="old").partial(product="new")

    prompt = prompt.partial(locale="Hangzhou")

    assert prompt.input_variables == ["name"]
    assert prompt.format(name="Lin") == "new: Hello Lin from Hangzhou"


def test_callable_partial_is_resolved_at_format_time():
    prompt = make_prompt().partial(
        product="agentUniverse",
        locale=lambda: "runtime locale",
    )

    assert prompt.format(name="Ada") == ("agentUniverse: Hello Ada from runtime locale")


def test_unknown_partial_variable_is_rejected():
    with pytest.raises(ValueError, match="not present.*missing"):
        make_prompt().partial(missing="value")


def test_as_langchain_preserves_partial_variables():
    prompt = make_prompt().partial(product="agentUniverse")

    langchain_prompt = prompt.as_langchain()

    assert langchain_prompt.partial_variables == {"product": "agentUniverse"}
    assert langchain_prompt.input_variables == ["locale", "name"]

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.llm import LLM


class ConfigurableLLM(LLM):
    """A minimal LLM subclass used to exercise configuration merging."""

    def _call(self, *args, **kwargs):
        """Stub synchronous completion call that always returns None."""
        return None

    async def _acall(self, *args, **kwargs):
        """Stub asynchronous completion call that always returns None."""
        return None

    def get_num_tokens(self, text: str) -> int:
        """Return the number of tokens as the character length of the text.

        Args:
            text: The input text to count.

        Returns:
            The length of the text in characters.
        """
        return len(text)


def _llm_configer(**overrides) -> LLMConfiger:
    """Build an LLMConfiger loaded from a base LLM config plus overrides.

    Args:
        **overrides: Additional config keys merged over the base config.

    Returns:
        An LLMConfiger populated with the merged configuration.
    """
    configer = Configer()
    configer.value = {
        "name": "configured_llm",
        "model_name": "gpt-4o",
        **overrides,
    }
    return LLMConfiger().load_by_configer(configer)


def test_initialize_preserves_explicit_falsy_values():
    """Verify config initialization keeps explicit falsy option values."""
    llm = ConfigurableLLM(
        model_name="initial-model",
        temperature=0.8,
        max_retries=3,
        streaming=True,
        ext_info={"initial": True},
    )

    llm.initialize_by_component_configer(
        _llm_configer(
            temperature=0.0,
            max_retries=0,
            streaming=False,
            ext_info={},
        )
    )

    assert llm.temperature == 0.0
    assert llm.max_retries == 0
    assert llm.streaming is False
    assert llm.ext_info == {}


def test_agent_model_overrides_preserve_explicit_falsy_values():
    """Verify agent model overrides keep explicit falsy option values."""
    llm = ConfigurableLLM(
        model_name="gpt-4o",
        temperature=0.8,
        max_retries=3,
        streaming=True,
    )

    configured = llm.set_by_agent_model(
        temperature=0.0,
        max_retries=0,
        streaming=False,
    )

    assert configured.temperature == 0.0
    assert configured.max_retries == 0
    assert configured.streaming is False
    assert llm.temperature == 0.8
    assert llm.max_retries == 3
    assert llm.streaming is True


def test_agent_model_none_values_do_not_override_defaults():
    """Verify None agent model overrides leave existing option values intact."""
    llm = ConfigurableLLM(
        model_name="gpt-4o",
        temperature=0.8,
        max_retries=3,
        streaming=True,
    )

    configured = llm.set_by_agent_model(
        temperature=None,
        max_retries=None,
        streaming=None,
    )

    assert configured.temperature == 0.8
    assert configured.max_retries == 3
    assert configured.streaming is True

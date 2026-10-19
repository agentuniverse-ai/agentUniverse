from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.llm import LLM


class ConfigurableLLM(LLM):
    def _call(self, *args, **kwargs):
        return None

    async def _acall(self, *args, **kwargs):
        return None

    def get_num_tokens(self, text: str) -> int:
        return len(text)


def _llm_configer(**overrides) -> LLMConfiger:
    configer = Configer()
    configer.value = {
        "name": "configured_llm",
        "model_name": "gpt-4o",
        **overrides,
    }
    return LLMConfiger().load_by_configer(configer)


def test_initialize_preserves_explicit_falsy_values():
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

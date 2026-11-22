from pathlib import Path

import yaml

from agentuniverse.llm.default import default_openai_llm
from agentuniverse.llm.langchain_instance import LangchainOpenAI
from agentuniverse.llm.openai_llm import OpenAILLM
from agentuniverse.llm.openai_style_langchain_instance import LangchainOpenAIStyleInstance
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Shut down on the OpenAI API (https://platform.openai.com/docs/deprecations):
# gpt-3.5-turbo, gpt-4 and gpt-4-turbo on 2026-10-23.
SHUT_DOWN = {"gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"}


def test_default_openai_llm_yaml_names_a_served_model():
    path = Path(default_openai_llm.__file__).with_suffix(".yaml")
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert config["model_name"] not in SHUT_DOWN


def test_langchain_fallback_model_is_served():
    instance = LangchainOpenAI(OpenAILLM(name="test", openai_api_key="test-key"))
    assert instance.model_name not in SHUT_DOWN


def test_openai_style_langchain_fallback_model_is_served():
    instance = LangchainOpenAIStyleInstance(OpenAIStyleLLM(name="test", api_key="test-key"))
    assert instance.model_name not in SHUT_DOWN

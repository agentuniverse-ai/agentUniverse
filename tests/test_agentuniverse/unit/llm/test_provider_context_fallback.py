"""Provider model tables must not be hidden by the OpenAI transport fallback."""

import importlib

import pytest
from langchain_core.prompts import PromptTemplate

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.util import prompt_util
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

PROVIDERS = [
    ("gemini_openai_style_llm", "GeminiOpenAIStyleLLM", "gemini-2.0-flash", 1048576),
    ("kimi_openai_style_llm", "KIMIOpenAIStyleLLM", "moonshot-v1-128k", 128000),
    ("baichuan_openai_style_llm", "BAICHUANOpenAIStyleLLM", "Baichuan3-Turbo-128k", 128000),
    ("qwen_openai_style_llm", "QWenOpenAIStyleLLM", "qwen-plus", 131072),
]


@pytest.fixture(params=PROVIDERS, ids=[entry[0] for entry in PROVIDERS])
def provider(request):
    module, class_name, model_name, expected = request.param
    if module.startswith("qwen"):
        pytest.importorskip("dashscope")
    cls = getattr(importlib.import_module("agentuniverse.llm.default." + module), class_name)
    return cls, model_name, expected


def configure(cls, model_name, **options):
    configer = Configer()
    configer.value = {"name": "offline", "model_name": model_name, "max_tokens": 1024, **options}
    return cls().initialize_by_component_configer(LLMConfiger().load_by_configer(configer))


def test_provider_table_is_used_without_explicit_limit(provider):
    cls, model_name, expected = provider
    assert configure(cls, model_name).max_context_length() == expected


def test_every_existing_provider_table_entry_is_reachable(provider):
    cls, _, _ = provider
    module = importlib.import_module(cls.__module__)
    table_names = {
        "GeminiOpenAIStyleLLM": "GEMINI_MAX_CONTEXT_LENGTH",
        "KIMIOpenAIStyleLLM": "KIMI_Max_CONTEXT_LENGTH",
        "BAICHUANOpenAIStyleLLM": "BAICHUAN_Max_CONTEXT_LENGTH",
        "QWenOpenAIStyleLLM": "QWen_Max_CONTEXT_LENGTH",
    }
    for model_name, expected in getattr(module, table_names[cls.__name__]).items():
        assert configure(cls, model_name).max_context_length() == expected


@pytest.mark.parametrize("model_name", ["unknown-model", "gpt-4o"])
def test_provider_unknown_fallback_does_not_use_openai_table(provider, model_name):
    cls, _, _ = provider
    assert configure(cls, model_name).max_context_length() == 8000


@pytest.mark.parametrize("known_model", [False, True])
@pytest.mark.parametrize("limit", [2000, 2000000])
def test_explicit_yaml_limit_wins(provider, known_model, limit):
    cls, model_name, _ = provider
    model = configure(cls, model_name if known_model else "custom-model", max_context_length=limit)
    assert model.max_context_length() == limit
    copied = model.set_by_agent_model(max_context_length=9000)
    assert copied.max_context_length() == 9000
    assert model.max_context_length() == limit


@pytest.mark.parametrize("max_tokens", [1024, 8192])
def test_prompt_processing_keeps_valid_provider_background(monkeypatch, provider, max_tokens):
    cls, model_name, _ = provider
    model = configure(cls, model_name, max_tokens=max_tokens)
    # Deterministic tokenizer avoids network/downloads; real prompt budgeting and
    # truncation still run, with a valid prompt larger than the wrong 4096 limit.
    monkeypatch.setattr(cls, "get_num_tokens", lambda self, text: len(text))
    monkeypatch.setattr(type(prompt_util.LLMManager()), "get_instance_obj", lambda *a, **kw: None)
    original = "x" * 5000
    inputs = {"background": original}
    prompt_util.process_llm_token(
        model, PromptTemplate.from_template("{background}"), {"llm_model": {}}, inputs
    )
    assert inputs["background"] == original


def test_prompt_processing_still_enforces_explicit_limit(monkeypatch, provider):
    cls, model_name, _ = provider
    model = configure(cls, model_name, max_context_length=6000)
    monkeypatch.setattr(cls, "get_num_tokens", lambda self, text: len(text))
    monkeypatch.setattr(type(prompt_util.LLMManager()), "get_instance_obj", lambda *a, **kw: None)
    inputs = {"background": "x" * 6500}
    prompt_util.process_llm_token(
        model, PromptTemplate.from_template("{background}"), {"llm_model": {}}, inputs
    )
    assert inputs["background"] == "x" * (6000 - 1024)


@pytest.mark.parametrize("model_name,expected", [("gpt-4o", 128000), ("unknown-model", 4096)])
def test_generic_openai_transport_fallback_is_unchanged(model_name, expected):
    assert configure(OpenAIStyleLLM, model_name).max_context_length() == expected

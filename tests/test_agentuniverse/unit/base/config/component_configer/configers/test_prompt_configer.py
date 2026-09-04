# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_prompt_configer.py

"""Unit tests for the PromptConfiger."""

from types import SimpleNamespace

from agentuniverse.base.config.component_configer.configers.prompt_configer import \
    PromptConfiger


class TestPromptConfiger:
    """Test prompt configuration loading."""

    def test_defaults(self):
        configer = PromptConfiger()
        assert configer.metadata_version is None

    def test_load_with_metadata_version(self):
        configer = PromptConfiger()
        value = {"metadata": {"type": "prompt", "version": "v2",
                              "module": "mod.prompt", "class": "MyPrompt"}}
        returned = configer.load_by_configer(SimpleNamespace(value=value,
                                                             path="x.yaml"))
        assert returned is configer
        assert configer.metadata_version == "v2"
        assert configer.metadata_module == "mod.prompt"
        assert configer.metadata_class == "MyPrompt"

    def test_load_without_metadata_derives_version_from_path(self):
        configer = PromptConfiger()
        configer.load_by_configer(SimpleNamespace(
            value={}, path="/tmp/prompts/hello.yaml"))
        assert configer.metadata_version == "prompts.hello"
        assert configer.metadata_module == "agentuniverse.prompt.prompt"
        assert configer.metadata_class == "Prompt"

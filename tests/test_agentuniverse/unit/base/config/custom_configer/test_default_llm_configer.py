# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_default_llm_configer.py

"""Unit tests for the DefaultLLMConfiger singleton."""

import os
import tempfile

from agentuniverse.base.config.custom_configer.default_llm_configer import     DefaultLLMConfiger


def test_loads_default_llm_from_toml():
    with tempfile.NamedTemporaryFile("w", suffix=".toml",
                                     delete=False) as f:
        f.write("[DEFAULT]\ndefault_llm = \"gpt-4o\"\n")
        path = f.name
    try:
        configer = DefaultLLMConfiger(path)
        assert configer.default_llm == "gpt-4o"
        assert configer.value.get("DEFAULT", {}).get("default_llm") == "gpt-4o"
    finally:
        os.unlink(path)


def test_set_get_roundtrip():
    configer = DefaultLLMConfiger()
    configer.set("a", 5)
    assert configer.get("a") == 5

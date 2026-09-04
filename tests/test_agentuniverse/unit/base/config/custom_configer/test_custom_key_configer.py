# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_custom_key_configer.py

"""Unit tests for the CustomKeyConfiger singleton."""

import os
import tempfile

from agentuniverse.base.config.custom_configer.custom_key_configer import \
    CustomKeyConfiger


def test_loads_key_list_into_environment():
    with tempfile.NamedTemporaryFile("w", suffix=".yaml",
                                     delete=False) as f:
        f.write("KEY_LIST:\n  AU_TEST_SECRET_KEY: abc123\n")
        path = f.name
    try:
        CustomKeyConfiger.__wrapped__(path)
        assert os.environ.get("AU_TEST_SECRET_KEY") == "abc123"
    finally:
        os.environ.pop("AU_TEST_SECRET_KEY", None)
        os.unlink(path)


def test_missing_config_file_is_tolerated(capsys):
    CustomKeyConfiger.__wrapped__("/tmp/missing_custom_key_file.yaml")
    assert "skip load custom key" in capsys.readouterr().out


def test_set_get_roundtrip():
    configer = CustomKeyConfiger()
    configer.set("x", 1)
    assert configer.get("x") == 1
    assert configer.to_dict()["x"] == 1

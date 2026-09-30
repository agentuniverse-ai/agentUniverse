# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_work_pattern_configer.py

"""Unit tests for the WorkPatternConfiger."""

from types import SimpleNamespace

from agentuniverse.base.config.component_configer.configers.work_pattern_configer import \
    WorkPatternConfiger


class TestWorkPatternConfiger:
    """Test work pattern configuration loading."""

    def test_defaults(self):
        configer = WorkPatternConfiger()
        assert configer.name is None
        assert configer.description is None

    def test_load_by_configer(self):
        configer = WorkPatternConfiger()
        value = {"name": "pattern1", "description": "desc",
                 "metadata": {"type": "work_pattern", "module": "m",
                              "class": "C"}}
        returned = configer.load_by_configer(SimpleNamespace(value=value,
                                                             path="x.yaml"))
        assert returned is configer
        assert configer.name == "pattern1"
        assert configer.description == "desc"

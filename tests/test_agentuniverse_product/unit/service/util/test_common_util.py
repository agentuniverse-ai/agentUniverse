# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: test_common_util.py
"""Unit tests for the common_util helpers in agentuniverse_product."""

import os
from pathlib import Path

from agentuniverse_product.service.util import common_util
from agentuniverse_product.service.util.common_util import (
    dict_does_not_contain_keys,
    get_core_path,
    get_resources_path,
)


def test_dict_does_not_contain_keys_when_keys_present():
    assert dict_does_not_contain_keys({'a': 1, 'b': 2}, ['a']) is False
    assert dict_does_not_contain_keys({'a': 1}, ['a', 'b']) is False


def test_dict_does_not_contain_keys_when_keys_absent():
    assert dict_does_not_contain_keys({'a': 1}, ['b']) is True
    assert dict_does_not_contain_keys({}, ['b']) is True


def test_dict_does_not_contain_keys_with_no_keys():
    assert dict_does_not_contain_keys({'a': 1}, []) is True


def test_get_core_path_returns_relative_core(monkeypatch):
    monkeypatch.setattr(common_util.os.path, 'exists',
                        lambda p: str(p) == os.path.join('..', 'core'))
    assert get_core_path() == Path(os.path.join('..', 'core'))


def test_get_core_path_returns_app_core(monkeypatch):
    def fake_exists(path):
        return str(path) == os.path.join('..', '..', 'app', 'core')
    monkeypatch.setattr(common_util.os.path, 'exists', fake_exists)
    assert get_core_path() == Path(os.path.join('..', '..', 'app', 'core'))


def test_get_core_path_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr(common_util.os.path, 'exists', lambda p: False)
    assert get_core_path() is None


def test_get_resources_path_returns_platform_resources(monkeypatch):
    target = os.path.join('..', '..', 'platform', 'difizen', 'resources')
    monkeypatch.setattr(common_util.os.path, 'exists',
                        lambda p: str(p) == target)
    assert get_resources_path() == Path(target)


def test_get_resources_path_returns_relative_resources(monkeypatch):
    target = os.path.join('..', 'resources')

    def fake_exists(path):
        return str(path) == target
    monkeypatch.setattr(common_util.os.path, 'exists', fake_exists)
    assert get_resources_path() == Path(target)


def test_get_resources_path_falls_back_to_app_resources(monkeypatch):
    monkeypatch.setattr(common_util.os.path, 'exists', lambda p: False)
    assert get_resources_path() == Path(os.path.join('..', '..', 'app', 'resources'))

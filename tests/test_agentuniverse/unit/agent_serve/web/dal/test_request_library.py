# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:35
# @Author  : yuewang
# @FileName: test_request_library.py
"""Unit tests for RequestLibrary backed by a temporary sqlite database."""

import datetime

import pytest

from agentuniverse.agent_serve.web.dal.entity.request_do import RequestDO
from agentuniverse.agent_serve.web.dal.request_library import RequestLibrary
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)


@pytest.fixture(autouse=True)
def app_config():
    """Provide a bare AppConfiger for component instance-code resolution."""
    ApplicationConfigManager().app_configer = AppConfiger()
    yield


def _configer(uri, table_name='request_task', update_interval=5):
    db = {'system_db_uri': uri,
          'request_table_name': table_name,
          'update_interval': update_interval}
    return type('C', (), {'get': lambda self, key, default=None: db})()


def _request_do(request_id='req-1'):
    return RequestDO(
        request_id=request_id, session_id='sess-1', query='hello',
        state='init', result={}, steps=[], additional_args={},
        gmt_create=datetime.datetime.now(), gmt_modified=datetime.datetime.now())


@pytest.fixture
def library(tmp_path):
    """Create a RequestLibrary on a temporary sqlite file."""
    return RequestLibrary(_configer(f'sqlite:///{tmp_path}/req.db'))


class TestRequestLibrary:
    """Test RequestLibrary CRUD behavior."""

    def test_init_defaults_and_customs(self, tmp_path):
        lib = RequestLibrary(_configer(f'sqlite:///{tmp_path}/r.db',
                                       table_name='custom_tbl', update_interval=9))
        assert lib.request_table_name == 'custom_tbl'
        assert lib.update_interval == 9
        assert lib.request_orm.__tablename__ == 'custom_tbl'

    def test_add_and_query(self, library):
        row_id = library.add_request(_request_do())
        assert isinstance(row_id, int)
        found = library.query_request_by_request_id('req-1')
        assert found is not None
        assert found.request_id == 'req-1'
        assert found.session_id == 'sess-1'
        assert found.query == 'hello'
        assert found.state == 'init'

    def test_query_unknown_returns_none(self, library):
        assert library.query_request_by_request_id('nope') is None

    def test_update_request(self, library):
        library.add_request(_request_do())
        library.update_request(RequestDO(
            request_id='req-1', session_id='sess-1', query='hello',
            state='finish', result={'ok': 1}, steps=['s1'], additional_args={},
            gmt_create=datetime.datetime.now(), gmt_modified=datetime.datetime.now()))
        found = library.query_request_by_request_id('req-1')
        assert found.state == 'finish'
        assert found.result == {'ok': 1}

    def test_update_gmt_modified(self, library):
        library.add_request(_request_do())
        before = library.query_request_by_request_id('req-1').gmt_modified
        library.update_gmt_modified('req-1')
        after = library.query_request_by_request_id('req-1').gmt_modified
        assert after >= before


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

#!/usr/bin/env python3

import pytest

from agentuniverse.agent_serve.web.dal.request_library import (
    REQUEST_TABLE_NAME,
    RequestLibrary,
)
from agentuniverse.base.config.application_configer.app_configer import (
    AppConfiger,
)
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)


class _ConfigerStub:
    """Minimal Configer stand-in exposing a DB section."""

    def __init__(self, db_config=None):
        self._db_config = db_config or {}

    def get(self, key, default=None):
        if key == 'DB':
            return self._db_config
        return default


@pytest.fixture(autouse=True)
def _minimal_app_config():
    """SQLDBWrapper needs an appname; install a minimal AppConfiger."""
    app_configer = AppConfiger()
    app_configer._AppConfiger__base_info_appname = 'test_app'
    manager = ApplicationConfigManager()
    saved = manager.__dict__.get('_ApplicationConfigManager__app_configer')
    manager.app_configer = app_configer
    yield
    manager.__dict__['_ApplicationConfigManager__app_configer'] = saved


@pytest.fixture(autouse=True)
def _tmp_project_root(monkeypatch, tmp_path):
    import agentuniverse.agent_serve.web.dal.request_library as rl_module
    monkeypatch.setattr(rl_module, 'get_project_root_path',
                        lambda: tmp_path)


def _fresh_library(configer):
    # bypass the singleton so each test builds an independent instance
    return RequestLibrary.__wrapped__(configer)


class TestRequestLibraryDefaultInit:

    def test_init_without_configer_uses_sqlite_default(self):
        library = _fresh_library(None)
        assert library.update_interval == 5
        assert library.request_table_name == REQUEST_TABLE_NAME
        db_uri = library.sqldb_wrapper.db_wrapper_configer.db_uri
        assert db_uri.startswith('sqlite:///')

    def test_init_honors_configured_db_uri(self):
        library = _fresh_library(_ConfigerStub({'system_db_uri': 'sqlite:///:memory:'}))
        db_uri = library.sqldb_wrapper.db_wrapper_configer.db_uri
        assert db_uri == 'sqlite:///:memory:'

    def test_init_honors_mysql_uri_alias(self):
        library = _fresh_library(_ConfigerStub({'mysql_uri': 'sqlite:///:memory:'}))
        db_uri = library.sqldb_wrapper.db_wrapper_configer.db_uri
        assert db_uri == 'sqlite:///:memory:'

    def test_init_honors_update_interval_and_table_name(self):
        library = _fresh_library(_ConfigerStub({
            'update_interval': 30,
            'request_table_name': 'custom_request_table',
        }))
        assert library.update_interval == 30
        assert library.request_table_name == 'custom_request_table'

    def test_request_table_roundtrip_on_default_sqlite(self):
        import datetime

        from agentuniverse.agent_serve.web.dal.entity.request_do import RequestDO
        library = _fresh_library(None)
        request_do = RequestDO(
            request_id='req-1',
            session_id='sess-1',
            query={'input': 'hello'},
            state='running',
            result={},
            steps=[],
            additional_args={},
            gmt_create=datetime.datetime.now(),
            gmt_modified=datetime.datetime.now(),
        )
        library.add_request(request_do)
        loaded = library.query_request_by_request_id('req-1')
        assert loaded is not None
        assert loaded.request_id == 'req-1'
        assert loaded.state == 'running'

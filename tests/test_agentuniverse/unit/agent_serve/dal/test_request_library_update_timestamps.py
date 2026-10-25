# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @FileName: test_request_library_update_timestamps.py
from datetime import datetime, timedelta

import pytest

from agentuniverse.agent_serve.web.dal.entity.request_do import RequestDO
from agentuniverse.agent_serve.web.dal.request_library import RequestLibrary
from agentuniverse.agent_serve.web.request_task import RequestTask
from agentuniverse.base.config.application_configer.application_config_manager \
    import ApplicationConfigManager
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager


class _StubConfiger:
    """Minimal Configer stand-in exposing only .get()."""

    def __init__(self, db_uri):
        self._db = {'system_db_uri': db_uri, 'update_interval': 5}

    def get(self, key, default=None):
        if key == 'DB':
            return self._db
        return default


class _StubAppConfiger:
    base_info_appname = 'timestamp_test_app'


def _singleton_cache() -> dict | None:
    """Return the closure dict caching singleton instances, if reachable."""
    for cell in (RequestLibrary.__closure__ or ()):
        cached = cell.cell_contents
        if isinstance(cached, dict) and RequestLibrary in cached:
            return cached
    return None


@pytest.fixture()
def request_library(tmp_path):
    """Build a RequestLibrary bound to a scratch sqlite file.

    Constructing the library mutates three pieces of process-global state:
    the closure-based RequestLibrary singleton, the SQLDBWrapperManager
    registry (the constructor registers its wrapper there), and the global
    ApplicationConfigManager app_configer swapped for a stub here. Each is
    snapshotted before the swap-in and restored on teardown, and the scratch
    engine is disposed, so repeated setups with separate temporary
    directories cannot leak singleton, database or configuration state into
    other tests.
    """
    config_manager = ApplicationConfigManager()
    try:
        prev_app_configer = config_manager.app_configer
    except ValueError:
        # The getter raises while no AppConfiger is set; restoring None
        # reproduces that exact unset state.
        prev_app_configer = None
    prev_registered = dict(SQLDBWrapperManager()._instance_obj_map)
    singleton_cache = _singleton_cache()
    prev_library_instance = (singleton_cache.get(RequestLibrary)
                             if singleton_cache else None)

    config_manager.app_configer = _StubAppConfiger()
    if singleton_cache is not None:
        singleton_cache.pop(RequestLibrary, None)
    db_uri = f'sqlite:///{tmp_path / "request_task.db"}'
    library = RequestLibrary(_StubConfiger(db_uri))
    yield library

    # Close the sqlite pool so the scratch file is released with its tmp dir.
    library.sqldb_wrapper.sql_database._engine.dispose()

    registry = SQLDBWrapperManager()._instance_obj_map
    registry.clear()
    registry.update(prev_registered)
    if singleton_cache is not None:
        if prev_library_instance is None:
            singleton_cache.pop(RequestLibrary, None)
        else:
            singleton_cache[RequestLibrary] = prev_library_instance
    config_manager.app_configer = prev_app_configer


def _make_do(request_id: str, gmt: datetime) -> RequestDO:
    return RequestDO(
        request_id=request_id,
        session_id='',
        query='demo query',
        state='running',
        result=dict(),
        steps=[],
        additional_args=dict(),
        gmt_create=gmt,
        gmt_modified=gmt,
    )


def test_live_update_preserves_heartbeat_timestamp(request_library):
    """A flush of produced output must not revert the row clock.

    check_state bumps gmt_modified once a minute; the stream flushes run
    every update_interval seconds. Before the fix the flush wrote the DO's
    creation-time gmt_modified back, undoing every heartbeat and freezing
    the row clock at creation time.
    """
    created = datetime.now() - timedelta(minutes=11)
    task = _make_do('heartbeat-task', created)
    request_library.add_request(task)

    request_library.update_gmt_modified('heartbeat-task')
    row = request_library.query_request_by_request_id('heartbeat-task')
    heartbeat = row.gmt_modified

    task.result['result'] = {'partial': 1}
    task.steps.append('chunk-1')
    request_library.update_request(task)

    row = request_library.query_request_by_request_id('heartbeat-task')
    assert row.gmt_modified >= heartbeat


def test_watchdog_keeps_healthy_long_task_running(request_library):
    """Polling a >10 min task must not mark it failed.

    is_validate treats a row untouched for 10 minutes as stuck. Before the
    fix every update_request reset gmt_modified to the creation time, so
    the watchdog saw an 11-minute-old row and flipped the state of a
    healthy task to fail.
    """
    created = datetime.now() - timedelta(minutes=11)
    task = _make_do('long-running-task', created)
    request_library.add_request(task)

    # Steady state of /service_run_async: heartbeat, then output flush.
    request_library.update_gmt_modified('long-running-task')
    task.steps.append('token-batch-1')
    request_library.update_request(task)

    polled = RequestTask.query_request_state('long-running-task')
    assert polled['state'] == 'running'


def test_genuinely_stale_task_still_fails(request_library):
    """The watchdog must keep detecting rows that are truly untouched."""
    created = datetime.now() - timedelta(minutes=11)
    task = _make_do('stuck-task', created)
    request_library.add_request(task)

    polled = RequestTask.query_request_state('stuck-task')
    assert polled['state'] == 'fail'

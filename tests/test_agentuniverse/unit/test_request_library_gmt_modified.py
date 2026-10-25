# -*- coding: utf-8 -*-
"""Regression test for agentUniverse issue #4034.

`update_request` must not overwrite the `gmt_create` / `gmt_modified` columns
with the in-memory `RequestDO`'s stale timestamps. Otherwise a
`update_gmt_modified` heartbeat is lost on the next flush and long-running async
tasks are wrongly marked as failed by `RequestTask.is_validate` (which treats a
row untouched for 10 minutes as dead).

The bug only manifests through the real code path used by `RequestTask`:
the row is queried back into a `RequestDO` (which *explicitly* sets
`gmt_create`/`gmt_modified`), then that same in-memory DO is flushed again via
`update_request`. Because pydantic's `model_dump(exclude_unset=True)` then
includes those timestamps, the old code wrote the stale load-time value back and
pinned the row clock.
"""
import sys
import tempfile
import types

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# `request_library` (and its transitive imports) loads `langchain_core` and
# `langchain_community` at module load time, but the test drives a real sqlite
# engine through a patched `get_session`, so the langchain SQLDatabase wrapper
# is never used at runtime. Stub these packages when they are not installed
# (lightweight local runs) so the test stays self-contained; CI, where
# langchain is present, imports the real packages instead.
class _AutoStubModule(types.ModuleType):
    """A module that resolves any attribute to a harmless dummy callable.

    Enough for import-time name resolution (class annotations, base classes)
    without needing the heavy langchain dependency tree.
    """

    def __getattr__(self, name):
        class _Dummy:
            def __init__(self, *args, **kwargs):
                pass

            def __call__(self, *args, **kwargs):
                return _Dummy()

            def __getattr__(self, _n):
                return _Dummy()

        return _Dummy


class _StubLoader:
    def create_module(self, spec):
        return _AutoStubModule(spec.name)

    def exec_module(self, module):
        # Treat as a package so nested submodule imports keep resolving.
        module.__path__ = []
        module.__package__ = module.__name__


class _StubFinder:
    def __init__(self, roots):
        self.roots = tuple(roots)

    def find_spec(self, fullname, path, target=None):
        if fullname in sys.modules:
            return None
        if not any(fullname == r or fullname.startswith(r + ".") for r in self.roots):
            return None
        from importlib.machinery import ModuleSpec
        return ModuleSpec(fullname, _StubLoader())


try:  # pragma: no cover - environment dependent
    import langchain_core  # noqa: F401
    import langchain_community  # noqa: F401
except ImportError:  # pragma: no cover - lightweight local runs
    sys.meta_path.insert(0, _StubFinder(["langchain_core", "langchain_community"]))

from agentuniverse.agent_serve.web.dal import request_library
from agentuniverse.agent_serve.web.dal.entity.request_do import RequestDO
from agentuniverse.agent_serve.web.dal.request_library import RequestLibrary
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper

# Use a dedicated sqlite engine so the test does not depend on the langchain
# SQLDatabase wrapper or the project's default on-disk db path.
_ENGINE = create_engine("sqlite:///" + tempfile.mktemp(suffix=".db"))
_SESSION = sessionmaker(bind=_ENGINE)


def _fake_get_session(self):
    request_library.Base.metadata.create_all(_ENGINE)
    return _SESSION()


def _make_library():
    class _Configer:
        def get(self, key, default=None):
            if key == "DB":
                return {"system_db_uri": "sqlite:///" + tempfile.mktemp(suffix=".db")}
            return default

    # `SQLDBWrapper.get_instance_code` reads the global application config, which
    # is not initialised in this isolated test. It is only used as a registry key
    # during construction, so patch it just for the `RequestLibrary(...)` call and
    # restore the original class method afterwards — a permanent class-level
    # patch would leak into every other test running in the same process.
    original_get_instance_code = SQLDBWrapper.get_instance_code
    SQLDBWrapper.get_instance_code = lambda self: "__system_db__"
    try:
        lib = RequestLibrary(configer=_Configer())
    finally:
        SQLDBWrapper.get_instance_code = original_get_instance_code
    # Route this instance's sessions to the dedicated sqlite engine via an
    # *instance* attribute (instance attributes shadow the class method), so
    # the production `RequestLibrary.get_session` is left untouched.
    lib.get_session = lambda: _fake_get_session(lib)
    return lib


def test_update_request_preserves_gmt_modified_heartbeat():
    lib = _make_library()
    lib.add_request(RequestDO(
        request_id="task-4034",
        session_id="",
        query="q",
        state="running",
        result={"result": ""},
        steps=[],
        additional_args={},
    ))

    # Load the DO exactly as RequestTask does before flushing output.
    do = lib.query_request_by_request_id("task-4034")
    loaded_ts = do.gmt_modified  # stale timestamp captured at load time

    # A heartbeat fires after the load, advancing the row clock.
    lib.update_gmt_modified("task-4034")
    heartbeat = lib.query_request_by_request_id("task-4034").gmt_modified
    assert heartbeat > loaded_ts

    # The task keeps producing output and flushes via update_request using the
    # SAME in-memory DO (exactly how RequestTask behaves).
    do.result["result"] = {"partial": 1}
    do.steps.append("chunk-1")
    lib.update_request(do)

    row = lib.query_request_by_request_id("task-4034")
    assert row.gmt_modified >= heartbeat, (
        "update_request pinned gmt_modified to the stale load-time value "
        f"({row.gmt_modified} < heartbeat {heartbeat})"
    )
    # The real payload must still be persisted.
    assert row.result == {"result": {"partial": 1}}
    assert row.steps == ["chunk-1"]


def test_update_request_leaves_gmt_create_immutable():
    lib = _make_library()
    lib.add_request(RequestDO(
        request_id="task-4034-b",
        session_id="",
        query="q",
        state="running",
        result={},
        steps=[],
        additional_args={},
    ))
    do = lib.query_request_by_request_id("task-4034-b")
    created = do.gmt_create

    do.result = {"result": 2}
    do.steps.append("extra")
    lib.update_request(do)

    row = lib.query_request_by_request_id("task-4034-b")
    assert row.gmt_create == created
    assert row.result == {"result": 2}

from unittest.mock import patch

import pytest

from agentuniverse.agent_serve.web.dal.request_library import RequestLibrary
from agentuniverse.agent_serve.web.dal.entity.request_do import RequestDO
from tests.test_agentuniverse.mock.agent_serve.mock_application_config_manager import (
    MockApplicationConfigManager,
)


@pytest.mark.parametrize(
    "query",
    [
        [],
        {"messages": [{"role": "user", "content": "hello"}]},
    ],
    ids=["list", "dict"],
)
def test_request_do_accepts_structured_query(query):
    request = RequestDO(
        request_id="request-id",
        session_id="session-id",
        query=query,
        state="init",
        result={},
        steps=[],
        additional_args={},
    )

    assert request.query == query


def test_request_library_add_request_round_trips_structured_query(tmp_path):
    with patch(
        "agentuniverse.database.sqldb_wrapper.ApplicationConfigManager",
        new=MockApplicationConfigManager,
    ):
        library = RequestLibrary(
            configer={
                "DB": {
                    "system_db_uri": f"sqlite:///{tmp_path.as_posix()}/request.db",
                    "request_table_name": "request_task",
                }
            }
        )
    cases = [
        ("request-list-query", ["hello", {"role": "user"}]),
        (
            "request-dict-query",
            {"messages": [{"role": "user", "content": "hello"}]},
        ),
    ]

    for request_id, query in cases:
        library.add_request(
            RequestDO(
                request_id=request_id,
                session_id="session-id",
                query=query,
                state="init",
                result={},
                steps=[],
                additional_args={},
            )
        )

        saved_request = library.query_request_by_request_id(request_id)

        assert saved_request is not None
        assert saved_request.query == query

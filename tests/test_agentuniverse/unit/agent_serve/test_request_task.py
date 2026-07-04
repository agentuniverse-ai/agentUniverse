import pytest

from agentuniverse.agent_serve.web.dal.entity.request_do import RequestDO


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

from unittest.mock import patch

from agentuniverse.agent_serve.web.rpc.rpc_server import service_run_result


def test_missing_request_result_keeps_complete_response_schema():
    with patch(
        "agentuniverse.agent_serve.web.rpc.rpc_server.RequestTask.query_request_state",
        return_value=None,
    ):
        result = service_run_result("missing-id")

    assert result == {
        "success": False,
        "result": "",
        "message": "request missing-id not found",
        "request_id": "missing-id",
    }

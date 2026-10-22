from agentuniverse.agent_serve.web import flask_server


def test_openai_stream_flag_enables_service_streaming(monkeypatch):
    captured = {}

    class FakeRequestTask:
        request_id = "request-id"

        def __init__(self, func, saved, **kwargs):
            captured.update(kwargs)

        def user_stream_run(self):
            yield '{"type":"EOF"}'

    monkeypatch.setattr(flask_server, "RequestTask", FakeRequestTask)

    response = flask_server.app.test_client().post(
        "/chat/completions",
        json={"model": "demo", "messages": [], "stream": True},
    )

    assert response.status_code == 200
    assert captured["streaming"] is True
    assert "stream" not in captured

from flask import Flask

from agentuniverse.agent_serve.web.web_util import request_param


def test_request_param_returns_bad_request_for_malformed_json():
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.post("/payload")
    @request_param
    def payload(value: str):
        return {"value": value}

    with app.test_client() as client:
        response = client.post(
            "/payload",
            data='{"value":',
            content_type="application/json",
        )

    assert response.status_code == 400

from flask import Flask

from agentuniverse.agent_serve.web.web_util import request_param


def create_app():
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.route("/payload", methods=["GET", "POST"])
    @request_param
    def payload(saved: bool = True):
        return {"saved": saved}

    return app


def test_request_param_parses_false_form_value():
    with create_app().test_client() as client:
        response = client.post("/payload", data={"saved": "false"})

    assert response.status_code == 200
    assert response.get_json()["saved"] is False


def test_request_param_parses_boolean_query_value_case_insensitively():
    with create_app().test_client() as client:
        response = client.get("/payload?saved=YES")

    assert response.status_code == 200
    assert response.get_json()["saved"] is True


def test_request_param_preserves_native_json_boolean():
    with create_app().test_client() as client:
        response = client.post("/payload", json={"saved": False})

    assert response.status_code == 200
    assert response.get_json()["saved"] is False


def test_request_param_rejects_unrecognized_boolean_value():
    with create_app().test_client() as client:
        response = client.post("/payload", data={"saved": "sometimes"})

    assert response.status_code == 400

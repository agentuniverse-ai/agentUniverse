#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import unittest

from flask import Flask, jsonify

from agentuniverse.agent_serve.web.web_util import request_param


def _build_app() -> Flask:
    app = Flask(__name__)

    @app.post('/echo')
    @request_param
    def echo(**kwargs):
        return jsonify(kwargs)

    return app


class TestRequestParamContentType(unittest.TestCase):
    def test_post_without_content_type_returns_200(self) -> None:
        """A POST without a Content-Type header must not turn into a 500.

        werkzeug's headers.get returns None for the absent header, and the
        previous 'in' membership check on None raised TypeError.
        """
        client = _build_app().test_client()
        resp = client.post('/echo', data=b'a=1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {})

    def test_post_with_json_content_type_still_parses_body(self) -> None:
        client = _build_app().test_client()
        resp = client.post('/echo', data=json.dumps({'a': '1'}),
                           content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {'a': '1'})


if __name__ == '__main__':
    unittest.main()

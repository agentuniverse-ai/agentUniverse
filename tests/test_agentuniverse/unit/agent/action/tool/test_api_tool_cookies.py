"""Offline request-level coverage for OpenAPI cookie parameters."""

import unittest
from http.cookies import SimpleCookie
from unittest.mock import patch

import httpx

from agentuniverse.agent.action.tool.api_tool import APITool
from agentuniverse.agent.action.tool.tool import ToolInput


class TestAPIToolCookies(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.redirect_to = None
        self.tool = APITool(
            openapi_spec={
                "url": "https://api.example.test/items/{item}",
                "method": "get",
                "operation": {
                    "parameters": [
                        {"name": "item", "in": "path", "required": True},
                        {"name": "session", "in": "cookie", "required": True},
                        {"name": "locale", "in": "cookie", "schema": {"default": "en"}},
                        {"name": "optional", "in": "cookie"},
                        {"name": "q", "in": "query"},
                        {"name": "X-Test", "in": "header"},
                    ]
                },
            }
        )

    def request(self, method, url, **kwargs):
        """Use HTTPX serialization and redirects without making network calls."""

        def handle(request):
            self.requests.append(request)
            if self.redirect_to and len(self.requests) == 1:
                return httpx.Response(302, headers={"Location": self.redirect_to})
            return httpx.Response(200, text="ok")

        cookies = kwargs.pop("cookies", None)
        with httpx.Client(cookies=cookies, transport=httpx.MockTransport(handle)) as client:
            return client.request(method, url, **kwargs)

    def call(self, **parameters):
        with patch("agentuniverse.agent.action.tool.utils.ssrf_proxy.httpx.request", self.request):
            return self.tool.execute(ToolInput({"item": "one", "session": "synthetic", **parameters}))

    def test_supplied_and_default_cookies_reach_request(self):
        self.assertEqual(self.call(q="query", **{"X-Test": "header"}), "ok")
        request = self.requests[0]
        self.assertEqual(
            {name: cookie.value for name, cookie in SimpleCookie(request.headers["Cookie"]).items()},
            {"session": "synthetic", "locale": "en"},
        )
        self.assertEqual(request.url.path, "/items/one")
        self.assertEqual(request.url.params["q"], "query")
        self.assertEqual(request.headers["X-Test"], "header")
        self.assertNotIn("session", request.url.params)

    def test_supplied_cookie_overrides_default(self):
        self.call(locale="fr")
        self.assertEqual(
            {name: cookie.value for name, cookie in SimpleCookie(self.requests[0].headers["Cookie"]).items()},
            {"session": "synthetic", "locale": "fr"},
        )

    def test_cookie_parameters_are_order_independent(self):
        self.tool.openapi_spec["operation"]["parameters"].reverse()
        for parameters, locale in (({}, "en"), ({"locale": "fr"}, "fr")):
            with self.subTest(parameters=parameters):
                self.call(**parameters)
                self.assertEqual(
                    {name: cookie.value for name, cookie in SimpleCookie(self.requests[-1].headers["Cookie"]).items()},
                    {"session": "synthetic", "locale": locale},
                )

    def test_empty_cookie_value_is_preserved(self):
        self.call(session="")
        self.assertIn("session=", self.requests[0].headers["Cookie"])

    def test_cookie_parameters_work_for_all_supported_methods(self):
        for method in ("get", "head", "post", "put", "delete", "patch"):
            with self.subTest(method=method):
                self.tool.openapi_spec["method"] = method
                self.call()
                self.assertEqual(self.requests[-1].method, method.upper())
                self.assertIn("session=synthetic", self.requests[-1].headers["Cookie"])

    def test_missing_required_cookie_fails_before_http(self):
        with (
            patch("agentuniverse.agent.action.tool.utils.ssrf_proxy.httpx.request") as request,
            self.assertRaisesRegex(Exception, "Missing required parameter session"),
        ):
            self.tool.execute(ToolInput({"item": "one"}))
        request.assert_not_called()

    def test_no_cookie_parameters_does_not_add_cookie_header(self):
        self.tool.openapi_spec["operation"]["parameters"] = []
        self.call()
        self.assertNotIn("Cookie", self.requests[0].headers)

    def test_cookie_parameters_support_local_endpoints(self):
        for host in ("localhost", "127.0.0.1", "[::1]"):
            with self.subTest(host=host):
                self.tool.openapi_spec["url"] = f"http://{host}:8000/items/{{item}}"
                self.call()
                self.assertIn("session=synthetic", self.requests[-1].headers["Cookie"])

    def test_cookies_survive_same_host_redirect(self):
        self.redirect_to = "https://api.example.test/redirected"
        self.call()
        self.assertEqual(len(self.requests), 2)
        self.assertIn("session=synthetic", self.requests[1].headers["Cookie"])

    def test_cookies_do_not_follow_cross_host_redirect(self):
        self.redirect_to = "https://other.example.test/redirected"
        self.call()
        self.assertEqual(len(self.requests), 2)
        self.assertNotIn("Cookie", self.requests[1].headers)

    def test_secure_cookies_do_not_follow_https_downgrade(self):
        self.redirect_to = "http://api.example.test/redirected"
        self.call()
        self.assertEqual(len(self.requests), 2)
        self.assertNotIn("Cookie", self.requests[1].headers)


if __name__ == "__main__":
    unittest.main()

import importlib
import unittest
from unittest.mock import Mock

from agentuniverse_extension.logger.log_sink.custom_flask_request_sink import CustomFlaskRequestSink
from agentuniverse_extension.logger.log_sink.custom_flask_response_sink import CustomFlaskResponseSink


class TestSafeFlaskSinks(unittest.TestCase):
    def test_request_uses_route_template_without_touching_credentials(self):
        request = Mock()
        request.method = 'POST'
        request.path = '/reset/private-token'
        request.url_rule.rule = '/reset/<token>'
        request.headers = {'Authorization': 'Bearer secret', 'Cookie': 'session=secret'}
        request.data = b'{"password": "secret"}'
        result = CustomFlaskRequestSink().generate_log(request)
        self.assertEqual(result, 'Request: POST /reset/<token>')
        request.get_data.assert_not_called()

    def test_unmatched_request_does_not_fall_back_to_raw_path(self):
        request = Mock(method='GET', path='/private-token', url_rule=None)
        self.assertEqual(CustomFlaskRequestSink().generate_log(request),
                         'Request: GET [unmatched route]')

    def test_response_omits_body_and_literal_string(self):
        response = Mock(status_code=200, content_type='application/json')
        response.data = b'{"token": "secret"}'
        sink = CustomFlaskResponseSink()
        self.assertEqual(sink.generate_log(response, 0.125),
                         'Response: 200 application/json Duration: 0.125s')
        response.get_data.assert_not_called()
        self.assertEqual(sink.generate_log('password=secret', 0.125),
                         'Response: [string response] Duration: 0.125s')

    def test_example_sinks_reuse_safe_implementation(self):
        for package in (
            'examples.sample_standard_app.intelligence.utils.log_sink',
            'examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.utils.log_sink',
        ):
            for typ, cls in (('request', CustomFlaskRequestSink),
                             ('response', CustomFlaskResponseSink)):
                module = importlib.import_module(f'{package}.custom_flask_{typ}_sink')
                self.assertIs(getattr(module, cls.__name__), cls)

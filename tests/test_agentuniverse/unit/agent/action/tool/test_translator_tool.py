#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import Mock, patch

import httpx
import yaml

from agentuniverse.agent.action.tool.common_tool import translator_tool as translator_module
from agentuniverse.agent.action.tool.common_tool.translator_tool import TranslatorTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = translator_module.__file__.replace(".py", ".yaml")


def httpx_response_mock(*, json_data=None):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class TranslatorToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = TranslatorTool()

    def _google_payload(self, translated="Hello", detected="en"):
        # Google's nested-list response format:
        # payload[0] = list of [translated_chunk, original_chunk, ...] segments
        # payload[2] = detected source language (when sl=auto)
        return [[[translated, "你好", None, None, 1]], None, detected]

    @patch("agentuniverse.agent.action.tool.common_tool.translator_tool.httpx.get")
    def test_translate_returns_translated_text(self, mock_get: Mock) -> None:
        mock_get.return_value = httpx_response_mock(json_data=self._google_payload("Hello", "zh"))
        result = self.tool.execute(text="你好", source="auto", target="en")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["translated_text"], "Hello")
        self.assertEqual(result["source_language"], "zh")
        self.assertEqual(result["target_language"], "en")
        self.assertEqual(result["engine"], "google_translate")

    @patch("agentuniverse.agent.action.tool.common_tool.translator_tool.httpx.get")
    def test_translate_uses_defaults_when_omitted(self, mock_get: Mock) -> None:
        mock_get.return_value = httpx_response_mock(json_data=self._google_payload("Bonjour", ""))
        tool = TranslatorTool(default_source="fr", default_target="en")
        result = tool.execute(text="bonjour")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["target_language"], "en")
        call_params = mock_get.call_args.kwargs["params"]
        self.assertEqual(call_params["sl"], "fr")
        self.assertEqual(call_params["tl"], "en")

    @patch("agentuniverse.agent.action.tool.common_tool.translator_tool.httpx.get")
    def test_translate_explicit_languages(self, mock_get: Mock) -> None:
        mock_get.return_value = httpx_response_mock(json_data=self._google_payload("Hallo", "de"))
        result = self.tool.execute(text="hello", source="en", target="de")
        self.assertEqual(result["translated_text"], "Hallo")
        self.assertEqual(result["source_language"], "de")
        self.assertEqual(result["target_language"], "de")

    @patch("agentuniverse.agent.action.tool.common_tool.translator_tool.httpx.get")
    def test_translate_passes_timeout_and_query(self, mock_get: Mock) -> None:
        mock_get.return_value = httpx_response_mock(json_data=self._google_payload("x", "en"))
        self.tool.execute(text="hi", source="en", target="zh")
        kwargs = mock_get.call_args.kwargs
        self.assertEqual(kwargs["timeout"], self.tool.request_timeout)
        self.assertEqual(kwargs["params"]["q"], "hi")
        self.assertEqual(kwargs["params"]["sl"], "en")
        self.assertEqual(kwargs["params"]["tl"], "zh")
        self.assertEqual(kwargs["params"]["client"], "gtx")

    def test_translate_rejects_empty_text(self) -> None:
        result = self.tool.execute(text="   ")
        self.assertEqual(result["status"], "error")
        self.assertIn("empty", result["error"])

    def test_translate_rejects_non_string_text(self) -> None:
        result = self.tool.execute(text=123)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_translate_rejects_unsupported_source(self) -> None:
        result = self.tool.execute(text="hi", source="klingon", target="en")
        self.assertEqual(result["status"], "error")
        self.assertIn("unsupported source language", result["error"])

    def test_translate_rejects_unsupported_target(self) -> None:
        result = self.tool.execute(text="hi", source="en", target="klingon")
        self.assertEqual(result["status"], "error")
        self.assertIn("unsupported target language", result["error"])

    def test_translate_rejects_same_source_and_target(self) -> None:
        result = self.tool.execute(text="hi", source="en", target="en")
        self.assertEqual(result["status"], "error")
        self.assertIn("different languages", result["error"])

    def test_translate_rejects_oversized_text(self) -> None:
        original = TranslatorTool.MAX_TEXT_CHARS
        TranslatorTool.MAX_TEXT_CHARS = 5
        try:
            result = self.tool.execute(text="abcdefgh")
        finally:
            TranslatorTool.MAX_TEXT_CHARS = original
        self.assertEqual(result["status"], "error")
        self.assertIn("MAX_TEXT_CHARS", result["error"])

    @patch("agentuniverse.agent.action.tool.common_tool.translator_tool.httpx.get")
    def test_translate_handles_network_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = httpx.ConnectError("boom")
        result = self.tool.execute(text="hi", source="en", target="zh")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "network_error")

    @patch("agentuniverse.agent.action.tool.common_tool.translator_tool.httpx.get")
    def test_translate_handles_malformed_payload(self, mock_get: Mock) -> None:
        # Non-empty payload whose segment list is empty raises ValueError in
        # the response parser, surfaced as a validation_error.
        mock_get.return_value = httpx_response_mock(json_data=[[]])
        result = self.tool.execute(text="hi", source="en", target="zh")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("no segments", result["error"])

    @patch("agentuniverse.agent.action.tool.common_tool.translator_tool.httpx.get")
    def test_translate_handles_unexpected_exception(self, mock_get: Mock) -> None:
        # response.json() raising a non-(TypeError/ValueError) becomes operation_error.
        mock_get.return_value = httpx_response_mock(json_data=None)
        mock_get.return_value.json.side_effect = RuntimeError("decode failed")
        result = self.tool.execute(text="hi", source="en", target="zh")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "operation_error")

    @patch("agentuniverse.agent.action.tool.common_tool.translator_tool.httpx.get")
    def test_translate_multi_segment_concatenation(self, mock_get: Mock) -> None:
        payload = [[["Hello, ", "你好, ", None, None, 0], ["world", "世界", None, None, 0]], None, "zh"]
        mock_get.return_value = httpx_response_mock(json_data=payload)
        result = self.tool.execute(text="你好, 世界", source="zh", target="en")
        self.assertEqual(result["translated_text"], "Hello, world")

    def test_parse_google_response_extracts_translation(self) -> None:
        payload = [[["Hello, ", "你好, ", None, None, 0], ["world", "世界", None, None, 0]], None, "zh"]
        translated, detected = TranslatorTool._parse_google_response(payload)
        self.assertEqual(translated, "Hello, world")
        self.assertEqual(detected, "zh")


class TranslatorRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.config = Configer(path=YAML_PATH).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "TranslatorTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, TranslatorTool)
        self.assertEqual(tool.input_keys, ["text"])
        self.assertEqual(tool.default_target, "en")

    def test_yaml_loads_as_dict(self):
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["name"], "translator_tool")
        self.assertEqual(data["metadata"]["class"], "TranslatorTool")


if __name__ == "__main__":
    unittest.main()

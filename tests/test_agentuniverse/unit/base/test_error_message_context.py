#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.common_util import parse_and_check_json_markdown
from agentuniverse.base.util.prompt_util import process_llm_token


class TestComponentEnumErrorMessage(unittest.TestCase):
    """Unknown component type errors should list the valid values."""

    def test_unknown_value_lists_valid_component_types(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ComponentEnum.from_value("NOT_A_REAL_TYPE")
        message = str(ctx.exception)
        self.assertIn("NOT_A_REAL_TYPE", message)
        # The message must offer the valid alternatives for self-correction.
        self.assertIn("LLM", message)
        self.assertIn("WORK_PATTERN", message)

    def test_unknown_value_message_quotes_the_offending_value(self) -> None:
        """A bad value should be quoted so whitespace/empty input is visible."""
        with self.assertRaises(ValueError) as ctx:
            ComponentEnum.from_value(" ")
        self.assertIn("' '", str(ctx.exception))


class TestComponentConfigerUtilErrorMessage(unittest.TestCase):
    """Unregistered component type errors should list registered types."""

    def test_unregistered_type_lists_registered_types(self) -> None:
        with self.assertRaises(Exception) as ctx:
            ComponentConfigerUtil.get_component_config_clz_by_type("NOT_A_TYPE")
        message = str(ctx.exception)
        self.assertIn("NOT_A_TYPE", message)
        # Registered alternatives must be discoverable from the error itself.
        self.assertIn("LLM", message)
        self.assertIn("WORK_PATTERN", message)


class TestParseAndCheckJsonMarkdownErrors(unittest.TestCase):
    """JSON parse/check failures should carry the offending input and cause."""

    def test_invalid_json_chains_cause_and_includes_snippet(self) -> None:
        text = "this is definitely not json {"
        with self.assertRaises(Exception) as ctx:
            parse_and_check_json_markdown(text, None)
        self.assertIsInstance(ctx.exception.__cause__, json.JSONDecodeError)
        message = str(ctx.exception)
        self.assertIn("this is definitely not json", message)
        self.assertIn("line 1", message)

    def test_long_invalid_text_is_truncated_in_message(self) -> None:
        text = "x" * 500 + " {"
        with self.assertRaises(Exception) as ctx:
            parse_and_check_json_markdown(text, None)
        message = str(ctx.exception)
        # The snippet must stay bounded so logs are not flooded.
        self.assertIn("...", message)
        self.assertLess(len(message), 400)

    def test_missing_key_reports_received_keys(self) -> None:
        with self.assertRaises(Exception) as ctx:
            parse_and_check_json_markdown('{"answer": "42"}', ["result"])
        message = str(ctx.exception)
        self.assertIn("result", message)
        # Received keys should be listed instead of only dumping the object.
        self.assertIn("answer", message)
        self.assertIn("keys", message)


class TestPromptTokenBudgetErrorMessage(unittest.TestCase):
    """The token-budget error should include the real numbers involved."""

    def test_budget_error_includes_context_length_and_max_tokens(self) -> None:
        agent_llm = MagicMock()
        agent_llm.max_context_length.return_value = 100
        agent_llm.max_tokens = 4096
        agent_llm.get_num_tokens.return_value = 10

        lc_prompt_template = MagicMock()
        lc_prompt_template.input_variables = []
        lc_prompt_template.format.return_value = "prompt"

        profile = {"llm_model": {"max_tokens": 200}}

        with patch("agentuniverse.base.util.prompt_util.LLMManager") as manager_cls:
            manager_cls.return_value.get_instance_obj.return_value = None
            with self.assertRaises(Exception) as ctx:
                process_llm_token(agent_llm, lc_prompt_template, profile, {})

        message = str(ctx.exception)
        self.assertIn("context_length=100", message)
        self.assertIn("max_tokens=200", message)
        self.assertIn("input token budget=-100", message)
        self.assertIn("less than 100", message)


if __name__ == "__main__":
    unittest.main()

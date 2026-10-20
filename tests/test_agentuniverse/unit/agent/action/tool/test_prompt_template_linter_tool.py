#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_prompt_template_linter_tool.py

"""Offline unit tests for PromptTemplateLinterTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic.

The placeholder convention exercised here was discovered from the
framework source (and is cited in the PR body):

* ``agentuniverse/prompt/prompt.py`` — ``Prompt.build_prompt`` and
  ``Prompt.initialize_by_component_configer`` extract
  ``input_variables`` with ``re.findall(r'\\{(.*?)}', template)``;
  ``agentuniverse/prompt/chat_prompt.py::extract_placeholders`` uses
  the same lazy pattern. Placeholder names in the shipped prompts
  (``agentuniverse/agent/default/react_agent/default_en_prompt.yaml``)
  are simple identifiers such as ``tools``, ``tool_names``,
  ``chat_history``, ``background``, ``input`` and
  ``agent_scratchpad``.
* Resolution goes through ``Prompt.as_langchain()`` (LangChain
  ``PromptTemplate``, default f-string format) — Python
  ``str.format`` semantics: ``{{`` / ``}}`` are literal-brace escapes
  and substituted values are verbatim. The fill-mode tests assert
  exact parity with ``str.format`` output on clean templates.
* ``agentuniverse/base/util/prompt/combine_en_prompt.yaml``
  intentionally keeps a placeholder inside a ```{text}``` fence, which
  is why ``placeholder_in_code`` is only a warning.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import PromptTemplateLinterTool
from agentuniverse.agent.action.tool.common_tool.prompt_template_linter_tool import (
    PromptTemplateLinterTool as DirectPromptTemplateLinterTool,
)


def finding_types(result):
    """Return the list of finding types of a lint result, in order."""
    return [f["type"] for f in result["findings"]]


class PromptTemplateLinterToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib linter tool."""

    def setUp(self) -> None:
        self.tool = PromptTemplateLinterTool()
        self.assertIs(self.tool.__class__, DirectPromptTemplateLinterTool)

    # ------------------------------------------------------------------ #
    # lint mode — finding kinds
    # ------------------------------------------------------------------ #

    def test_lint_clean_react_style_template(self) -> None:
        template = (
            "You can use the following tools:\n"
            "{tools}\n"
            "Action: one of {tool_names}\n"
            "Previous conversation:\n"
            "{chat_history}\n"
            "Question: {input}\n"
        )
        result = self.tool.execute(mode="lint", template=template)
        self.assertTrue(result["ok"])
        self.assertEqual(result["findings"], [])
        self.assertEqual(
            result["placeholders"],
            ["tools", "tool_names", "chat_history", "input"],
        )
        self.assertEqual(
            result["counts"], {"error": 0, "warning": 0, "info": 0, "total": 0}
        )

    def test_lint_malformed_braces_unclosed(self) -> None:
        result = self.tool.execute(mode="lint", template="Hello {name")
        self.assertFalse(result["ok"])
        self.assertEqual(finding_types(result), ["malformed_braces"])
        finding = result["findings"][0]
        self.assertEqual(finding["severity"], "error")
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["column"], 7)

    def test_lint_malformed_braces_stray_closer(self) -> None:
        result = self.tool.execute(mode="lint", template="Hello } world")
        self.assertFalse(result["ok"])
        self.assertEqual(finding_types(result), ["malformed_braces"])
        self.assertIn("without a matching", result["findings"][0]["message"])

    def test_lint_malformed_braces_nested(self) -> None:
        result = self.tool.execute(mode="lint", template="{outer {inner} tail}")
        self.assertFalse(result["ok"])
        self.assertEqual(finding_types(result)[0], "malformed_braces")
        self.assertGreaterEqual(
            sum(1 for t in finding_types(result) if t == "malformed_braces"), 1
        )

    def test_lint_escaped_braces_are_literal_not_placeholders(self) -> None:
        template = "Output JSON like {{\"key\": \"{name}\"}} then stop."
        result = self.tool.execute(mode="lint", template=template)
        self.assertTrue(result["ok"])
        self.assertEqual(result["placeholders"], ["name"])
        self.assertEqual(result["findings"], [])
        extracted = self.tool.execute(mode="extract", template=template)
        self.assertEqual(extracted["result"], ["name"])

    def test_lint_empty_placeholder(self) -> None:
        result = self.tool.execute(mode="lint", template="Hello {} world")
        self.assertFalse(result["ok"])
        self.assertEqual(finding_types(result), ["empty_placeholder"])
        self.assertEqual(result["placeholders"], [])

    def test_lint_invalid_name_with_space(self) -> None:
        result = self.tool.execute(mode="lint", template="Hi {user name}!")
        self.assertFalse(result["ok"])
        self.assertEqual(finding_types(result), ["invalid_name"])
        self.assertIn("user name", result["findings"][0]["message"])

    def test_lint_invalid_name_leading_digit_and_dash(self) -> None:
        result = self.tool.execute(mode="lint", template="{1st} {dash-name}")
        self.assertFalse(result["ok"])
        self.assertEqual(finding_types(result), ["invalid_name", "invalid_name"])

    def test_lint_valid_identifier_shapes_accepted(self) -> None:
        template = "{_private} {agent_scratchpad} {x9} {A}"
        result = self.tool.execute(mode="lint", template=template)
        self.assertTrue(result["ok"])
        self.assertEqual(
            result["placeholders"],
            ["_private", "agent_scratchpad", "x9", "A"],
        )

    def test_lint_duplicate_placeholder_is_info(self) -> None:
        template = "First {topic}, again {topic}, and {other}."
        result = self.tool.execute(mode="lint", template=template)
        self.assertTrue(result["ok"])  # info does not fail the lint
        self.assertEqual(finding_types(result), ["duplicate_placeholder"])
        finding = result["findings"][0]
        self.assertEqual(finding["severity"], "info")
        self.assertEqual(finding["name"], "topic")
        self.assertEqual(
            result["counts"], {"error": 0, "warning": 0, "info": 1, "total": 1}
        )

    def test_lint_placeholder_in_fenced_code_block_is_warning(self) -> None:
        template = (
            "Example:\n"
            "```python\n"
            "print({query})\n"
            "```\n"
            "Answer: {input}\n"
        )
        result = self.tool.execute(mode="lint", template=template)
        self.assertTrue(result["ok"])  # warning does not fail the lint
        self.assertEqual(finding_types(result), ["placeholder_in_code"])
        finding = result["findings"][0]
        self.assertEqual(finding["severity"], "warning")
        self.assertEqual(finding["name"], "query")
        self.assertEqual(finding["line"], 3)
        # the placeholder outside the fence is not flagged
        self.assertEqual(result["placeholders"], ["query", "input"])

    def test_lint_fence_opening_on_first_line(self) -> None:
        template = "```sql\nSELECT {column} FROM t;\n```\n"
        result = self.tool.execute(mode="lint", template=template)
        self.assertEqual(finding_types(result), ["placeholder_in_code"])
        self.assertTrue(result["ok"])

    def test_lint_framework_combine_prompt_fence_is_warning_only(self) -> None:
        # Mirrors agentuniverse/base/util/prompt/combine_en_prompt.yaml,
        # which intentionally fills the fenced block with {text}.
        template = (
            "Write a detailed summary of the following text:\n"
            "```{text}```\n"
        )
        result = self.tool.execute(mode="lint", template=template)
        self.assertEqual(finding_types(result), ["placeholder_in_code"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["placeholders"], ["text"])

    def test_lint_inline_triple_backtick_is_not_a_fence(self) -> None:
        template = "Use `x` and ```not a fence``` but {input} here.\n"
        result = self.tool.execute(mode="lint", template=template)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["placeholders"], ["input"])

    def test_lint_known_variables_comparison(self) -> None:
        template = "Tools: {tools}. Question: {input}."
        result = self.tool.execute(
            mode="lint",
            template=template,
            known_variables=["tools", "input", "background"],
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["placeholders_not_in_vars"], [])
        self.assertEqual(result["vars_without_placeholder"], ["background"])
        types = finding_types(result)
        self.assertEqual(types, ["vars_without_placeholder"])

        result2 = self.tool.execute(
            mode="lint",
            template=template,
            known_variables=["tools"],
        )
        self.assertEqual(result2["placeholders_not_in_vars"], ["input"])
        self.assertEqual(result2["vars_without_placeholder"], [])
        self.assertIn("placeholders_not_in_vars", finding_types(result2))

    def test_lint_known_variables_perfect_match(self) -> None:
        result = self.tool.execute(
            mode="lint",
            template="{a} {b}",
            known_variables=["b", "a"],
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["placeholders_not_in_vars"], [])
        self.assertEqual(result["vars_without_placeholder"], [])
        self.assertEqual(result["findings"], [])

    def test_lint_summary_string_and_line_columns(self) -> None:
        template = "line one\nline two {x}\nline three {x}\n"
        result = self.tool.execute(mode="lint", template=template)
        self.assertEqual(result["counts"]["info"], 1)
        self.assertIn("1 info", result["result"])
        finding = result["findings"][0]
        self.assertEqual(finding["line"], 2)  # first occurrence position
        self.assertEqual(finding["column"], 10)  # "line two " is 9 chars

    # ------------------------------------------------------------------ #
    # extract mode
    # ------------------------------------------------------------------ #

    def test_extract_ordered_and_deduplicated(self) -> None:
        template = "{zebra} {alpha} {zebra} {middle} {alpha}"
        result = self.tool.execute(mode="extract", template=template)
        self.assertEqual(result["mode"], "extract")
        self.assertEqual(result["result"], ["zebra", "alpha", "middle"])
        self.assertEqual(result["count"], 3)

    def test_extract_mirrors_framework_regex_on_mixed_template(self) -> None:
        # Like the framework's lazy regex, extract lists every
        # non-empty {name} span — including names lint flags as
        # invalid; the empty {} span has no name and is skipped.
        import re

        template = "{good} {} {bad name} {also_good}"
        result = self.tool.execute(mode="extract", template=template)
        self.assertEqual(result["result"], ["good", "bad name", "also_good"])
        self.assertEqual(
            result["result"],
            [name for name in re.findall(r"\{(.*?)}", template) if name],
        )

    def test_extract_no_placeholders(self) -> None:
        result = self.tool.execute(mode="extract", template="plain text only")
        self.assertEqual(result["result"], [])
        self.assertEqual(result["count"], 0)

    def test_extract_ignores_escaped_braces(self) -> None:
        result = self.tool.execute(
            mode="extract", template="{{not_a_placeholder}} {real_one}"
        )
        self.assertEqual(result["result"], ["real_one"])

    def test_extract_matches_framework_lazy_regex_on_clean_template(self) -> None:
        # On well-formed templates the tool agrees with the framework's
        # own extraction pattern from agentuniverse/prompt/prompt.py.
        import re

        template = (
            "You can use the following tools:\n{tools}\n"
            "Action: one of {tool_names}\nQuestion: {input}\n"
        )
        expected = re.findall(r"\{(.*?)}", template)
        result = self.tool.execute(mode="extract", template=template)
        self.assertEqual(result["result"], expected)

    # ------------------------------------------------------------------ #
    # fill mode
    # ------------------------------------------------------------------ #

    def test_fill_basic(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template="Hello {name}, welcome to {place}.",
            variables={"name": "Ada", "place": "agentUniverse"},
        )
        self.assertEqual(
            result,
            {
                "mode": "fill",
                "keep_unknown": False,
                "result": "Hello Ada, welcome to agentUniverse.",
                "filled": ["name", "place"],
                "unfilled": [],
                "extra_variables": [],
                "warnings": [],
            },
        )

    def test_fill_duplicate_placeholder_gets_same_value(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template="{x} and {x}",
            variables={"x": "same"},
        )
        self.assertEqual(result["result"], "same and same")
        self.assertEqual(result["filled"], ["x"])

    def test_fill_strict_missing_variables_error(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template="{a} {b} {c}",
            variables={"a": "1"},
        )
        self.assertEqual(result["error"]["type"], "missing_variables")
        self.assertIn("{b}", result["error"]["message"])
        self.assertIn("{c}", result["error"]["message"])
        self.assertNotIn("{a}", result["error"]["message"])

    def test_fill_extra_variables_produce_warnings(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template="{a}",
            variables={"a": "1", "unused": "2", "extra": "3"},
        )
        self.assertEqual(result["extra_variables"], ["unused", "extra"])
        self.assertEqual(result["warnings"], [
            "variable 'unused' has no placeholder in the template",
            "variable 'extra' has no placeholder in the template",
        ])
        self.assertEqual(result["result"], "1")
        self.assertNotIn("error", result)

    def test_fill_keep_unknown_leaves_placeholders(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template="Hello {name}, score {score}.",
            variables={"name": "Ada"},
            keep_unknown=True,
        )
        self.assertNotIn("error", result)
        self.assertTrue(result["keep_unknown"])
        self.assertEqual(result["result"], "Hello Ada, score {score}.")
        self.assertEqual(result["filled"], ["name"])
        self.assertEqual(result["unfilled"], ["score"])

    def test_fill_keep_unknown_with_all_present(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template="{a}",
            variables={"a": "x"},
            keep_unknown=True,
        )
        self.assertEqual(result["result"], "x")
        self.assertEqual(result["unfilled"], [])

    def test_fill_escapes_resolve_to_literal_braces(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template='Output JSON like {{"key": "{value}"}}.',
            variables={"value": "42"},
        )
        self.assertEqual(result["result"], 'Output JSON like {"key": "42"}.')

    def test_fill_escape_round_trip_with_str_format(self) -> None:
        template = "{{{{}}}} {name} {{x}} {name}"
        variables = {"name": "V"}
        result = self.tool.execute(
            mode="fill", template=template, variables=variables
        )
        # Exact parity with the framework's resolution semantics.
        self.assertEqual(result["result"], template.format(**variables))
        self.assertEqual(result["result"], "{{}} V {x} V")

    def test_fill_parity_with_str_format_on_react_style_template(self) -> None:
        template = (
            "You can use the following tools:\n{tools}\n"
            "Action: one of [{tool_names}]\n"
            "Previous conversation:\n{chat_history}\n"
            "Question: {input}\n"
        )
        variables = {
            "tools": "search, calculator",
            "tool_names": "search, calculator",
            "chat_history": "user: hi",
            "input": "what is 2+2?",
        }
        result = self.tool.execute(
            mode="fill", template=template, variables=variables
        )
        self.assertEqual(result["result"], template.format(**variables))

    def test_fill_values_are_verbatim_not_rescanned(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template="{block}",
            variables={"block": "{{not_a_placeholder}} {also_not}"},
        )
        # Substituted values keep their braces verbatim (str.format
        # semantics: replacement text is never re-scanned).
        self.assertEqual(
            result["result"], "{{not_a_placeholder}} {also_not}"
        )
        template2 = "{block}"
        variables2 = {"block": "{x}"}
        result2 = self.tool.execute(
            mode="fill", template=template2, variables=variables2
        )
        self.assertEqual(result2["result"], template2.format(**variables2))

    def test_fill_combine_prompt_fenced_placeholder(self) -> None:
        template = "Summarize:\n```{text}```\n"
        result = self.tool.execute(
            mode="fill", template=template, variables={"text": "a {b} c"}
        )
        self.assertEqual(result["result"], "Summarize:\n```a {b} c```\n")

    def test_fill_malformed_template_returns_error(self) -> None:
        result = self.tool.execute(
            mode="fill",
            template="Hello {name",
            variables={"name": "Ada"},
        )
        self.assertEqual(result["error"]["type"], "malformed_template")
        self.assertIn("malformed braces", result["error"]["message"])

    def test_fill_empty_placeholder_returns_error(self) -> None:
        result = self.tool.execute(
            mode="fill", template="Hi {}", variables={"x": "1"}
        )
        self.assertEqual(result["error"]["type"], "malformed_template")
        self.assertIn("empty placeholder", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Input validation error matrix (ValueError before any computation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode_rejected(self) -> None:
        self.assert_invalid(mode="render", template="{x}")

    def test_missing_or_bad_template_rejected(self) -> None:
        self.assert_invalid(mode="lint")
        self.assert_invalid(mode="lint", template=None)
        self.assert_invalid(mode="lint", template="")
        self.assert_invalid(mode="lint", template=123)
        self.assert_invalid(mode="lint", template=True)
        self.assert_invalid(mode="extract", template=["{x}"])
        self.assert_invalid(mode="fill", template=None, variables={"x": "1"})

    def test_template_size_cap(self) -> None:
        self.assert_invalid(mode="lint", template="x" * 100_001)
        result = self.tool.execute(mode="lint", template="x" * 100_000)
        self.assertTrue(result["ok"])

    def test_fill_requires_variables_mapping(self) -> None:
        self.assert_invalid(mode="fill", template="{x}")
        self.assert_invalid(mode="fill", template="{x}", variables=None)
        self.assert_invalid(mode="fill", template="{x}", variables="x=1")
        self.assert_invalid(mode="fill", template="{x}", variables=[("x", "1")])
        self.assert_invalid(mode="fill", template="{x}", variables={"x": 1})
        self.assert_invalid(mode="fill", template="{x}", variables={"x": None})
        self.assert_invalid(mode="fill", template="{x}", variables={"x": True})
        self.assert_invalid(mode="fill", template="{x}", variables={1: "one"})
        self.assert_invalid(mode="fill", template="{x}", variables={"": "empty"})

    def test_variables_count_cap(self) -> None:
        variables = {f"v{i}": str(i) for i in range(201)}
        self.assert_invalid(mode="fill", template="{x}", variables=variables)
        # exactly 200 entries (199 extras plus the used one) is allowed
        ok_variables = {f"v{i}": str(i) for i in range(199)}
        result = self.tool.execute(
            mode="fill", template="{x}", variables={**ok_variables, "x": "1"}
        )
        self.assertEqual(result["result"], "1")
        self.assertEqual(len(result["extra_variables"]), 199)

    def test_known_variables_validation(self) -> None:
        self.assert_invalid(
            mode="lint", template="{x}", known_variables="x"
        )
        self.assert_invalid(
            mode="lint", template="{x}", known_variables=[1]
        )
        self.assert_invalid(
            mode="lint", template="{x}", known_variables=[""]
        )
        self.assert_invalid(
            mode="lint", template="{x}", known_variables=[None]
        )
        self.assert_invalid(
            mode="lint", template="{x}", known_variables={"x": 1}
        )

    def test_keep_unknown_must_be_boolean(self) -> None:
        self.assert_invalid(
            mode="fill", template="{x}", variables={"x": "1"}, keep_unknown="yes"
        )
        self.assert_invalid(
            mode="fill", template="{x}", variables={"x": "1"}, keep_unknown=1
        )
        # None means "not provided" and defaults to False.
        result = self.tool.execute(
            mode="fill", template="{x}", variables={"x": "1"}, keep_unknown=None
        )
        self.assertFalse(result["keep_unknown"])

    def test_error_messages_are_prefixed(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="nope", template="{x}")
        self.assertIn("prompt_template_linter_tool", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

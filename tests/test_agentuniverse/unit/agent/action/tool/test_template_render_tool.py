#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_template_render_tool.py

"""Offline unit tests for TemplateRenderTool.

The tool is built purely on the standard library (``string.Template``
plus a ``{{name}}``-grammar subclass) and never touches the network,
so this suite runs fully offline. Every assertion is deterministic:
substitutions are checked against literal ground-truth strings that do
not depend on the implementation under test, placeholder extraction /
validation positions are hand-computed from the template text, and the
error matrix pins the exact ``ValueError`` / structured-payload split.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import TemplateRenderTool
from agentuniverse.agent.action.tool.common_tool.template_render_tool import (
    TemplateRenderTool as DirectTemplateRenderTool,
)


class TemplateRenderToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TemplateRenderTool."""

    def setUp(self) -> None:
        self.tool = TemplateRenderTool()

    def assert_invalid(self, **kwargs) -> None:
        """Assert the call raises the input-validation ValueError."""
        kwargs.setdefault("mode", "render")
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    # ------------------------------------------------------------------ #
    # render mode — substitution ground truths (dollar style)
    # ------------------------------------------------------------------ #

    def test_render_braced_placeholder(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="Hello, ${name}!",
            variables={"name": "Alice"},
        )
        self.assertEqual(
            result,
            {
                "mode": "render",
                "placeholder_style": "dollar",
                "missing_policy": "strict",
                "placeholders": ["name"],
                "missing_variables": [],
                "unused_variables": [],
                "result": "Hello, Alice!",
            },
        )

    def test_render_bare_placeholder(self) -> None:
        result = self.tool.execute(
            mode="render", template="Hi $name", variables={"name": "Alice"}
        )
        self.assertEqual(result["result"], "Hi Alice")
        self.assertEqual(result["placeholders"], ["name"])

    def test_render_dollar_escape(self) -> None:
        result = self.tool.execute(
            mode="render", template="cost: $$5 today", variables={}
        )
        self.assertEqual(result["result"], "cost: $5 today")
        self.assertEqual(result["placeholders"], [])
        self.assertEqual(result["missing_variables"], [])

    def test_render_escape_directly_before_placeholder(self) -> None:
        # "$$$a" = escaped "$$" (literal "$") followed by the "$a" placeholder.
        result = self.tool.execute(
            mode="render", template="$$$a", variables={"a": "A"}
        )
        self.assertEqual(result["result"], "$A")

    def test_render_adjacent_placeholders(self) -> None:
        cases = {
            "$a$b": "12",
            "${a}${b}": "12",
            "$a${b}": "12",
            "${a}$b": "12",
        }
        for template, expected in cases.items():
            result = self.tool.execute(
                mode="render", template=template, variables={"a": "1", "b": "2"}
            )
            self.assertEqual(result["result"], expected)
            self.assertEqual(result["placeholders"], ["a", "b"])

    def test_render_identifier_boundary(self) -> None:
        # The name match stops at the first non-identifier character.
        result = self.tool.execute(
            mode="render",
            template="ab$cd-ef ${name}.",
            variables={"cd": "CD", "name": "n"},
        )
        self.assertEqual(result["result"], "abCD-ef n.")

    def test_render_no_resubstitution_of_values(self) -> None:
        # Substituted values are inserted literally: placeholders,
        # dollars and backslash sequences inside a value never take
        # effect and are never re-scanned.
        tricky = "${other} $$ \\1 ${missing}"
        result = self.tool.execute(
            mode="render", template="[$v]", variables={"v": tricky}
        )
        self.assertEqual(result["result"], "[${other} $$ \\1 ${missing}]")

    def test_render_empty_template(self) -> None:
        result = self.tool.execute(mode="render", template="", variables={})
        self.assertEqual(result["result"], "")
        self.assertEqual(result["placeholders"], [])
        self.assertEqual(result["unused_variables"], [])

    def test_render_scalar_values_are_coerced(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="$a ${b} $c $d",
            variables={"a": 42, "b": 1.5, "c": True, "d": False},
        )
        self.assertEqual(result["result"], "42 1.5 True False")

    def test_render_default_policy_fill(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="[$user]",
            variables={},
            missing_policy="default",
            default_value="-",
        )
        self.assertEqual(result["result"], "[-]")
        self.assertEqual(result["missing_variables"], ["user"])
        self.assertEqual(result["missing_policy"], "default")

    def test_render_default_policy_partial_and_coercion(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="$a/$b",
            variables={"a": 1},
            missing_policy="default",
            default_value=0,
        )
        self.assertEqual(result["result"], "1/0")
        self.assertEqual(result["missing_variables"], ["b"])

    def test_render_keep_policy_preserves_both_spellings(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="$name and ${name}",
            variables={},
            missing_policy="keep",
        )
        self.assertEqual(result["result"], "$name and ${name}")
        self.assertEqual(result["missing_variables"], ["name"])

    def test_render_keep_policy_partial(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="Hi $name, city: ${city}",
            variables={"name": "Alice"},
            missing_policy="keep",
        )
        self.assertEqual(result["result"], "Hi Alice, city: ${city}")
        self.assertEqual(result["placeholders"], ["name", "city"])
        self.assertEqual(result["missing_variables"], ["city"])

    def test_render_strict_error_lists_missing_names(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="${z} $a ${m}",
            variables={"a": "1"},
        )
        self.assertNotIn("result", result)
        self.assertEqual(result["mode"], "render")
        self.assertEqual(result["error"]["type"], "missing_variables")
        self.assertEqual(result["error"]["missing"], ["m", "z"])
        self.assertEqual(result["missing_variables"], ["m", "z"])
        self.assertIn("m", result["error"]["message"])
        self.assertIn("z", result["error"]["message"])
        self.assertIn("strict", result["error"]["message"])

    def test_render_unused_variables_reported_sorted(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="Hello ${name}",
            variables={"name": "Alice", "lang": "en", "extra": "x"},
        )
        self.assertEqual(result["result"], "Hello Alice")
        self.assertEqual(result["unused_variables"], ["extra", "lang"])

    def test_render_all_variables_unused(self) -> None:
        result = self.tool.execute(
            mode="render", template="no placeholders", variables={"a": "1"}
        )
        self.assertEqual(result["result"], "no placeholders")
        self.assertEqual(result["unused_variables"], ["a"])

    def test_render_malformed_template_error_payload(self) -> None:
        result = self.tool.execute(
            mode="render", template="a ${b", variables={"b": "1"}
        )
        self.assertNotIn("result", result)
        self.assertEqual(result["error"]["type"], "malformed_template")
        self.assertEqual(result["error"]["index"], 2)

    def test_render_is_deterministic(self) -> None:
        kwargs = {
            "mode": "render",
            "template": "${a} $b $$ ${c}",
            "variables": {"a": "1", "c": "3"},
            "missing_policy": "keep",
        }
        self.assertEqual(self.tool.execute(**kwargs), self.tool.execute(**kwargs))

    # ------------------------------------------------------------------ #
    # extract mode
    # ------------------------------------------------------------------ #

    def test_extract_unique_names_in_first_appearance_order(self) -> None:
        result = self.tool.execute(mode="extract", template="$b ${a} $b ${a} $c")
        self.assertEqual(
            result,
            {
                "mode": "extract",
                "placeholder_style": "dollar",
                "placeholders": ["b", "a", "c"],
                "count": 3,
            },
        )

    def test_extract_no_placeholders(self) -> None:
        result = self.tool.execute(mode="extract", template="plain text only")
        self.assertEqual(result["placeholders"], [])
        self.assertEqual(result["count"], 0)

    def test_extract_escape_is_not_a_placeholder(self) -> None:
        result = self.tool.execute(mode="extract", template="$$name and $$")
        self.assertEqual(result["placeholders"], [])
        self.assertEqual(result["count"], 0)

    def test_extract_variables_validated_but_not_used(self) -> None:
        result = self.tool.execute(
            mode="extract",
            template="$a",
            variables={"a": "x", "unused": "y"},
        )
        self.assertEqual(result["placeholders"], ["a"])
        self.assertNotIn("unused_variables", result)

    def test_extract_malformed_template_error_payload(self) -> None:
        result = self.tool.execute(mode="extract", template="x ${y")
        self.assertNotIn("placeholders", result)
        self.assertEqual(result["error"]["type"], "malformed_template")
        self.assertEqual(result["error"]["index"], 2)

    # ------------------------------------------------------------------ #
    # validate mode — positions are hand-computed
    # ------------------------------------------------------------------ #

    def test_validate_valid_template(self) -> None:
        result = self.tool.execute(
            mode="validate", template="Hello ${name}, bye $x $$"
        )
        self.assertEqual(
            result,
            {
                "mode": "validate",
                "placeholder_style": "dollar",
                "valid": True,
                "placeholders": ["name", "x"],
                "count": 2,
            },
        )

    def test_validate_trailing_dollar(self) -> None:
        result = self.tool.execute(mode="validate", template="a $")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "malformed_template")
        self.assertEqual(result["error"]["index"], 2)
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["col"], 3)
        self.assertIn("line 1, column 3", result["error"]["message"])

    def test_validate_unclosed_braced_placeholder(self) -> None:
        result = self.tool.execute(mode="validate", template="a ${b c}")
        # "$" sits at index 2 ("a "): the braced name "b" is followed by
        # a space, not the closing "}", so the placeholder is malformed.
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["index"], 2)
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["col"], 3)

    def test_validate_dollar_before_digit(self) -> None:
        result = self.tool.execute(mode="validate", template="cost: $5")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["index"], 6)
        self.assertEqual(result["error"]["col"], 7)

    def test_validate_dollar_before_space(self) -> None:
        result = self.tool.execute(mode="validate", template="$ x")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["index"], 0)
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["col"], 1)

    def test_validate_lone_dollar(self) -> None:
        result = self.tool.execute(mode="validate", template="$")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["index"], 0)

    def test_validate_third_dollar_after_escape(self) -> None:
        # "$$$" is the "$$" escape followed by a trailing bare "$".
        result = self.tool.execute(mode="validate", template="$$$")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["index"], 2)

    def test_validate_nested_braces(self) -> None:
        result = self.tool.execute(mode="validate", template="${x${y}")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["index"], 0)
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["col"], 1)

    def test_validate_position_on_multiline_template(self) -> None:
        # "line1\nline2 ${x" — the "${" opens at index 12, on line 2
        # right after the six characters of "line2 ".
        result = self.tool.execute(mode="validate", template="line1\nline2 ${x")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["index"], 12)
        self.assertEqual(result["error"]["line"], 2)
        self.assertEqual(result["error"]["col"], 7)

    def test_validate_underscore_and_digit_names(self) -> None:
        result = self.tool.execute(mode="validate", template="$_x1 ${_y2}")
        self.assertEqual(result["valid"], True)
        self.assertEqual(result["placeholders"], ["_x1", "_y2"])

    # ------------------------------------------------------------------ #
    # brace placeholder style ($-free grammar)
    # ------------------------------------------------------------------ #

    def test_brace_render_basic(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="Hello {{name}}!",
            variables={"name": "Alice"},
            placeholder_style="brace",
        )
        self.assertEqual(result["placeholder_style"], "brace")
        self.assertEqual(result["result"], "Hello Alice!")
        self.assertEqual(result["placeholders"], ["name"])

    def test_brace_render_dollar_is_literal(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="cost: $5 {{name}} (shell: $$HOME)",
            variables={"name": "Alice"},
            missing_policy="keep",
            placeholder_style="brace",
        )
        # No "$" escaping is needed or performed in brace style.
        self.assertEqual(result["result"], "cost: $5 Alice (shell: $$HOME)")
        self.assertEqual(result["placeholders"], ["name"])

    def test_brace_render_escape_emits_literal_double_brace(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="a {{{{ b",
            variables={},
            placeholder_style="brace",
        )
        self.assertEqual(result["result"], "a {{ b")

    def test_brace_render_single_braces_are_literal(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="{name} {0} {a.b}",
            variables={"name": "x"},
            placeholder_style="brace",
        )
        self.assertEqual(result["result"], "{name} {0} {a.b}")
        self.assertEqual(result["unused_variables"], ["name"])

    def test_brace_render_adjacent_placeholders(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="{{a}}{{b}}",
            variables={"a": "1", "b": "2"},
            placeholder_style="brace",
        )
        self.assertEqual(result["result"], "12")

    def test_brace_render_keep_policy(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="[{{user}}]",
            variables={},
            missing_policy="keep",
            placeholder_style="brace",
        )
        self.assertEqual(result["result"], "[{{user}}]")

    def test_brace_extract(self) -> None:
        result = self.tool.execute(
            mode="extract", template="a {{b}} c {{b}} {{d}}", placeholder_style="brace"
        )
        self.assertEqual(result["placeholders"], ["b", "d"])
        self.assertEqual(result["count"], 2)

    def test_brace_validate_valid(self) -> None:
        result = self.tool.execute(
            mode="validate", template="{{name}} and {{{{", placeholder_style="brace"
        )
        self.assertEqual(result["valid"], True)
        self.assertEqual(result["placeholders"], ["name"])

    def test_brace_validate_malformed_cases(self) -> None:
        for template in ("{{name", "{{name}", "{{1a}}", "{{}}", "{{{"):
            result = self.tool.execute(
                mode="validate", template=template, placeholder_style="brace"
            )
            self.assertEqual(result["valid"], False, template)
            self.assertEqual(result["error"]["type"], "malformed_template")
            self.assertEqual(result["error"]["index"], 0, template)
            self.assertEqual(result["error"]["line"], 1, template)
            self.assertEqual(result["error"]["col"], 1, template)

    def test_brace_render_malformed_error_payload(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="x {{name",
            variables={"name": "Alice"},
            placeholder_style="brace",
        )
        self.assertNotIn("result", result)
        self.assertEqual(result["error"]["type"], "malformed_template")
        self.assertEqual(result["error"]["index"], 2)

    # ------------------------------------------------------------------ #
    # CJK templates and values
    # ------------------------------------------------------------------ #

    def test_cjk_template_and_values(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="你好，${name}！欢迎来到${city}。",
            variables={"name": "小明", "city": "北京"},
        )
        self.assertEqual(result["result"], "你好，小明！欢迎来到北京。")
        self.assertEqual(result["placeholders"], ["name", "city"])
        self.assertEqual(result["unused_variables"], [])

    def test_cjk_with_escape(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="价格：$$5（${cur}）",
            variables={"cur": "¥"},
        )
        self.assertEqual(result["result"], "价格：$5（¥）")

    def test_cjk_extract(self) -> None:
        result = self.tool.execute(
            mode="extract", template="报告${topic}：${author}著"
        )
        self.assertEqual(result["placeholders"], ["topic", "author"])

    def test_cjk_variable_name_reports_unused(self) -> None:
        # Placeholder names must be ASCII identifiers, so a CJK key can
        # never match and is reported back as unused.
        result = self.tool.execute(
            mode="render",
            template="你好，${name}",
            variables={"名字": "小明", "name": "Alice"},
        )
        self.assertEqual(result["result"], "你好，Alice")
        self.assertEqual(result["unused_variables"], ["名字"])

    # ------------------------------------------------------------------ #
    # Error matrix — parameter validation raises ValueError
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="replace", template="$a")
        self.assert_invalid(mode=None, template="$a")
        self.assert_invalid(mode="RENDER", template="$a")

    def test_invalid_template(self) -> None:
        self.assert_invalid(template=None)
        self.assert_invalid(template=123)
        self.assert_invalid(template=True)
        self.assert_invalid(template=["$a"])

    def test_template_length_limit(self) -> None:
        self.assert_invalid(template="x" * 100_001)
        # Exactly at the 100,000-character cap; the space filler keeps
        # the placeholder name from extending over the "x" run.
        result = self.tool.execute(
            mode="extract", template="$a" + " x" * 49_999
        )
        self.assertEqual(len("$a" + " x" * 49_999), 100_000)
        self.assertEqual(result["placeholders"], ["a"])

    def test_invalid_variables_container(self) -> None:
        self.assert_invalid(template="$a", variables=["a"])
        self.assert_invalid(template="$a", variables="a=1")
        self.assert_invalid(template="$a", variables=1)
        self.assert_invalid(template="$a", variables=True)

    def test_invalid_variable_names(self) -> None:
        self.assert_invalid(template="$a", variables={42: "x"})
        self.assert_invalid(template="$a", variables={"": "x"})
        self.assert_invalid(template="$a", variables={True: "x"})

    def test_invalid_variable_values(self) -> None:
        self.assert_invalid(template="$a", variables={"a": None})
        self.assert_invalid(template="$a", variables={"a": ["x"]})
        self.assert_invalid(template="$a", variables={"a": {"b": "x"}})

    def test_variables_entry_limit(self) -> None:
        many = {f"v{i}": i for i in range(501)}
        self.assert_invalid(template="$a", variables=many)

    def test_variable_value_length_limit(self) -> None:
        self.assert_invalid(template="$a", variables={"a": "v" * 100_001})

    def test_invalid_missing_policy(self) -> None:
        self.assert_invalid(
            template="$a", missing_policy="ignore"
        )
        self.assert_invalid(template="$a", missing_policy="STRICT")

    def test_default_value_requires_default_policy(self) -> None:
        self.assert_invalid(template="$a", default_value="-")
        self.assert_invalid(
            template="$a", missing_policy="strict", default_value="-"
        )
        self.assert_invalid(
            template="$a", missing_policy="keep", default_value="-"
        )

    def test_default_policy_requires_default_value(self) -> None:
        self.assert_invalid(template="$a", missing_policy="default")
        self.assert_invalid(
            template="$a", missing_policy="default", default_value=None
        )

    def test_invalid_default_value(self) -> None:
        self.assert_invalid(
            template="$a",
            missing_policy="default",
            default_value=["-"],
        )
        self.assert_invalid(
            template="$a", missing_policy="default", default_value="-" * 100_001
        )

    def test_invalid_placeholder_style(self) -> None:
        self.assert_invalid(template="$a", placeholder_style="mustache")
        self.assert_invalid(template="$a", placeholder_style=1)

    # ------------------------------------------------------------------ #
    # Security — format braces and code are never interpreted
    # ------------------------------------------------------------------ #

    def test_format_brace_sequences_stay_literal(self) -> None:
        template = "{0} {user.__class__} {0.__init__} {{}}"
        result = self.tool.execute(mode="render", template=template, variables={})
        self.assertEqual(result["result"], template)

    def test_values_never_evaluated(self) -> None:
        result = self.tool.execute(
            mode="render",
            template="${expr}",
            variables={"expr": "__import__('os').system('id')"},
        )
        self.assertEqual(result["result"], "__import__('os').system('id')")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectTemplateRenderTool, TemplateRenderTool)
        self.assertEqual(self.tool.name, "template_render_tool")
        self.assertIn("mode='render'", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("TemplateRenderTool", __all__)


if __name__ == "__main__":
    unittest.main()

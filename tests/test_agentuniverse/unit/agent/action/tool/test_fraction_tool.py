"""Offline oracle tests for FractionTool, pinned to fractions.Fraction."""

# Seeded random.Random corpora are deliberate test data (S311); the corpora
# intentionally contain ambiguous-Unicode digit inputs (RUF001); the ast
# reference evaluator is branch-heavy by nature (C901, TRY003).
# ruff: noqa: S311, RUF001, C901, TRY003

import ast
import os
import random
import time
import unittest
from fractions import Fraction

from agentuniverse.agent.action.tool.common_tool import fraction_tool as fraction_module
from agentuniverse.agent.action.tool.common_tool.fraction_tool import FractionTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(fraction_module.__file__), "fraction_tool.yaml")


def multiplicative_order_ten(denominator: int) -> int:
    """Reference multiplicative order of 10 modulo a coprime denominator."""
    value = 10 % denominator
    order = 1
    while value != 1:
        value = value * 10 % denominator
        order += 1
    return order


def strip_two_and_five(denominator: int) -> int:
    """Reference removal of the terminating factors 2 and 5."""
    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    return denominator


class FractionToolParseTest(unittest.TestCase):
    """Deterministic tests for documented parse forms, rules, and rejections."""

    def setUp(self):
        self.tool = FractionTool()

    def test_proper_fraction_reduced(self):
        """Verify '2/4' reduces to '1/2' with the sign on the numerator."""
        result = self.tool.execute("parse", value="2/4")
        self.assertEqual(result["normalized"], "1/2")
        self.assertEqual(result["fraction"], {"numerator": 1, "denominator": 2})
        self.assertEqual(result["form"], "proper")

    def test_mixed_number(self):
        """Verify '1 1/2' parses as three halves."""
        result = self.tool.execute("parse", value="1 1/2")
        self.assertEqual(result["normalized"], "3/2")
        self.assertEqual(result["form"], "mixed")

    def test_negative_mixed_number(self):
        """Verify '-2 3/8' applies the negative sign to the whole value."""
        result = self.tool.execute("parse", value="-2 3/8")
        self.assertEqual(result["normalized"], "-19/8")
        self.assertEqual(result["form"], "mixed")
        self.assertEqual(result["issues"], [])

    def test_mixed_sign_placement_rule(self):
        """Verify '2 -1/2' equals '-2 1/2' and documents the applied rule."""
        moved = self.tool.execute("parse", value="2 -1/2")
        leading = self.tool.execute("parse", value="-2 1/2")
        self.assertEqual(moved["normalized"], "-5/2")
        self.assertEqual(leading["normalized"], "-5/2")
        self.assertIn("applied to the whole value", moved["issues"][0])
        self.assertEqual(leading["issues"], [])

    def test_mixed_double_negative_signs(self):
        """Verify signs on both mixed parts multiply to a positive value."""
        result = self.tool.execute("parse", value="-2 -1/2")
        self.assertEqual(result["normalized"], "5/2")
        self.assertTrue(any("multiplied" in issue for issue in result["issues"]))

    def test_mixed_improper_fractional_part(self):
        """Verify '2 3/2' parses as seven halves with an advisory issue."""
        result = self.tool.execute("parse", value="2 3/2")
        self.assertEqual(result["normalized"], "7/2")
        self.assertTrue(any("not proper" in issue for issue in result["issues"]))

    def test_all_vulgar_characters(self):
        """Verify every supported vulgar character maps to its exact value."""
        for character, (numerator, denominator) in fraction_module._VULGAR_VALUES.items():
            result = self.tool.execute("parse", value=character)
            self.assertEqual(result["normalized"], str(Fraction(numerator, denominator)), character)
            self.assertEqual(result["form"], "vulgar", character)
            signed = self.tool.execute("parse", value=f"-{character}")
            self.assertEqual(signed["normalized"], str(Fraction(-numerator, denominator)), character)

    def test_decimal_and_scientific_forms(self):
        """Verify decimal and scientific strings parse exactly."""
        self.assertEqual(self.tool.execute("parse", value="0.75")["normalized"], "3/4")
        self.assertEqual(self.tool.execute("parse", value="-2.5")["normalized"], "-5/2")
        self.assertEqual(self.tool.execute("parse", value="1.5e-3")["normalized"], "3/2000")
        self.assertEqual(self.tool.execute("parse", value="7")["normalized"], "7")
        self.assertEqual(self.tool.execute("parse", value="7")["form"], "integer")

    def test_zero_denominator_rejected(self):
        """Verify '3/0' and mixed zero denominators fail cleanly."""
        for bad in ("3/0", "1 2/0", "-4/0"):
            result = self.tool.execute("parse", value=bad)
            self.assertEqual(result["status"], "error", bad)
            self.assertIn("zero denominator", result["error"], bad)

    def test_leading_zeros_accepted(self):
        """Verify leading zeros are fine in either part."""
        result = self.tool.execute("parse", value="007/002")
        self.assertEqual(result["normalized"], "7/2")

    def test_negative_zero_pin(self):
        """Verify '-0/5' equals zero, byte-equal with str(Fraction('-0/5'))."""
        expected = Fraction("-0/5")
        self.assertEqual(expected, 0)
        result = self.tool.execute("parse", value="-0/5")
        self.assertEqual(result["normalized"], str(expected))
        self.assertEqual(result["fraction"], {"numerator": 0, "denominator": 1})

    def test_denominator_sign_normalized(self):
        """Verify '1/-2' and '-1/-2' move the sign onto the numerator."""
        first = self.tool.execute("parse", value="1/-2")
        self.assertEqual(first["normalized"], "-1/2")
        self.assertTrue(any("denominator" in issue for issue in first["issues"]))
        second = self.tool.execute("parse", value="-1/-2")
        self.assertEqual(second["normalized"], "1/2")

    def test_huge_numerator(self):
        """Verify a 10^50-scale numerator parses without loss."""
        numerator = 10**50 + 12345
        result = self.tool.execute("parse", value=f"{numerator}/3")
        self.assertEqual(result["normalized"], str(Fraction(numerator, 3)))

    def test_rejected_values(self):
        """Verify malformed values are rejected with structured errors."""
        for bad in ("0x1/2", "½⅓", "1 2/3 4", "", "   ", "abc", "1/2/3", "3/", "/4", "1.2.3", "(1/2)", "nan", "inf"):
            result = self.tool.execute("parse", value=bad)
            self.assertEqual(result["status"], "error", bad)
            self.assertFalse(result["ok"], bad)

    def test_non_ascii_digits_require_normalize(self):
        """Verify fullwidth and Arabic-Indic digits are rejected unless normalized."""
        for text in ("１/2", "1/２", "١/2"):
            result = self.tool.execute("parse", value=text)
            self.assertEqual(result["status"], "error", text)
            self.assertIn("normalize=True", result["error"], text)
            normalized = self.tool.execute("parse", value=text, normalize=True)
            self.assertEqual(normalized["status"], "success", text)
            self.assertEqual(normalized["normalized"], "1/2", text)
            self.assertTrue(any("NFKC" in issue for issue in normalized["issues"]), text)

    def test_improper_form_classification(self):
        """Verify as-written fractions classify as proper or improper."""
        self.assertEqual(self.tool.execute("parse", value="5/4")["form"], "improper")
        self.assertEqual(self.tool.execute("parse", value="10/2")["form"], "improper")
        self.assertEqual(self.tool.execute("parse", value="10/2")["normalized"], "5")
        self.assertEqual(self.tool.execute("parse", value="3/4")["form"], "proper")


class FractionOracleParseFuzzTest(unittest.TestCase):
    """600 seeded values: parse verdicts and arithmetic byte-equal with Fraction."""

    def setUp(self):
        self.tool = FractionTool()
        rng = random.Random(252)
        vulgar = sorted(fraction_module._VULGAR_VALUES)
        cases = []
        for index in range(600):
            kind = index % 8
            if kind == 0:
                numerator, denominator = rng.randint(-50, 50), rng.randint(1, 50)
                cases.append((f"{numerator}/{denominator}", Fraction(numerator, denominator)))
            elif kind == 1:
                whole, denominator = rng.randint(0, 20), rng.randint(2, 10)
                numerator = rng.randint(1, denominator - 1)
                sign = rng.choice(("", "-"))
                cases.append(
                    (
                        f"{sign}{whole} {numerator}/{denominator}",
                        int(sign + "1") * (whole + Fraction(numerator, denominator)),
                    )
                )
            elif kind == 2:
                character = vulgar[rng.randrange(len(vulgar))]
                numerator, denominator = fraction_module._VULGAR_VALUES[character]
                sign = rng.choice(("", "-"))
                cases.append((f"{sign}{character}", int(sign + "1") * Fraction(numerator, denominator)))
            elif kind == 3:
                text = f"{rng.randint(0, 999)}.{rng.randint(0, 9999)}"
                cases.append((text, Fraction(text)))
            elif kind == 4:
                mantissa = f"{rng.randint(1, 99)}.{rng.randint(1, 99)}"
                exponent = rng.randint(-6, 6)
                text = f"{mantissa}e{exponent}"
                cases.append((text, Fraction(text)))
            elif kind == 5:
                number = rng.randint(-(10**6), 10**6)
                cases.append((str(number), Fraction(number)))
            elif kind == 6:
                numerator, denominator = rng.randint(1, 60), rng.randint(1, 60)
                sign = rng.choice(("/", "/-", "-/", "-/-"))
                value = Fraction(numerator, denominator)
                if sign.count("-") % 2 == 1:
                    value = -value
                cases.append((self._signed_slash(sign, numerator, denominator), value))
            else:
                numerator = rng.randint(10**40, 10**50)
                denominator = rng.randint(10**20, 10**30)
                cases.append((f"{numerator}/{denominator}", Fraction(numerator, denominator)))
        mutations = [
            ("3/0", None),
            ("1 2/3 4", None),
            ("½⅓", None),
            ("0x1/2", None),
            ("-0/5", Fraction("-0/5")),
            ("1/-2", Fraction(1, -2)),
            ("2 -1/2", Fraction(-5, 2)),
            (f"{10**50}/1", Fraction(10**50, 1)),
        ]
        self.cases = cases + mutations

    @staticmethod
    def _signed_slash(sign: str, numerator: int, denominator: int) -> str:
        left = "-" if sign.startswith("-") else ""
        right = "-" if sign.endswith("-") else ""
        return f"{left}{numerator}/{right}{denominator}"

    def test_parse_verdicts_match_fraction(self):
        """Verify every seeded value normalizes byte-equal to its Fraction value."""
        for text, expected in self.cases:
            result = self.tool.execute("parse", value=text)
            if expected is None:
                self.assertEqual(result["status"], "error", text)
                self.assertFalse(result["ok"], text)
                continue
            self.assertEqual(result["status"], "success", text)
            self.assertEqual(result["normalized"], str(expected), text)
            self.assertEqual(result["fraction"]["numerator"], expected.numerator, text)
            self.assertEqual(result["fraction"]["denominator"], expected.denominator, text)
            self.assertIn(result["form"], {"proper", "improper", "mixed", "integer", "vulgar", "decimal"}, text)

    def test_stdlib_accepted_values_byte_equal(self):
        """Verify values Fraction() itself accepts match str(Fraction(...))."""
        checked = 0
        for text, expected in self.cases:
            if expected is None:
                continue
            try:
                direct = Fraction(text)
            except (ValueError, ZeroDivisionError):
                continue
            self.assertEqual(self.tool.execute("parse", value=text)["normalized"], str(direct), text)
            checked += 1
        self.assertGreater(checked, 300)

    def test_arithmetic_matches_fraction_operations(self):
        """Verify single operations agree byte-equal with Fraction arithmetic."""
        rng = random.Random(2521)
        operations = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
        }
        usable = [expected for _, expected in self.cases if expected is not None]
        for _ in range(len(self.cases)):
            left = rng.choice(usable)
            right = rng.choice(usable)
            operator = rng.choice("+-*/")
            if operator == "/" and right == 0:
                operator = "+"
            expected = operations[operator](left, right)
            result = self.tool.execute("compute", expression=f"({left}) {operator} ({right})")
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["result"], str(expected))
            self.assertEqual(result["steps"], [f"{left} {operator} {right} = {expected}"])


class FractionExpressionFuzzTest(unittest.TestCase):
    """500 seeded expressions against an ast-walked Fraction evaluator."""

    EXACT_DECIMALS = ("0.5", "0.25", "0.75", "1.25", "2.5", "0.125", "3.75")

    def setUp(self):
        self.tool = FractionTool()

    @staticmethod
    def evaluate(expression: str) -> Fraction:
        """Evaluate the same expression through ast with Fraction leaves."""

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant):
                return Fraction(node.value)
            if isinstance(node, ast.UnaryOp):
                if isinstance(node.op, ast.USub):
                    return -visit(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return visit(node.operand)
            if isinstance(node, ast.BinOp):
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                if isinstance(node.op, ast.Sub):
                    return left - right
                if isinstance(node.op, ast.Mult):
                    return left * right
                if isinstance(node.op, ast.Div):
                    return left / right
            raise AssertionError(f"unexpected node {node}")

        return visit(ast.parse(expression, mode="eval"))

    @staticmethod
    def count_nodes(expression: str):
        """Count BinOp nodes and glued slash literals inside the expression."""
        tree = ast.parse(expression, mode="eval")
        operations = sum(isinstance(node, ast.BinOp) for node in ast.walk(tree))
        tokens = fraction_module._ExpressionParser(FractionTool(), expression).tokens
        literals = sum("/" in lexeme and lexeme != "/" for lexeme in tokens)
        return operations, literals

    def build(self, rng: random.Random, depth: int) -> str:
        """Build a random expression over fraction, decimal, and int literals."""
        if depth == 0 or rng.random() < 0.3:
            roll = rng.random()
            if roll < 0.4:
                return str(rng.randint(1, 99))
            if roll < 0.8:
                return f"{rng.randint(1, 99)}/{rng.randint(2, 99)}"
            return rng.choice(self.EXACT_DECIMALS)
        left = self.build(rng, depth - 1)
        right = self.build(rng, depth - 1)
        operator = rng.choice("+-*/")
        if operator == "/" and rng.random() < 0.08:
            right = "0"
        text = f"{left} {operator} {right}"
        if rng.random() < 0.4:
            text = f"({text})"
        if rng.random() < 0.2:
            text = f"-{text}"
        return text

    def test_fuzz_matches_ast_oracle(self):
        """Verify 500 seeded expressions and per-operation audit steps."""
        rng = random.Random(2520)
        divisions_by_zero = 0
        for _ in range(500):
            expression = self.build(rng, rng.randint(1, 4))
            try:
                expected = self.evaluate(expression)
                error_expected = False
            except ZeroDivisionError:
                error_expected = True
            result = self.tool.execute("compute", expression=expression)
            if error_expected:
                divisions_by_zero += 1
                self.assertEqual(result["status"], "error", expression)
                self.assertEqual(result["error_type"], "arithmetic_error", expression)
                continue
            self.assertEqual(result["status"], "success", expression)
            self.assertEqual(result["result"], str(expected), expression)
            operations, literals = self.count_nodes(expression)
            self.assertEqual(len(result["steps"]), operations - literals, expression)
            self.assertTrue(self._steps_verify(result["steps"]), expression)
        self.assertGreater(divisions_by_zero, 0)

    @staticmethod
    def _steps_verify(steps: list[str]) -> bool:
        """Verify each audit step recomputes exactly with Fraction."""
        operators = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}
        for step in steps:
            left, operator, right, _, product = step.split(" ")
            if operators[operator](Fraction(left), Fraction(right)) != Fraction(product):
                return False
        return True

    def test_precedence_and_unary(self):
        """Verify precedence, parentheses, unary minus, and whitespace."""
        cases = {
            "1 + 2 * 3": Fraction(7),
            "1/2 + 1/2": Fraction(1),
            "2 * 3/4": Fraction(3, 2),
            "(1 + 1/2) / (1/6)": Fraction(9),
            "--5": Fraction(5),
            "-(1/2 + 1/2)": Fraction(-1),
            "  1/2   +   1/4 ": Fraction(3, 4),
            "½ + ⅓": Fraction(5, 6),
        }
        for expression, expected in cases.items():
            result = self.tool.execute("compute", expression=expression)
            self.assertEqual(result["result"], str(expected), expression)

    def test_left_associative_division_chains(self):
        """Verify slash literals inside division chains divide left-to-right."""
        cases = {
            "3.75 / 80/45": Fraction("3.75") / 80 / 45,
            "1/2 / 3/4": Fraction(1, 2) / 3 / 4,
            "35/14 / 14 / 49": Fraction(35, 14) / 14 / 49,
            "2/3/4": Fraction(2, 3) / 4,
            "4/8/2": Fraction(4, 8) / 2,
            "7 / -82/82": Fraction(7) / -82 / 82,
            "7 / --82/82": Fraction(7) / 82 / 82,
            "9 / (3/4)": Fraction(9) / Fraction(3, 4),
            "5 * -3/4": 5 * Fraction(-3, 4),
        }
        for expression, expected in cases.items():
            result = self.tool.execute("compute", expression=expression)
            self.assertEqual(result["result"], str(expected), expression)

    def test_mixed_operands_rejected_in_expressions(self):
        """Verify mixed-number operands fail with a structured error."""
        result = self.tool.execute("compute", expression="-2 3/8 + 1")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_literal_zero_denominator_in_expression(self):
        """Verify a '3/0' literal inside an expression reports arithmetic_error."""
        result = self.tool.execute("compute", expression="1/2 + 3/0")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "arithmetic_error")

    def test_division_by_zero_reports_step(self):
        """Verify operator division by zero names the failing step."""
        result = self.tool.execute("compute", expression="1 / (1 - 1)")
        self.assertEqual(result["status"], "error")
        self.assertIn("division by zero", result["error"])

    def test_preview_detects_repetend(self):
        """Verify the compute decimal preview marks repeating expansions."""
        result = self.tool.execute("compute", expression="1/2 / 3")
        self.assertEqual(result["result"], "1/6")
        self.assertEqual(result["decimal_preview"], "0.1(6)")
        long_period = self.tool.execute("compute", expression="1/97")
        self.assertTrue(long_period["decimal_preview"].endswith("…"))


class FractionRepeatingDecimalTest(unittest.TestCase):
    """Classic repeating-decimal table plus number-theoretic period checks."""

    def setUp(self):
        self.tool = FractionTool()

    def test_classic_table(self):
        """Verify expansions and periods for the classic denominators."""
        table = [
            ("1/3", "0.(3)", 1, False),
            ("1/6", "0.1(6)", 1, False),
            ("1/7", "0.(142857)", 6, False),
            ("22/7", "3.(142857)", 6, False),
            ("1/2", "0.5", 0, True),
            ("1/8", "0.125", 0, True),
        ]
        for value, decimal, period, terminating in table:
            result = self.tool.execute("to_decimal", value=value, max_digits=30)
            self.assertEqual(result["decimal"], decimal, value)
            self.assertEqual(result["period_length"], period, value)
            self.assertEqual(result["terminating"], terminating, value)
            self.assertFalse(result["truncated"], value)
            denominator = Fraction(value).denominator
            core = strip_two_and_five(denominator)
            if core > 1:
                self.assertEqual(result["period_length"], multiplicative_order_ten(core), value)

    def test_period_96_for_one_over_97(self):
        """Verify 1/97 reports period 96 whether shown fully or truncated."""
        digits, remainders, remainder = [], {}, 1
        while remainder not in remainders:
            remainders[remainder] = len(digits)
            remainder *= 10
            quotient, remainder = divmod(remainder, 97)
            digits.append(str(quotient))
        start = remainders[remainder]
        prefix, repetend = "".join(digits[:start]), "".join(digits[start:])
        self.assertEqual(len(repetend), 96)
        full = self.tool.execute("to_decimal", value="1/97", max_digits=200)
        self.assertEqual(full["period_length"], 96)
        self.assertFalse(full["truncated"])
        self.assertEqual(full["repetend"], repetend)
        self.assertEqual(full["decimal"], f"0.{prefix}({repetend})")
        default_digits = self.tool.execute("to_decimal", value="1/97")
        self.assertEqual(default_digits["period_length"], 96)
        self.assertTrue(default_digits["truncated"])
        self.assertIsNone(default_digits["repetend"])
        self.assertEqual(default_digits["digits_emitted"], 30)
        self.assertTrue(default_digits["decimal"].endswith("…"))

    def test_period_capped_for_huge_core(self):
        """Verify a core denominator beyond max_period reports period_capped."""
        capped = FractionTool(max_period=10)
        result = capped.execute("to_decimal", value="1/97", max_digits=5)
        self.assertTrue(result["period_capped"])
        self.assertIsNone(result["period_length"])
        self.assertTrue(result["truncated"])

    def test_scientific_and_repeating_to_fraction(self):
        """Verify exact decimal-string conversion including repetend notation."""
        cases = {
            "0.(3)": Fraction(1, 3),
            "0.1(6)": Fraction(1, 6),
            "2.1(6)": Fraction(13, 6),
            "-2.1(6)": Fraction(-13, 6),
            "0.(142857)": Fraction(1, 7),
            "1.5e-3": Fraction(3, 2000),
            "2.5": Fraction(5, 2),
            ".5": Fraction(1, 2),
            "7": Fraction(7),
        }
        for text, expected in cases.items():
            result = self.tool.execute("to_fraction", value=text)
            self.assertEqual(result["status"], "success", text)
            self.assertEqual(result["normalized"], str(expected), text)
            self.assertTrue(result["exact"], text)

    def test_round_trip_300_fractions(self):
        """Verify to_decimal then to_fraction returns the original fraction."""
        rng = random.Random(2522)
        for _ in range(300):
            denominator = rng.randint(1, 999)
            numerator = rng.randint(-999, 999)
            original = Fraction(numerator, denominator)
            expanded = self.tool.execute("to_decimal", value=f"{numerator}/{denominator}", max_digits=1200)
            self.assertFalse(expanded["truncated"], (numerator, denominator))
            core = strip_two_and_five(original.denominator)
            self.assertEqual(expanded["period_length"], 0 if core == 1 else multiplicative_order_ten(core))
            restored = self.tool.execute("to_fraction", value=expanded["decimal"])
            self.assertEqual(restored["status"], "success", expanded["decimal"])
            self.assertEqual(
                Fraction(restored["fraction"]["numerator"], restored["fraction"]["denominator"]),
                original,
                expanded["decimal"],
            )


class FractionFloatPathTest(unittest.TestCase):
    """Float inputs follow Fraction(float).limit_denominator with error bounds."""

    def setUp(self):
        self.tool = FractionTool()

    def test_200_floats_match_limit_denominator(self):
        """Verify approximation equality and honest exact error bounds."""
        rng = random.Random(2523)
        values = [rng.uniform(-1000, 1000) for _ in range(150)]
        values += [
            0.1,
            0.2,
            0.3,
            1 / 3,
            2 / 3,
            3.141592653589793,
            2.718281828459045,
            1e-7,
            1e9,
            0.5,
            -0.125,
            123456.789,
            -42.75,
            0.9999999999,
        ] * 4
        values = values[:200]
        self.assertEqual(len(values), 200)
        for value in values:
            expected = Fraction(value).limit_denominator(10**6)
            result = self.tool.execute("to_fraction", value=value)
            self.assertEqual(result["status"], "success", value)
            self.assertEqual(result["normalized"], str(expected), value)
            self.assertEqual(result["input_kind"], "float", value)
            exact_error = abs(Fraction(value) - expected)
            self.assertEqual(result["error_bound"]["numerator"], exact_error.numerator, value)
            self.assertEqual(result["error_bound"]["denominator"], exact_error.denominator, value)
            self.assertGreaterEqual(exact_error, 0)
            self.assertEqual(result["exact"], exact_error == 0, value)

    def test_custom_max_denominator(self):
        """Verify the max_denominator override selects coarser approximations."""
        value = 0.35
        result = self.tool.execute("to_fraction", value=value, max_denominator=64)
        self.assertEqual(result["normalized"], str(Fraction(value).limit_denominator(64)))

    def test_non_finite_float_rejected(self):
        """Verify inf and nan floats fail with structured errors."""
        for bad in (float("inf"), float("-inf"), float("nan")):
            result = self.tool.execute("to_fraction", value=bad)
            self.assertEqual(result["status"], "error", bad)
            self.assertIn("finite", result["error"], bad)

    def test_integer_and_bool_inputs(self):
        """Verify ints are exact and bools are rejected."""
        self.assertEqual(self.tool.execute("to_fraction", value=7)["normalized"], "7")
        self.assertTrue(self.tool.execute("to_fraction", value=7)["exact"])
        self.assertEqual(self.tool.execute("to_fraction", value=True)["status"], "error")


class FractionCompareTest(unittest.TestCase):
    """Comparison verdicts with side-by-side decimal previews."""

    def setUp(self):
        self.tool = FractionTool()

    def test_compare_relations(self):
        """Verify less, equal, and greater verdicts across forms."""
        cases = [
            ("-1/2", "1/3", -1, "less"),
            ("1 1/2", "3/2", 0, "equal"),
            ("3/4", "0.7", 1, "greater"),
            ("2 -1/2", "-2 1/2", 0, "equal"),
            ("½", "⅓", 1, "greater"),
        ]
        for left, right, expected, relation in cases:
            result = self.tool.execute("compare", value=left, other=right)
            self.assertEqual(result["status"], "success", (left, right))
            self.assertEqual(result["result"], expected, (left, right))
            self.assertEqual(result["relation"], relation, (left, right))

    def test_compare_previews(self):
        """Verify previews accompany both operands."""
        result = self.tool.execute("compare", value="1/3", other="1/6")
        self.assertEqual(result["a"]["decimal_preview"], "0.(3)")
        self.assertEqual(result["b"]["decimal_preview"], "0.1(6)")


class FractionPathologicalTest(unittest.TestCase):
    """Bounded handling of oversized, deeply nested, and huge-operand inputs."""

    def setUp(self):
        self.tool = FractionTool()

    def test_5000_term_expression_completes(self):
        """Verify a within-cap 4999-term sum evaluates correctly and quickly."""
        expression = "+".join(["1"] * 4999)
        self.assertLess(len(expression), 10_000)
        started = time.monotonic()
        result = self.tool.execute("compute", expression=expression)
        elapsed = time.monotonic() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], "4999")
        self.assertLess(elapsed, 10.0)

    def test_oversized_expression_capped(self):
        """Verify an over-cap expression is rejected immediately by length."""
        expression = "+".join(["1"] * 6000)
        self.assertGreater(len(expression), 10_000)
        started = time.monotonic()
        result = self.tool.execute("compute", expression=expression)
        elapsed = time.monotonic() - started
        self.assertEqual(result["status"], "error")
        self.assertIn("max_expression_length", result["error"])
        self.assertLess(elapsed, 2.0)

    def test_deeply_nested_expression_capped(self):
        """Verify nesting beyond max_parse_depth fails without recursion crash."""
        expression = "(" * 250 + "1" + ")" * 250
        result = self.tool.execute("compute", expression=expression)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_parse_depth", result["error"])

    def test_operation_cap(self):
        """Verify the max_operations cap triggers independently of length."""
        tool = FractionTool(max_expression_length=100_000, max_operations=10)
        result = tool.execute("compute", expression="+".join(["1"] * 20))
        self.assertEqual(result["status"], "error")
        self.assertIn("max_operations", result["error"])

    def test_hundred_digit_denominators_under_two_seconds(self):
        """Verify 100-digit denominators compute and expand under two seconds."""
        left_denominator = 10**100 + 267
        right_denominator = 10**99 + 159
        expression = f"{left_denominator + 1}/{left_denominator} + {right_denominator + 1}/{right_denominator}"
        started = time.monotonic()
        result = self.tool.execute("compute", expression=expression)
        elapsed = time.monotonic() - started
        expected = Fraction(left_denominator + 1, left_denominator) + Fraction(right_denominator + 1, right_denominator)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], str(expected))
        self.assertLess(elapsed, 2.0)
        started = time.monotonic()
        expanded = self.tool.execute("to_decimal", value=f"1/{left_denominator}", max_digits=1000)
        elapsed = time.monotonic() - started
        self.assertEqual(expanded["status"], "success")
        self.assertTrue(expanded["truncated"])
        self.assertEqual(expanded["digits_emitted"], 1000)
        self.assertLess(elapsed, 2.0)

    def test_max_digits_parameter_bounds(self):
        """Verify the max_digits parameter is range checked."""
        for bad in (0, -1, 10_001, 1_000_000):
            result = self.tool.execute("to_decimal", value="1/3", max_digits=bad)
            self.assertEqual(result["status"], "error", bad)
        ok = self.tool.execute("to_decimal", value="1/3", max_digits=10_000)
        self.assertEqual(ok["status"], "success")

    def test_invalid_mode_and_types(self):
        """Verify invalid modes and wrong types return structured errors."""
        self.assertEqual(self.tool.execute("parse", value=123)["status"], "error")
        self.assertEqual(self.tool.execute("lcm", value="1/2")["status"], "error")
        self.assertEqual(self.tool.execute("compute", expression=None)["status"], "error")
        self.assertEqual(self.tool.execute("compare", value="1/2")["status"], "error")
        self.assertEqual(self.tool.execute("parse", value="1/2", normalize="yes")["status"], "error")


class HostileReviewRegressionTest(unittest.TestCase):
    """Regressions found by a fresh hostile probe battery (independent seeds and oracles)."""

    def setUp(self):
        self.tool = FractionTool()

    def test_repeating_notation_accepted_by_all_string_modes(self):
        """The docstring promises repeating notation support; parse/to_decimal/compare must honor it."""
        parsed = self.tool.execute("parse", value="0.1(6)")
        self.assertEqual(parsed["status"], "success")
        self.assertEqual(parsed["normalized"], "1/6")
        self.assertEqual(parsed["form"], "repeating")
        expanded = self.tool.execute("to_decimal", value="2.1(6)")
        self.assertEqual(expanded["status"], "success")
        self.assertEqual(expanded["decimal"], "2.1(6)")
        self.assertEqual(expanded["fraction"], {"numerator": 13, "denominator": 6})
        compared = self.tool.execute("compare", value="0.(3)", other="1/3")
        self.assertEqual(compared["status"], "success")
        self.assertEqual(compared["relation"], "equal")
        # degenerate forms stay rejected
        for bad in ("(3)", "0.()", "1.(2"):
            self.assertEqual(self.tool.execute("parse", value=bad)["status"], "error", bad)

    def test_truncated_expansion_does_not_claim_a_cycle_start(self):
        """cycle_start must be None when truncation hides the cycle (true start unknowable)."""
        truncated = self.tool.execute("to_decimal", value="1/97", max_digits=5)
        self.assertTrue(truncated["truncated"])
        self.assertIsNone(truncated["repetend"])
        self.assertIsNone(truncated["cycle_start"], "1/97's cycle starts at digit 0, not at the truncation point")
        self.assertEqual(truncated["period_length"], 96)
        full = self.tool.execute("to_decimal", value="1/97", max_digits=200)
        self.assertFalse(full["truncated"])
        self.assertEqual(full["cycle_start"], 0)
        terminating = self.tool.execute("to_decimal", value="1/2")
        self.assertFalse(terminating["truncated"])
        self.assertEqual(terminating["cycle_start"], 1)
        self.assertEqual(terminating["period_length"], 0)


class FractionToolRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped fraction_tool.yaml component."""

    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "FractionTool")

    def test_manager(self):
        """Verify the FractionTool is resolvable and configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, FractionTool)
        self.assertEqual(tool.input_keys, ["mode", "value"])
        self.assertEqual(tool.max_digits, 30)
        self.assertEqual(tool.max_denominator, 1_000_000)


if __name__ == "__main__":
    unittest.main()

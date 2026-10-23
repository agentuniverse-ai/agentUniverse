# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for `simple_math_tool`.

The four tools in that module had no coverage at all. They take a string of two
comma-separated numbers and return a float, so the interesting behaviour is the
input contract: whitespace tolerance, scientific notation, and what happens on
malformed input. Each expectation below was recorded from the current
implementation rather than assumed.
"""

import asyncio
import inspect
import unittest

from agentuniverse.agent.action.tool.common_tool.simple_math_tool import (
    AddTool,
    DivideTool,
    MultiplyTool,
    SubtractTool,
)
from agentuniverse.agent.action.tool.tool import Tool

TOOLS = (AddTool, SubtractTool, MultiplyTool, DivideTool)


class SimpleMathToolInstantiationTest(unittest.TestCase):
    """The tools must be usable as plain `Tool` components."""

    def test_every_class_is_a_tool(self):
        for cls in TOOLS:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(issubclass(cls, Tool))

    def test_every_class_instantiates_without_configuration(self):
        for cls in TOOLS:
            with self.subTest(cls=cls.__name__):
                self.assertIsInstance(cls(), Tool)

    def test_every_class_exposes_both_sync_and_async_entry_points(self):
        for cls in TOOLS:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(callable(cls().execute))
                self.assertTrue(inspect.iscoroutinefunction(cls.async_execute))


class SimpleMathToolArithmeticTest(unittest.TestCase):
    """The arithmetic itself, one case per operator."""

    def test_addition(self):
        self.assertEqual(AddTool().execute("1,2"), 3.0)

    def test_subtraction_keeps_the_operand_order(self):
        self.assertEqual(SubtractTool().execute("5,2"), 3.0)
        self.assertEqual(SubtractTool().execute("2,5"), -3.0)

    def test_multiplication(self):
        self.assertEqual(MultiplyTool().execute("3,4"), 12.0)

    def test_division_keeps_the_operand_order(self):
        self.assertEqual(DivideTool().execute("8,2"), 4.0)
        self.assertEqual(DivideTool().execute("2,8"), 0.25)

    def test_results_are_floats_even_for_whole_numbers(self):
        for cls, text in ((AddTool, "1,2"), (MultiplyTool, "3,4")):
            with self.subTest(cls=cls.__name__):
                self.assertIsInstance(cls().execute(text), float)


class SimpleMathToolInputContractTest(unittest.TestCase):
    """What the parsing accepts, measured on the current implementation."""

    def test_surrounding_whitespace_is_tolerated(self):
        self.assertEqual(AddTool().execute("1, 2"), 3.0)
        self.assertEqual(AddTool().execute("  1 , 2  "), 3.0)

    def test_negative_and_decimal_operands(self):
        self.assertEqual(AddTool().execute("-1,2"), 1.0)
        self.assertEqual(AddTool().execute("1.5,2.5"), 4.0)

    def test_scientific_notation_is_accepted(self):
        self.assertEqual(AddTool().execute("1e3,2"), 1002.0)

    def test_zero_is_a_valid_operand_for_the_non_dividing_tools(self):
        self.assertEqual(AddTool().execute("1,0"), 1.0)
        self.assertEqual(MultiplyTool().execute("7,0"), 0.0)


class SimpleMathToolErrorTest(unittest.TestCase):
    """Malformed input raises rather than returning a sentinel."""

    def test_three_operands_are_rejected(self):
        with self.assertRaises(ValueError):
            AddTool().execute("1,2,3")

    def test_an_empty_string_is_rejected(self):
        with self.assertRaises(ValueError):
            AddTool().execute("")

    def test_a_single_operand_is_rejected(self):
        with self.assertRaises(ValueError):
            AddTool().execute("1")

    def test_a_non_numeric_operand_is_rejected(self):
        with self.assertRaises(ValueError):
            AddTool().execute("abc,1")

    def test_division_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            DivideTool().execute("1,0")

    def test_the_other_tools_do_not_raise_on_a_zero_second_operand(self):
        for cls, text in ((AddTool, "1,0"), (SubtractTool, "1,0"), (MultiplyTool, "1,0")):
            with self.subTest(cls=cls.__name__):
                self.assertIsInstance(cls().execute(text), float)


class SimpleMathToolAsyncTest(unittest.TestCase):
    """`async_execute` mirrors `execute`, including the error cases."""

    def test_async_results_match_the_synchronous_ones(self):
        loop = asyncio.new_event_loop()
        try:
            for cls, text, expected in (
                (AddTool, "1,2", 3.0),
                (SubtractTool, "5,2", 3.0),
                (MultiplyTool, "3,4", 12.0),
                (DivideTool, "8,2", 4.0),
            ):
                with self.subTest(cls=cls.__name__):
                    self.assertEqual(loop.run_until_complete(cls().async_execute(text)), expected)
        finally:
            loop.close()

    def test_async_division_by_zero_raises(self):
        loop = asyncio.new_event_loop()
        try:
            with self.assertRaises(ZeroDivisionError):
                loop.run_until_complete(DivideTool().async_execute("1,0"))
        finally:
            loop.close()

    def test_async_rejects_malformed_input_like_the_sync_path(self):
        loop = asyncio.new_event_loop()
        try:
            with self.assertRaises(ValueError):
                loop.run_until_complete(AddTool().async_execute("1,2,3"))
        finally:
            loop.close()


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_command_arg_lexer_tool.py

"""Offline unit tests for CommandArgLexerTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: ``lex`` results are checked against literal ground
truths, cross-checked against Python's ``shlex.split`` on a corpus of
command lines that avoids the three documented divergences (``\\$``
and ``\\` `` inside double quotes, backslash-newline, trailing
backslash / unterminated quotes), ``join`` results against minimal-
quoting ground truths, and the ``lex(join(argv)) == argv`` round-trip
property over 200 seeded random argv lists. ``count`` classification
(including the ``--`` separator and ``flag=value`` splitting) and the
full error matrices are pinned as well.
"""

import os
import random
import shlex
import sys
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import CommandArgLexerTool
from agentuniverse.agent.action.tool.common_tool.command_arg_lexer_tool import (
    CommandArgLexerTool as DirectCommandArgLexerTool,
)

# --------------------------------------------------------------------- #
# Corpora
# --------------------------------------------------------------------- #

# Command lines on which this tool's tokenizer must agree EXACTLY with
# Python's shlex.split. They avoid the three deliberate divergences:
# no \$ or \` inside double quotes, no backslash-newline anywhere, and
# no unterminated quote or trailing backslash.
SHLEX_SAFE_CORPUS = [
    "cp file1 file2",
    "ls -la /tmp",
    "echo hello   world",
    "echo\ttab\tseparated",
    "sort a\nb\nc",
    "  trim leading and trailing  ",
    "echo 'single quoted arg'",
    "echo 'a  b' 'c d'",
    'echo "double quoted arg"',
    'echo "a  b" "c d"',
    "echo 'mixed \"inside\" quotes'",
    "echo \"mixed 'inside' quotes\"",
    "echo a\"b c\"d",
    "'a'b\"c\"",
    "pre'post'post",
    "pre\"post\"post",
    "echo it\\'s",
    'echo "she said \\"hi\\""',
    'echo "back\\\\slash"',
    "echo back\\\\slash",
    "echo a\\ b",
    "echo \\$HOME",
    "echo $HOME ${HOME} $5 $? $$ $",
    'echo "$HOME/x"',
    "echo #not-a-comment ; ls",
    "echo * ? [a-z] ~",
    "grep -e pattern -- file.txt || true",
    "tar -czf out.tar.gz dir1 dir2",
    "prog '' arg",
    'prog "" arg',
    "'' ",
    '""',
    "p\x0bq p\x0cq",
    "héllo wörld",
    "PYTHONPATH=/tmp python -c 'print(1)'",
    "ssh user@host 'cd /tmp && ls -l'",
    "echo 'a'b\"c\"d'e'f",
    "x='a b' y=\"c d\" echo",
]

# Nasty alphabet for the seeded round-trip property: quotes, escapes,
# whitespace, dollar, unicode.
ROUND_TRIP_ALPHABET = "ab-'\"\\ \t=/$.;xé🌍"


class CommandArgLexerToolTest(unittest.TestCase):
    """Offline deterministic test cases for CommandArgLexerTool."""

    def setUp(self) -> None:
        self.tool = CommandArgLexerTool()

    # ------------------------------------------------------------------ #
    # Registration and metadata
    # ------------------------------------------------------------------ #

    def test_package_export_and_defaults(self) -> None:
        self.assertIs(DirectCommandArgLexerTool, CommandArgLexerTool)
        self.assertEqual(self.tool.name, "command_arg_lexer_tool")
        self.assertEqual(
            DirectCommandArgLexerTool.MODES, ("lex", "join", "count")
        )
        self.assertIn("WITHOUT execution", self.tool.description)

    def test_yaml_config_matches_module(self) -> None:
        # Resolve through the imported module object (pydantic model
        # classes do not expose __file__ directly).
        module = sys.modules[DirectCommandArgLexerTool.__module__]
        path = os.path.join(
            os.path.dirname(module.__file__), "command_arg_lexer_tool.yaml"
        )
        with open(path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "command_arg_lexer_tool")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool."
            "command_arg_lexer_tool",
        )
        self.assertEqual(config["metadata"]["class"], "CommandArgLexerTool")
        self.assertEqual(config["args_model_schema"]["required"], ["mode"])

    def test_deterministic_output(self) -> None:
        first = self.tool.execute(mode="lex", command_line="a 'b c' d")
        second = self.tool.execute(mode="lex", command_line="a 'b c' d")
        self.assertEqual(first, second)
        self.assertEqual(
            first,
            {"mode": "lex", "expand_vars": False, "argv": ["a", "b c", "d"], "argc": 3},
        )

    # ------------------------------------------------------------------ #
    # lex mode — ground truths
    # ------------------------------------------------------------------ #

    def test_lex_basic_splitting(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="lex", command_line="cp file1 file2")["argv"],
            ["cp", "file1", "file2"],
        )

    def test_lex_whitespace_variants_separate_words(self) -> None:
        for line in ("a\tb", "a\nb", "a\rb", "a \t\r\n b", "  a  ", "\n\n"):
            if line == "\n\n":
                self.assertEqual(
                    self.tool.execute(mode="lex", command_line=line)["argv"], []
                )
            else:
                self.assertEqual(
                    self.tool.execute(mode="lex", command_line=line)["argv"],
                    [part for part in line.split() if part.isalnum()],
                )

    def test_lex_empty_and_blank_lines(self) -> None:
        for line in ("", " ", "\t \r\n"):
            result = self.tool.execute(mode="lex", command_line=line)
            self.assertEqual(
                result, {"mode": "lex", "expand_vars": False, "argv": [], "argc": 0}
            )

    def test_lex_single_quotes_are_literal(self) -> None:
        line = 'echo \'a  b  $HOME `cmd` "x" \\n\''
        argv = self.tool.execute(mode="lex", command_line=line)["argv"]
        self.assertEqual(
            argv,
            ["echo", "a  b  $HOME `cmd` \"x\" \\n"],
        )

    def test_lex_double_quotes_preserve_spaces(self) -> None:
        argv = self.tool.execute(
            mode="lex", command_line='echo "a  b\tc"'
        )["argv"]
        self.assertEqual(argv, ["echo", "a  b\tc"])

    def test_lex_adjacent_segments_join(self) -> None:
        cases = {
            "'a'b\"c\"": ["abc"],
            "a\"b c\"d": ["ab cd"],
            "'pre'post": ["prepost"],
            "pre\"post\"post": ["prepostpost"],
            "echo 'a'b\"c\"d'e'f": ["echo", "abcdef"],
            "''''": [""],
            "\"\"x''": ["x"],
            "$-'x'\"y\"": ["$-xy"],
        }
        for line, expected in cases.items():
            self.assertEqual(
                self.tool.execute(mode="lex", command_line=line)["argv"],
                expected,
                msg=line,
            )

    def test_lex_empty_quoted_arguments(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="lex", command_line="prog '' arg")["argv"],
            ["prog", "", "arg"],
        )
        self.assertEqual(
            self.tool.execute(mode="lex", command_line='prog "" arg')["argv"],
            ["prog", "", "arg"],
        )

    def test_lex_line_continuation_unquoted(self) -> None:
        argv = self.tool.execute(
            mode="lex", command_line="gcc -o prog \\\n  main.c"
        )["argv"]
        self.assertEqual(argv, ["gcc", "-o", "prog", "main.c"])

    def test_lex_line_continuation_inside_double_quotes(self) -> None:
        argv = self.tool.execute(
            mode="lex", command_line='echo "a\\\nb"'
        )["argv"]
        self.assertEqual(argv, ["echo", "ab"])

    # ------------------------------------------------------------------ #
    # lex mode — escape matrix
    # ------------------------------------------------------------------ #

    def test_lex_unquoted_escape_matrix(self) -> None:
        cases = {
            r"echo a\ b": ["echo", "a b"],
            r"echo it\'s": ["echo", "it's"],
            r'echo say\"hi': ["echo", 'say"hi'],
            r"echo back\\slash": ["echo", "back\\slash"],
            r"echo \t\n": ["echo", "tn"],
            r"echo \\$HOME": ["echo", "\\$HOME"],
            r"echo \*": ["echo", "*"],
        }
        for line, expected in cases.items():
            self.assertEqual(
                self.tool.execute(mode="lex", command_line=line)["argv"],
                expected,
                msg=line,
            )

    def test_lex_double_quote_escape_matrix(self) -> None:
        cases = {
            'echo "a\\\\"': ["echo", "a\\"],
            'echo "a\\"b"': ["echo", 'a"b'],
            'echo "a\\$b"': ["echo", "a$b"],
            'echo "a\\`b"': ["echo", "a`b"],
            'echo "a\\xb"': ["echo", "a\\xb"],
            'echo "a\\tb"': ["echo", "a\\tb"],
        }
        for line, expected in cases.items():
            self.assertEqual(
                self.tool.execute(mode="lex", command_line=line)["argv"],
                expected,
                msg=line,
            )

    def test_lex_glob_and_metacharacters_stay_literal(self) -> None:
        argv = self.tool.execute(
            mode="lex", command_line="echo * ? [a-z] ~ # ; && || | < >"
        )["argv"]
        self.assertEqual(
            argv,
            ["echo", "*", "?", "[a-z]", "~", "#", ";", "&&", "||", "|", "<", ">"],
        )

    # ------------------------------------------------------------------ #
    # lex mode — variable expansion
    # ------------------------------------------------------------------ #

    def test_lex_variables_literal_by_default(self) -> None:
        line = "echo $HOME ${HOME} $5 $? $$ $ `cmd`"
        result = self.tool.execute(mode="lex", command_line=line)
        self.assertEqual(
            result,
            {
                "mode": "lex",
                "expand_vars": False,
                "argv": ["echo", "$HOME", "${HOME}", "$5", "$?", "$$", "$", "`cmd`"],
                "argc": 8,
            },
        )

    def test_lex_expand_vars_on(self) -> None:
        variables = {"HOME": "/root", "NAME": "au"}
        cases = {
            "echo $HOME": ["echo", "/root"],
            "echo ${HOME}": ["echo", "/root"],
            "echo $HOME/bin": ["echo", "/root/bin"],
            "echo ${HOME}s": ["echo", "/roots"],
            "echo $HOMEx": ["echo", ""],
            "echo $NAME-$NAME": ["echo", "au-au"],
            'echo "$HOME/x"': ["echo", "/root/x"],
            'echo "v=$NAME!"': ["echo", "v=au!"],
            "echo ${MISSING}x": ["echo", "x"],
        }
        for line, expected in cases.items():
            self.assertEqual(
                self.tool.execute(
                    mode="lex",
                    command_line=line,
                    expand_vars=True,
                    variables=variables,
                )["argv"],
                expected,
                msg=line,
            )

    def test_lex_expand_vars_single_quotes_and_backslash_suppress(self) -> None:
        variables = {"X": "value"}
        cases = {
            "echo '$X'": ["echo", "$X"],
            "echo '${X}'": ["echo", "${X}"],
            "echo \\$X": ["echo", "$X"],
            'echo "a\\$X"': ["echo", "a$X"],
        }
        for line, expected in cases.items():
            self.assertEqual(
                self.tool.execute(
                    mode="lex",
                    command_line=line,
                    expand_vars=True,
                    variables=variables,
                )["argv"],
                expected,
                msg=line,
            )

    def test_lex_expand_vars_non_name_dollars_stay_literal(self) -> None:
        variables = {"X": "value"}
        argv = self.tool.execute(
            mode="lex",
            command_line="echo $5 $? $$ $ $'x' ",
            expand_vars=True,
            variables=variables,
        )["argv"]
        # $ followed by ' is a literal $; the 'x' that follows is then
        # an ordinary single-quoted segment joined into the same word
        # (ANSI-C $'...' quoting is deliberately NOT supported).
        self.assertEqual(argv, ["echo", "$5", "$?", "$$", "$", "$x"])

    def test_lex_expand_vars_empty_string_value(self) -> None:
        argv = self.tool.execute(
            mode="lex",
            command_line="echo a${E}b",
            expand_vars=True,
            variables={"E": ""},
        )["argv"]
        self.assertEqual(argv, ["echo", "ab"])

    # ------------------------------------------------------------------ #
    # shlex cross-check and documented divergences
    # ------------------------------------------------------------------ #

    def test_lex_matches_shlex_on_safe_corpus(self) -> None:
        for line in SHLEX_SAFE_CORPUS:
            self.assertEqual(
                self.tool.execute(mode="lex", command_line=line)["argv"],
                shlex.split(line),
                msg=line,
            )

    def test_lex_divergence_dollar_escape_in_double_quotes(self) -> None:
        # POSIX collapses \$ inside double quotes to a bare $; shlex
        # keeps both characters. Ours follows POSIX.
        line = 'a "b\\$c" d'
        self.assertEqual(
            self.tool.execute(mode="lex", command_line=line)["argv"],
            ["a", "b$c", "d"],
        )
        self.assertEqual(shlex.split(line), ["a", "b\\$c", "d"])

    def test_lex_divergence_backtick_escape_in_double_quotes(self) -> None:
        line = 'a "b\\`c" d'
        self.assertEqual(
            self.tool.execute(mode="lex", command_line=line)["argv"],
            ["a", "b`c", "d"],
        )
        self.assertEqual(shlex.split(line), ["a", "b\\`c", "d"])

    def test_lex_divergence_backslash_newline(self) -> None:
        # POSIX removes backslash-newline as a line continuation;
        # shlex keeps the newline as a literal character.
        line = "echo a\\\nb"
        self.assertEqual(
            self.tool.execute(mode="lex", command_line=line)["argv"],
            ["echo", "ab"],
        )
        self.assertEqual(shlex.split(line), ["echo", "a\nb"])

    def test_lex_divergence_unterminated_quote(self) -> None:
        line = 'echo "unclosed'
        with self.assertRaises(ValueError):
            shlex.split(line)
        result = self.tool.execute(mode="lex", command_line=line)
        self.assertEqual(result["error"]["type"], "unterminated_quote")

    def test_lex_divergence_dangling_backslash(self) -> None:
        line = "echo a\\"
        with self.assertRaises(ValueError):
            shlex.split(line)
        result = self.tool.execute(mode="lex", command_line=line)
        self.assertEqual(result["error"]["type"], "dangling_backslash")

    # ------------------------------------------------------------------ #
    # lex mode — structured errors with positions
    # ------------------------------------------------------------------ #

    def test_lex_unterminated_quote_positions(self) -> None:
        cases = [
            ('echo "unclosed', 5, '"'),
            ("echo 'unclosed", 5, "'"),
            ('a b "c\'d', 4, '"'),
            ("'start", 0, "'"),
            ('echo "a\\', 5, '"'),  # backslash as last char: quote never closes
            ("pre'mid\"dle", 3, "'"),
        ]
        for line, position, quote in cases:
            result = self.tool.execute(mode="lex", command_line=line)
            self.assertNotIn("argv", result, msg=line)
            error = result["error"]
            self.assertEqual(error["type"], "unterminated_quote", msg=line)
            self.assertEqual(error["position"], position, msg=line)
            self.assertIn(quote, error["message"], msg=line)

    def test_lex_dangling_backslash_position(self) -> None:
        result = self.tool.execute(mode="lex", command_line="echo a\\")
        self.assertEqual(
            result["error"],
            {
                "type": "dangling_backslash",
                "message": (
                    "backslash at position 6 is the last character of "
                    "the command line and escapes nothing"
                ),
                "position": 6,
            },
        )

    def test_lex_variable_errors(self) -> None:
        cases = [
            ("echo ${NAME", "unterminated_variable_brace", 5),
            ("echo ${}", "invalid_variable_name", 5),
            ("echo ${1abc}", "invalid_variable_name", 5),
            ("echo ${a-b}", "invalid_variable_name", 5),
            ("echo x${NAME", "unterminated_variable_brace", 6),
            ('echo "${NAME', "unterminated_variable_brace", 6),
        ]
        for line, error_type, position in cases:
            result = self.tool.execute(
                mode="lex", command_line=line, expand_vars=True, variables={"a": "v"}
            )
            self.assertNotIn("argv", result, msg=line)
            self.assertEqual(result["error"]["type"], error_type, msg=line)
            self.assertEqual(result["error"]["position"], position, msg=line)

    # ------------------------------------------------------------------ #
    # join mode — minimal-quoting ground truths
    # ------------------------------------------------------------------ #

    def test_join_ground_truths(self) -> None:
        cases = [
            (["cp", "file1", "file2"], "cp file1 file2"),
            (["echo", "hello world"], "echo 'hello world'"),
            (["echo", "a\tb"], "echo 'a\tb'"),
            (["echo", "a\nb"], "echo 'a\nb'"),
            (["echo", "a\rb"], "echo 'a\rb'"),
            ([""], "''"),
            ([], ""),
            (["-flag", "--opt=v", "$var", "a#b", "*"], "-flag --opt=v $var a#b *"),
            (['say "hi"'], "'say \"hi\"'"),
            (["back\\slash"], "'back\\slash'"),
            (["it's"], "'it'\"'\"'s'"),
            (["'"], "''\"'\"''"),
            (["a'b'c"], "'a'\"'\"'b'\"'\"'c'"),
            (["", "x", ""], "'' x ''"),
            (["héllo wörld"], "'héllo wörld'"),
            (["a b", "c d", "e"], "'a b' 'c d' e"),
        ]
        for argv, expected in cases:
            self.assertEqual(
                self.tool.execute(mode="join", argv=argv),
                {"mode": "join", "result": expected},
                msg=repr(argv),
            )

    def test_join_quotes_only_when_needed(self) -> None:
        # A word with no whitespace/quote/backslash stays bare even if
        # it contains characters other tools consider special.
        for word in ("plain", "-x", "--long=v", "$HOME", "a#b", "*", "~", "a=b", "héllo"):
            self.assertEqual(
                self.tool.execute(mode="join", argv=[word])["result"], word
            )

    def test_join_then_lex_round_trip_property_200_seeds(self) -> None:
        rng = random.Random(252)
        for _ in range(200):
            argv = [
                "".join(
                    rng.choice(ROUND_TRIP_ALPHABET)
                    for _ in range(rng.randrange(0, 13))
                )
                for _ in range(rng.randrange(0, 9))
            ]
            argv = [word for word in argv if "\x00" not in word]
            line = self.tool.execute(mode="join", argv=argv)["result"]
            self.assertEqual(
                self.tool.execute(mode="lex", command_line=line)["argv"],
                argv,
                msg=repr((argv, line)),
            )

    # ------------------------------------------------------------------ #
    # count mode
    # ------------------------------------------------------------------ #

    def test_count_basic_classification(self) -> None:
        result = self.tool.execute(
            mode="count", command_line="ls -l -t file1 file2"
        )
        self.assertEqual(
            result,
            {
                "mode": "count",
                "count": 5,
                "program": "ls",
                "flag_count": 2,
                "operand_count": 2,
                "flags": [
                    {"raw": "-l", "name": "-l", "has_value": False, "value": None},
                    {"raw": "-t", "name": "-t", "has_value": False, "value": None},
                ],
                "operands": ["file1", "file2"],
                "separator_seen": False,
            },
        )

    def test_count_flag_value_split_on_first_equals(self) -> None:
        result = self.tool.execute(
            mode="count", command_line="grep --color=auto -e=pat --out=a=b f"
        )
        flags = result["flags"]
        self.assertEqual(
            flags,
            [
                {"raw": "--color=auto", "name": "--color", "has_value": True, "value": "auto"},
                {"raw": "-e=pat", "name": "-e", "has_value": True, "value": "pat"},
                {"raw": "--out=a=b", "name": "--out", "has_value": True, "value": "a=b"},
            ],
        )
        self.assertEqual(result["operands"], ["f"])

    def test_count_double_dash_separator(self) -> None:
        result = self.tool.execute(
            mode="count", command_line="mytool -v -- -x --after file"
        )
        self.assertEqual(result["count"], 6)
        self.assertEqual(
            result["flags"],
            [{"raw": "-v", "name": "-v", "has_value": False, "value": None}],
        )
        self.assertEqual(result["operands"], ["-x", "--after", "file"])
        self.assertTrue(result["separator_seen"])
        self.assertEqual(result["flag_count"], 1)
        self.assertEqual(result["operand_count"], 3)

    def test_count_lone_dash_is_operand(self) -> None:
        # | is NOT an operator in this subset — it is an ordinary
        # token, so the pipeline words all belong to the one command.
        result = self.tool.execute(mode="count", command_line="cat - | wc -l")
        self.assertEqual(result["program"], "cat")
        self.assertEqual(result["flags"], [{"raw": "-l", "name": "-l", "has_value": False, "value": None}])
        self.assertEqual(result["operands"], ["-", "|", "wc"])

    def test_count_program_only_and_empty(self) -> None:
        result = self.tool.execute(mode="count", command_line="prog")
        self.assertEqual(
            result,
            {
                "mode": "count",
                "count": 1,
                "program": "prog",
                "flag_count": 0,
                "operand_count": 0,
                "flags": [],
                "operands": [],
                "separator_seen": False,
            },
        )
        empty = self.tool.execute(mode="count", command_line="   ")
        self.assertEqual(empty["count"], 0)
        self.assertIsNone(empty["program"])
        self.assertEqual(empty["flags"], [])
        self.assertEqual(empty["operands"], [])

    def test_count_program_is_argv0_even_when_dashed(self) -> None:
        result = self.tool.execute(mode="count", command_line="-prog -x")
        self.assertEqual(result["program"], "-prog")
        self.assertEqual(result["operands"], [])

    def test_count_separator_equals_edge(self) -> None:
        # --=x is not the bare -- separator; it is a flag whose name
        # splits at the first '='.
        result = self.tool.execute(mode="count", command_line="p --=x")
        self.assertFalse(result["separator_seen"])
        self.assertEqual(
            result["flags"],
            [{"raw": "--=x", "name": "--", "has_value": True, "value": "x"}],
        )

    def test_count_respects_quoting_and_expansion(self) -> None:
        # Classification is textual on the final argv: a quoted "-x"
        # is still the option -x, exactly as getopt sees it.
        result = self.tool.execute(
            mode="count", command_line='run "-x" "$MODE" --flag "a b"'
        )
        self.assertEqual(result["count"], 5)
        self.assertEqual(result["operands"], ["$MODE", "a b"])
        self.assertEqual(
            [flag["name"] for flag in result["flags"]], ["-x", "--flag"]
        )
        expanded = self.tool.execute(
            mode="count",
            command_line='run "-x" "$MODE"',
            expand_vars=True,
            variables={"MODE": "-v"},
        )
        self.assertEqual(expanded["program"], "run")
        self.assertEqual(
            [flag["raw"] for flag in expanded["flags"]], ["-x", "-v"]
        )
        self.assertEqual(expanded["operands"], [])

    def test_count_propagates_lex_errors(self) -> None:
        result = self.tool.execute(mode="count", command_line="echo 'oops")
        self.assertEqual(result["error"]["type"], "unterminated_quote")
        self.assertEqual(result["error"]["position"], 5)

    # ------------------------------------------------------------------ #
    # Input validation — ValueError matrix
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        for mode in (None, "parse", "split", 1, True):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, command_line="ls")

    def test_invalid_command_line(self) -> None:
        for command_line in (None, 123, True, ["ls"], b"ls"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="lex", command_line=command_line)

    def test_command_line_with_nul(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lex", command_line="ls \x00")

    def test_command_line_over_limit(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lex", command_line="a" * 100_001)

    def test_invalid_argv(self) -> None:
        for argv in (None, "echo hi", 42, True, [1], ["a", None], ["a", True]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="join", argv=argv)

    def test_argv_with_nul(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="join", argv=["a\x00b"])

    def test_argv_over_item_limit(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="join", argv=["x"] * 10_001)

    def test_argv_over_total_char_limit(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="join", argv=["x" * 50_001, "y" * 50_001])

    def test_invalid_expand_vars(self) -> None:
        for value in ("yes", 1, "true"):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="lex", command_line="ls", expand_vars=value
                )

    def test_variables_require_expand_vars_flag(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lex", command_line="ls", variables={"A": "b"}
            )

    def test_expand_vars_requires_variables(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lex", command_line="ls", expand_vars=True)

    def test_invalid_variables(self) -> None:
        bad_dicts = [
            None,
            "dict",
            ["A"],
            {1: "x"},
            {"1abc": "x"},
            {"a-b": "x"},
            {"a b": "x"},
            {"": "x"},
            {"A": 1},
            {"A": None},
            {"A": True},
            {"A": "b\x00c"},
        ]
        for variables in bad_dicts:
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="lex",
                    command_line="ls",
                    expand_vars=True,
                    variables=variables,
                )

    def test_variables_over_limit(self) -> None:
        variables = {f"V{i}": "x" for i in range(201)}
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lex", command_line="ls", expand_vars=True, variables=variables
            )

    def test_empty_variables_dict_is_valid(self) -> None:
        result = self.tool.execute(
            mode="lex",
            command_line="echo $A${B}",
            expand_vars=True,
            variables={},
        )
        self.assertEqual(result["argv"], ["echo", ""])


if __name__ == "__main__":
    unittest.main()

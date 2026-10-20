#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: command_arg_lexer_tool.py

"""POSIX-shell-style argv tokenization tool — lexing only, never execution.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency command-line lexer
agents can call when they must understand a user-supplied command
without running it: splitting it into ``argv`` words the way a shell
would, quoting an ``argv`` list back into one safe line, or classifying
flags versus operands.

The tool complements ``ContextEscapeTool``: that tool *quotes* text for
safe embedding into a shell (among other contexts), while this tool
*parses* a command line that a shell would split. Together they cover
both directions of the boundary between "one command-line string" and
"a list of argument words".

Three modes, all built purely on the standard library:

* ``lex`` — command line (string) → ``argv`` (list of strings),
  implementing a deliberate POSIX-shell-style subset of tokenization:

  - Word splitting on runs of the separator whitespace characters
    space, tab, CR and LF (the same set Python's ``shlex`` uses; VT,
    FF and Unicode whitespace such as U+00A0 are *not* separators —
    they stay inside the token, matching byte-oriented shells).
  - Single quotes: fully literal content, no escapes, cannot contain a
    single quote.
  - Double quotes: ``\\`` → ``\``, ``\"`` → ``"``, ``\$`` → ``$`` and
    ``\\` `` → ``\\` `` collapse per POSIX; backslash-newline is a line
    continuation (removed); a backslash before any other character
    keeps both characters; a lone ``$`` is handled by the variable
    rules below.
  - Backslash outside quotes: escapes the next character
    (``\\x`` → ``x`` for any ``x``); backslash-newline is a line
    continuation (removed, and not a token boundary).
  - Adjacent segments join into one word: ``'a'b"c"`` → ``abc``.
  - An unterminated quote or a trailing backslash is a structured
    error carrying the 0-based position of the offending opening
    quote / backslash.
  - Variable expansion is OFF by default: ``$VAR``, ``${VAR}``, ``$5``,
    ``$?`` and friends are kept literally, which is what an agent
    usually wants when inspecting a command someone else wrote. The
    opt-in ``expand_vars`` flag substitutes ``$NAME`` and ``${NAME}``
    forms (name = ``[A-Za-z_][A-Za-z0-9_]*``) from a caller-supplied
    ``variables`` dict — never from the environment — in unquoted and
    double-quoted text, never inside single quotes, with ``\$``
    suppressing expansion exactly as in a shell. An undefined name
    substitutes the empty string (POSIX behaviour); ``$`` followed by
    anything that is not a name (``$5``, ``$?``, ``$$``, ``$ ``) stays
    literal; an unterminated ``${`` or a ``${...}`` whose content is
    not a valid name is a structured error with a position. Expanded
    text is inserted verbatim — it is never re-split or re-parsed for
    quotes (a deliberate simplification of full POSIX field
    splitting).

* ``join`` — ``argv`` (list of strings) → a single safely-quoted line
  using the minimal quoting needed: a word with no separator
  whitespace, quote or backslash character is emitted verbatim;
  anything else is wrapped in single quotes with each embedded single
  quote spelled as the standard ``'"'"'`` idiom; the empty string
  becomes ``''``. The transform is exactly invertible under ``lex``:
  ``lex(join(argv)) == argv`` (with the default ``expand_vars=False``;
  a word containing ``$`` is emitted bare because ``$`` is literal by
  default).

* ``count`` — command line → ``argv`` count plus flags-versus-operands
  classification: ``argv[0]`` is reported as the program, leading-dash
  words (length > 1) before the ``--`` separator are flags with an
  optional ``flag=value`` split on the first ``=``, everything else —
  including a lone ``-`` (the conventional stdin marker) and every
  word after ``--`` — is an operand.

Deliberately NOT part of the subset (all of these would require
execution or are shell-specific syntax): glob expansion (``*``,
``?``, ``[...]``), command substitution ``$(...)`` / ``...``,
process substitution, tilde expansion, redirection operators as
syntax, here-documents, assignment-word detection, ANSI-C quoting
``$'...'``, locale-specific ``$`` forms (``$1``, ``$?``, ``$$``,
``$@``), alias/history expansion and semicolon/``&&``/``||`` command
separators. Those characters are ordinary token characters; an agent
that needs them interpreted must hand the line to a real shell
consciously, not accidentally.

Divergences from Python's ``shlex.split`` (all deliberate): ``\$`` and
``\\` `` inside double quotes collapse to the bare character here but
are kept as two characters by ``shlex`` (POSIX collapses them);
backslash-newline is a removed line continuation here but a literal
newline inside the word for ``shlex``; unterminated quotes and a
trailing backslash return a structured error with a position here but
raise ``ValueError`` in ``shlex``. On every command line that avoids
those three constructs the two tokenizers agree exactly.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, ``argv`` given as a bare string,
non-string ``argv`` items, NUL characters anywhere — a POSIX shell
cannot represent them —, unknown mode, ``expand_vars`` that is not a
boolean, ``variables`` supplied without ``expand_vars`` or missing
with it, variable names outside ``[A-Za-z_][A-Za-z0-9_]*``,
non-string variable values, inputs over the size caps) raise a
``ValueError``, mirroring the other common tools. Errors that depend
on the *content being processed* — unterminated quote, trailing
backslash, unterminated ``${``, invalid ``${...}`` name — are
returned as a structured ``error`` payload (``{"type": ...,
"message": ..., "position": ...}``) so an agent can react without
catching exceptions.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Separator whitespace: the same four characters Python's shlex treats
# as whitespace. VT/FF and Unicode whitespace deliberately do NOT
# separate words (they stay inside the token).
_WHITESPACE = " \t\r\n"
# Characters that force single-quote wrapping in join mode: any
# separator whitespace, either quote character, or a backslash.
_NEEDS_QUOTING = re.compile(r"[ \t\r\n'\"\\]")
# Valid variable name for $NAME / ${NAME}.
_VAR_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Inside double quotes a backslash only collapses before these chars
# (POSIX); before any other character both characters are kept.
_DQ_ESCAPE_CHARS = "$`\"\\"
# Input size caps (referenced by classmethods, which cannot read the
# pydantic instance fields through the class).
_MAX_COMMAND_LINE_CHARS = 100_000
_MAX_ARGV_ITEMS = 10_000
_MAX_ARGV_TOTAL_CHARS = 100_000
_MAX_VARIABLES = 200


class CommandArgLexerTool(Tool):
    """POSIX-shell-style argv lexer / joiner / classifier (no execution).

    Attributes:
        max_command_line_chars (int): Upper bound on the ``command_line``
            input length for the ``lex`` and ``count`` modes.
        max_argv_items (int): Upper bound on the number of ``argv``
            items for the ``join`` mode.
        max_argv_total_chars (int): Upper bound on the total number of
            characters across all ``argv`` items for the ``join`` mode.
        max_variables (int): Upper bound on the number of ``variables``
            entries.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "command_arg_lexer_tool"
    description: str = (
        "Command argument lexer tool — POSIX-shell-style argv "
        "tokenization WITHOUT execution, pure Python stdlib, no "
        "network. mode='lex' splits a command line into an argv list "
        "(whitespace splitting, single/double quotes, backslash "
        "escapes, adjacent-segment joining, optional dict-based "
        "$VAR/${VAR} expansion via expand_vars; variable text is "
        "literal by default), mode='join' quotes an argv list back "
        "into one safe line with minimal quoting "
        "(lex(join(argv)) == argv round-trip), and mode='count' "
        "classifies argv into program, flags (leading dash, with "
        "flag=value split, -- separator respected) and operands. No "
        "globs, no command substitution, no execution."
    )

    MODES: ClassVar[tuple] = ("lex", "join", "count")

    max_command_line_chars: int = _MAX_COMMAND_LINE_CHARS
    max_argv_items: int = _MAX_ARGV_ITEMS
    max_argv_total_chars: int = _MAX_ARGV_TOTAL_CHARS
    max_variables: int = _MAX_VARIABLES

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        command_line: Any = None,
        argv: Any = None,
        expand_vars: Any = None,
        variables: Any = None,
    ) -> Dict[str, Any]:
        """Run one lexer operation.

        Args:
            mode (str): One of ``lex`` / ``join`` / ``count``.
            command_line (str): The command line to tokenize; required
                for the ``lex`` and ``count`` modes (may be empty or
                all-whitespace, which lexes to an empty argv).
            argv (List[str]): The argument words to quote; required for
                the ``join`` mode (may be an empty list, which joins
                to the empty string).
            expand_vars (bool): ``lex``/``count`` only — opt-in
                ``$NAME`` / ``${NAME}`` substitution from ``variables``.
                Defaults to ``False`` (all ``$`` text stays literal).
            variables (Dict[str, str]): ``lex``/``count`` only — the
                substitution table for ``expand_vars=True`` (required
                when the flag is set, forbidden without it). Keys must
                be valid names, values plain strings; the process
                environment is never consulted.

        Returns:
            Dict[str, Any]: The operation result — ``argv``/``argc``
                for ``lex``, the quoted line under ``result`` for
                ``join``, and the flag/operand classification for
                ``count`` — or a structured ``error`` payload for
                content-level failures (unterminated quote, trailing
                backslash, malformed ``${...}``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "join":
            clean_argv = self._validate_argv(argv)
            return {"mode": "join", "result": self._join_argv(clean_argv)}

        clean_line = self._validate_command_line(command_line)
        clean_expand, clean_variables = self._validate_expansion(
            mode, expand_vars, variables
        )
        tokenized, error = self._tokenize(clean_line, clean_expand, clean_variables)
        if mode == "lex":
            context = {"mode": "lex", "expand_vars": clean_expand}
            if error is not None:
                return {**context, "error": error}
            return {**context, "argv": tokenized, "argc": len(tokenized)}
        return self._run_count(clean_line, clean_expand, clean_variables, tokenized, error)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"command_arg_lexer_tool: {message}")

    @classmethod
    def _reject_nul(cls, where: str, text: str) -> None:
        """Reject NUL characters, which a POSIX shell cannot represent."""
        index = text.find("\x00")
        if index != -1:
            cls._invalid(
                f"{where} must not contain NUL characters "
                f"(found one at position {index}; a POSIX shell cannot "
                "represent it in an argument)"
            )

    @classmethod
    def _validate_command_line(cls, command_line: Any) -> str:
        """Validate the ``command_line`` input (lex and count modes)."""
        if command_line is None or isinstance(command_line, bool) or not isinstance(command_line, str):
            cls._invalid(
                f"command_line must be a string (got {command_line!r})"
            )
        cls._reject_nul("command_line", command_line)
        limit = _MAX_COMMAND_LINE_CHARS
        if len(command_line) > limit:
            cls._invalid(
                f"command_line exceeds the {limit:,}-character limit "
                f"(got {len(command_line):,} characters)"
            )
        return command_line

    @classmethod
    def _validate_argv(cls, argv: Any) -> List[str]:
        """Validate the ``argv`` input (join mode)."""
        if argv is None or isinstance(argv, (str, bool)) or not isinstance(argv, (list, tuple)):
            cls._invalid(
                f"argv must be a list of strings (got {argv!r})"
            )
        if len(argv) > _MAX_ARGV_ITEMS:
            cls._invalid(
                f"argv exceeds the {_MAX_ARGV_ITEMS:,}-item limit "
                f"(got {len(argv):,} items)"
            )
        total = 0
        for item in argv:
            if isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(f"every argv item must be a string (got {item!r})")
            cls._reject_nul("argv items", item)
            total += len(item)
        if total > _MAX_ARGV_TOTAL_CHARS:
            cls._invalid(
                f"argv items total more than {_MAX_ARGV_TOTAL_CHARS:,} "
                f"characters (got {total:,})"
            )
        return list(argv)

    @classmethod
    def _validate_expansion(
        cls, mode: str, expand_vars: Any, variables: Any
    ) -> Tuple[bool, Dict[str, str]]:
        """Validate the ``expand_vars`` / ``variables`` pair (lex/count)."""
        if expand_vars is None:
            clean_expand = False
        elif isinstance(expand_vars, bool):
            clean_expand = expand_vars
        else:
            cls._invalid(f"expand_vars must be a boolean (got {expand_vars!r})")

        if not clean_expand:
            if variables is not None:
                cls._invalid(
                    "variables is only accepted together with "
                    "expand_vars=True (got variables without the flag)"
                )
            return False, {}
        if variables is None:
            cls._invalid(
                "expand_vars=True requires a variables dict to "
                "substitute from (got None; pass {} explicitly to "
                "expand every name to the empty string)"
            )
        if isinstance(variables, bool) or not isinstance(variables, dict):
            cls._invalid(f"variables must be a dict of name -> string (got {variables!r})")
        if len(variables) > _MAX_VARIABLES:
            cls._invalid(
                f"variables exceeds the {_MAX_VARIABLES:,}-entry limit "
                f"(got {len(variables):,} entries)"
            )
        for key, value in variables.items():
            if isinstance(key, bool) or not isinstance(key, str) or not _VAR_NAME.fullmatch(key):
                cls._invalid(
                    "every variables key must be a valid variable name "
                    f"[A-Za-z_][A-Za-z0-9_]* (got {key!r})"
                )
            if isinstance(value, bool) or not isinstance(value, str):
                cls._invalid(
                    f"every variables value must be a string (got {value!r} for {key!r})"
                )
            cls._reject_nul("variables values", value)
        return True, dict(variables)

    # ------------------------------------------------------------------ #
    # Core lexer (lex and count modes)
    # ------------------------------------------------------------------ #

    @classmethod
    def _tokenize(
        cls, line: str, expand_vars: bool, variables: Dict[str, str]
    ) -> Tuple[Optional[List[str]], Optional[Dict[str, Any]]]:
        """Split ``line`` into argv words, or return a structured error.

        Returns ``(argv, None)`` on success and ``(None, error)`` on a
        content-level failure (never raises for content problems).
        """
        argv: List[str] = []
        current: List[str] = []
        have_word = False
        i = 0
        n = len(line)
        while i < n:
            ch = line[i]
            if ch in _WHITESPACE:
                if have_word:
                    argv.append("".join(current))
                    current = []
                    have_word = False
                i += 1
                continue
            if ch == "'":
                end = line.find("'", i + 1)
                if end == -1:
                    return None, cls._content_error(
                        "unterminated_quote", i, quote="'"
                    )
                current.append(line[i + 1 : end])
                have_word = True
                i = end + 1
                continue
            if ch == '"':
                opening = i
                i += 1
                have_word = True
                closed = False
                while i < n:
                    inner = line[i]
                    if inner == '"':
                        i += 1
                        closed = True
                        break
                    if inner == "\\" and i + 1 < n:
                        nxt = line[i + 1]
                        if nxt in _DQ_ESCAPE_CHARS:
                            current.append(nxt)
                            i += 2
                        elif nxt == "\n":
                            # Line continuation inside double quotes.
                            i += 2
                        else:
                            # POSIX: backslash before any other char
                            # inside double quotes keeps both chars.
                            current.append("\\")
                            current.append(nxt)
                            i += 2
                        continue
                    if inner == "$" and expand_vars:
                        text, new_i, error = cls._expand_variable(line, i, variables)
                        if error is not None:
                            return None, error
                        current.append(text)
                        i = new_i
                        continue
                    current.append(inner)
                    i += 1
                if not closed:
                    return None, cls._content_error(
                        "unterminated_quote", opening, quote='"'
                    )
                continue
            if ch == "\\":
                if i + 1 >= n:
                    return None, cls._content_error("dangling_backslash", i)
                nxt = line[i + 1]
                if nxt == "\n":
                    # Line continuation: removed, not a word boundary.
                    i += 2
                    continue
                current.append(nxt)
                have_word = True
                i += 2
                continue
            if ch == "$" and expand_vars:
                text, new_i, error = cls._expand_variable(line, i, variables)
                if error is not None:
                    return None, error
                current.append(text)
                have_word = True
                i = new_i
                continue
            current.append(ch)
            have_word = True
            i += 1
        if have_word:
            argv.append("".join(current))
        return argv, None

    @classmethod
    def _expand_variable(
        cls, line: str, i: int, variables: Dict[str, str]
    ) -> Tuple[str, int, Optional[Dict[str, Any]]]:
        """Expand ``$NAME`` / ``${NAME}`` at ``line[i] == '$'``.

        An undefined name substitutes the empty string (POSIX
        behaviour); ``$`` followed by anything that is not a name
        stays literal; the caller never consults the environment.
        """
        n = len(line)
        if i + 1 < n and line[i + 1] == "{":
            end = line.find("}", i + 2)
            if end == -1:
                return "", i, cls._content_error(
                    "unterminated_variable_brace", i
                )
            name = line[i + 2 : end]
            if not _VAR_NAME.fullmatch(name):
                return "", i, cls._content_error(
                    "invalid_variable_name", i, name=name
                )
            return variables.get(name, ""), end + 1, None
        match = _VAR_NAME.match(line, i + 1)
        if match is not None:
            name = match.group()
            return variables.get(name, ""), match.end(), None
        # $5, $?, $$, "$ ", '$''' … — no name follows, keep literal.
        return "$", i + 1, None

    # ------------------------------------------------------------------ #
    # join mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _quote_word(word: str) -> str:
        """Quote one argv word with the minimal quoting ``lex`` undoes.

        Bare when the word contains no separator whitespace, quote or
        backslash; otherwise single-quoted with every embedded single
        quote spelled as the standard ``'"'"'`` idiom; the empty word
        becomes ``''``.
        """
        if not word:
            return "''"
        if _NEEDS_QUOTING.search(word) is None:
            return word
        return "'" + word.replace("'", "'\"'\"'") + "'"

    @classmethod
    def _join_argv(cls, argv: List[str]) -> str:
        """Join argv words into one safely-quoted line."""
        return " ".join(cls._quote_word(word) for word in argv)

    # ------------------------------------------------------------------ #
    # count mode
    # ------------------------------------------------------------------ #

    def _run_count(
        self,
        command_line: str,
        expand_vars: bool,
        variables: Dict[str, str],
        tokenized: Optional[List[str]],
        error: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Classify argv into program / flags / operands."""
        if error is not None:
            return {"mode": "count", "error": error}
        flags: List[Dict[str, Any]] = []
        operands: List[str] = []
        separator_seen = False
        for word in tokenized[1:]:
            if separator_seen:
                operands.append(word)
            elif word == "--":
                separator_seen = True
            elif word.startswith("-") and len(word) > 1:
                name, eq, value = word.partition("=")
                flags.append(
                    {
                        "raw": word,
                        "name": name,
                        "has_value": bool(eq),
                        "value": value if eq else None,
                    }
                )
            else:
                # Operands include the lone "-" (stdin marker) and
                # every dashed word after the -- separator.
                operands.append(word)
        return {
            "mode": "count",
            "count": len(tokenized),
            "program": tokenized[0] if tokenized else None,
            "flag_count": len(flags),
            "operand_count": len(operands),
            "flags": flags,
            "operands": operands,
            "separator_seen": separator_seen,
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _content_error(
        error_type: str, position: int, quote: Optional[str] = None, name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a structured content-level error with a position."""
        if error_type == "unterminated_quote":
            message = (
                f"unterminated {quote} quote: the quote opening at "
                f"position {position} is never closed before the end "
                "of the command line"
            )
        elif error_type == "dangling_backslash":
            message = (
                f"backslash at position {position} is the last "
                "character of the command line and escapes nothing"
            )
        elif error_type == "unterminated_variable_brace":
            message = (
                f"${{ opened at position {position} is never closed "
                "with '}'"
            )
        elif error_type == "invalid_variable_name":
            message = (
                f"${{...}} at position {position} does not contain a "
                f"valid variable name [A-Za-z_][A-Za-z0-9_]* (got {name!r})"
            )
        else:  # pragma: no cover - defensive
            message = f"lexing failed at position {position}"
        return {
            "type": error_type,
            "message": message[:500],
            "position": position,
        }

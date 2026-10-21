#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: docstring_coverage_tool.py

"""Python module docstring / API-coverage auditing tool, pure stdlib ``ast``.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency documentation
**measurement** utility. Upstream's docstring-batch PRs *add*
docstrings one module at a time; this tool is the audit layer that
tells an agent **where the gaps still are**: which modules, public
functions, classes and methods lack docstrings, what the coverage
percentage is, and whether it clears a gate. It reads source text,
never executes it, and returns structured numbers — it does not
write or lint prose (unlike the family's prompt-lint / PR-quality
tools, it audits Python source, not natural-language artifacts).

Single-text contract (same as the rest of the family): ``text`` is
the full source of **one** Python module per call — callers batch
one call per file; directories / file lists are not accepted. The
text is parsed once with ``ast.parse`` (a single leading UTF-8 BOM
is stripped first, mirroring how CPython's importer loads
BOM-prefixed files); a syntax error is a content-level failure and
returns a structured ``error`` payload (never an exception),
carrying the parser's line / offset and a 60-character preview of
the offending line.

The tool supports three modes (all walk the same AST inventory):

* ``scan`` — the full inventory: ``module_docstring`` (bool) plus
  ``items``, one row per ``def`` / ``async def`` / ``class``
  statement, each ``{kind: function|class|method, qualname, line,
  has_docstring, is_public, is_nested, is_dunder, is_override,
  is_abstractmethod, is_wraps, exempt}``, sorted by line. ``line``
  is the ``def`` / ``class`` statement line (decorators excluded).
  Qualnames mirror Python's own ``__qualname__`` convention:
  ``C.m`` for methods and nested classes, ``outer.<locals>.inner``
  for functions defined inside functions.
* ``summary`` — the CI-gate numbers over the audit surface (public
  items only, see below): ``total_public``, ``documented_public``,
  ``exempt_public``, ``coverage_pct`` (1 decimal place; 100.0 when
  nothing requires a docstring), ``by_kind`` total/documented
  counts, and ``undocumented`` — the offending rows
  ``{qualname, line, kind}`` sorted by line, capped at 50 with
  ``undocumented_total`` + ``truncated`` flags.
* ``check`` — the lint mode: thresholds ``min_module`` (0/1 — the
  module docstring gate), ``min_public`` and ``min_class`` (0-100 —
  coverage percentage gates; defaults 0, i.e. off) produce one
  pass/fail row per threshold with the offending names (listed
  only for a failing gate, capped at 50). ``passed`` is the AND of
  the three. Gates compare the **reported** 1-decimal coverage
  number, so what you see is what gates.

Audit surface semantics (the numbers ``summary`` / ``check``
report):

* ``is_public`` is the mechanical name rule — not ``_``-prefixed.
  Dunder names therefore fail the rule and are excluded from the
  requirement (they are conventionally undocumented); they still
  appear in ``scan`` rows with ``is_dunder`` set.
* Nested definitions (any function or class lexically inside a
  function — ``<locals>.`` in the qualname) are **not importable
  API**; they are reported by ``scan`` with ``is_nested`` set but
  excluded from the coverage requirement.
* Exemptions for "documented elsewhere" decorators:
  ``@override`` (PEP 698 — the parent's docstring applies),
  ``@abstractmethod`` (the abstract declaration; implementations
  carry the docs) and ``@functools.wraps`` (copies the wrapped
  function's ``__doc__`` at runtime). Exempt items keep their
  ``scan`` row and flags and drop out of the requirement counts
  (reported via ``exempt_public``).
* Property protocol pairs are counted once: a ``@property`` /
  ``@cached_property`` getter emits the row and its same-named
  ``@x.setter`` / ``@x.deleter`` accessors in the same class body
  emit none (the property docstring is the getter's). A setter
  without a visible same-named getter falls back to a normal
  method row (the AST alone cannot see inherited properties).
* ``async def`` counts like ``def``; lambdas are skipped entirely;
  definitions inside module- or class-level ``if`` / ``try`` /
  ``for`` / ``with`` blocks belong to that scope like their
  siblings (``if TYPE_CHECKING:`` blocks included).

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty or whitespace-only text,
unknown mode, out-of-place or out-of-range thresholds, text over
10,000,000 characters) raise a ``ValueError``, mirroring the other
common tools. The one content-level failure — a syntax error —
returns a structured ``error`` payload so an agent can react
without catching exceptions.
"""

import ast
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Definition statements the walk emits one row per.
_DEFINITION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
# Statements whose suites belong to the enclosing module / class
# scope (e.g. ``if TYPE_CHECKING:`` definitions).
_BRANCH_NODES = (
    ast.If,
    ast.Try,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.With,
    ast.AsyncWith,
)


def _is_dunder(name: str) -> bool:
    """True for ``__double_leading_and_trailing__`` names."""
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def _has_docstring(node: ast.AST) -> bool:
    """True when the node carries a literal docstring.

    Mirrors ``ast.get_docstring`` presence semantics: the first
    statement of the body is a string-literal expression. F-string
    "docstrings" do not count (Python itself ignores them).
    """
    if not isinstance(node, (ast.Module, *_DEFINITION_NODES)):
        return False
    if not node.body:
        return False
    first = node.body[0]
    return isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str)


def _decorator_tags(decorators: list[ast.expr]) -> dict[str, Any]:
    """Classify a definition's decorator list.

    Returns flag fields plus the property-protocol role.
    Recognition is by the decorator's last name segment
    (``@override``, ``@typing.override``, ``@abc.abstractmethod``
    and decorator factories like ``@functools.wraps(f)`` /
    ``@x.setter`` all reduce to that segment).
    """
    tags = {
        "is_override": False,
        "is_abstractmethod": False,
        "is_wraps": False,
        "property_role": None,  # None | "getter" | "accessor"
    }
    for decorator in decorators:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Name):
            segment = target.id
        elif isinstance(target, ast.Attribute):
            segment = target.attr
        else:
            continue
        if segment == "override":
            tags["is_override"] = True
        elif segment == "abstractmethod":
            tags["is_abstractmethod"] = True
        elif segment == "wraps" and isinstance(decorator, ast.Call):
            tags["is_wraps"] = True
        elif segment in ("property", "cached_property"):
            tags["property_role"] = "getter"
        elif segment in ("setter", "deleter") and isinstance(target, ast.Attribute):
            # ``@speed.setter`` is a bare attribute reference — the
            # decorator protocol itself supplies the call.
            tags["property_role"] = "accessor"
    return tags


def _definitions_in(body: list[ast.stmt]) -> list[ast.AST]:
    """Definitions introduced by one scope's statement list.

    Flattens control-flow suites (``if`` / ``try`` / ``for`` /
    ``while`` / ``with`` / ``match``) so that e.g. a ``def`` inside
    ``if TYPE_CHECKING:`` belongs to the module scope. Definitions
    inside functions / classes are NOT descended into here — the
    caller recurses into scopes itself with the right qualname.
    """
    found: list[ast.AST] = []
    for statement in body:
        if isinstance(statement, _DEFINITION_NODES):
            found.append(statement)
        elif isinstance(statement, ast.If):
            found.extend(_definitions_in(statement.body))
            found.extend(_definitions_in(statement.orelse))
        elif isinstance(statement, ast.Try):
            found.extend(_definitions_in(statement.body))
            for handler in statement.handlers:
                found.extend(_definitions_in(handler.body))
            found.extend(_definitions_in(statement.orelse))
            found.extend(_definitions_in(statement.finalbody))
        elif isinstance(statement, ast.Match):
            for case in statement.cases:
                found.extend(_definitions_in(case.body))
        elif isinstance(statement, _BRANCH_NODES):
            found.extend(_definitions_in(statement.body))
            found.extend(_definitions_in(getattr(statement, "orelse", None) or []))
    return found


class DocstringCoverageTool(Tool):
    """Docstring / API-coverage auditor built purely on the stdlib ``ast``.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length.
        max_items (int): Upper bound on ``scan`` rows (with an
            ``items_truncated`` flag) so a pathological module cannot
            produce an unbounded response.
        max_undocumented (int): Cap on the ``undocumented`` /
            offending-name lists in ``summary`` and ``check``.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "docstring_coverage_tool"
    description: str = (
        "Docstring coverage tool — Python module docstring / API-coverage "
        "auditing with pure stdlib ast, no network required, source is "
        "parsed never executed. Measures where documentation gaps are: "
        "mode='scan' returns the full inventory (module_docstring plus one "
        "row per def/async def/class: kind, __qualname__-style qualname, "
        "line, has_docstring, is_public/_nested/_dunder, @override / "
        "@abstractmethod / functools.wraps exemptions, property+setter "
        "pairs counted once, lambdas skipped, async counted, nested defs "
        "with <locals>. qualnames); mode='summary' returns the CI-gate "
        "numbers (total/documented/exempt public items, coverage_pct at 1 "
        "decimal, by_kind counts, undocumented offenders capped at 50); "
        "mode='check' applies min_module (0/1), min_public and min_class "
        "(0-100 percentage gates, default 0) with pass/fail per threshold "
        "and the offending names. Public = not _-prefixed; dunders and "
        "non-importable nested defs are excluded from the requirement; a "
        "syntax error returns a structured error payload, never an "
        "exception. One module's source text per call."
    )

    MODES: ClassVar[tuple] = ("scan", "summary", "check")
    KINDS: ClassVar[tuple] = ("function", "class", "method")

    # Size caps are class constants so validating classmethods can read
    # them off ``cls``.
    max_text_chars: ClassVar[int] = 10_000_000
    max_items: ClassVar[int] = 10_000
    max_undocumented: ClassVar[int] = 50
    error_preview_chars: ClassVar[int] = 60

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        text: Any = None,
        min_module: Any = None,
        min_public: Any = None,
        min_class: Any = None,
    ) -> dict[str, Any]:
        """Run one docstring-coverage operation.

        Args:
            mode (str): One of ``scan`` / ``summary`` / ``check``.
            text (str): The full source text of one Python module
                (single-text contract — batch one call per file).
            min_module (int): Check mode only — 0 or 1; when 1 the
                module docstring is required. Default 0. Rejected in
                the other modes.
            min_public (float): Check mode only — minimum overall
                public coverage percentage, 0-100, default 0. The
                gate compares the reported 1-decimal number.
            min_class (float): Check mode only — minimum coverage
                percentage over the class API surface (public classes
                plus their public methods), 0-100, default 0; 100.0
                when the module declares no public class API.

        Returns:
            Dict[str, Any]: The inventory for ``scan``, the coverage
            numbers for ``summary``, the threshold results for
            ``check`` — or a structured ``error`` payload when the
            text is not valid Python.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        clean_text = self._validate_text(text)
        if clean_text.startswith("\ufeff"):
            # A UTF-8 BOM survives utf-8 decoding as U+FEFF and
            # CPython's own importer strips it — mirror that so a
            # BOM-prefixed file audits like Python loads it.
            clean_text = clean_text[1:]
        if mode == "check":
            clean_thresholds = (
                self._validate_min_module(min_module),
                self._validate_min_percent("min_public", min_public),
                self._validate_min_percent("min_class", min_class),
            )
        else:
            for name, value in (
                ("min_module", min_module),
                ("min_public", min_public),
                ("min_class", min_class),
            ):
                self._reject_option(name, value, allowed_modes=("check",))
            clean_thresholds = None
        try:
            tree = ast.parse(clean_text)
        except (SyntaxError, ValueError) as exc:
            return {"mode": mode, **self._syntax_error(exc)}
        module_docstring, items = self._scan(tree)
        if mode == "scan":
            return self._run_scan(module_docstring, items)
        summary = self._summarize(module_docstring, items)
        if mode == "summary":
            return summary
        return self._run_check(summary, items, clean_thresholds)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"docstring_coverage_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the module source text (single-text contract)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text.strip():
            preview = text if len(text) <= 20 else text[:20] + "..."
            cls._invalid(f"text must be a non-empty string (got {preview!r})")
        if len(text) > cls.max_text_chars:
            cls._invalid(f"text exceeds the {cls.max_text_chars:,}-character limit " f"(got {len(text):,} characters)")
        return text

    @classmethod
    def _validate_min_module(cls, min_module: Any) -> int:
        """Validate the module-docstring gate (check mode)."""
        if min_module is None:
            return 0
        if isinstance(min_module, bool):
            return int(min_module)
        if isinstance(min_module, int) and min_module in (0, 1):
            return min_module
        cls._invalid(f"min_module must be 0 or 1 (got {min_module!r})")

    @classmethod
    def _validate_min_percent(cls, name: str, value: Any) -> float:
        """Validate a percentage gate (check mode)."""
        if value is None:
            return 0.0
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or value > 100:
            cls._invalid(f"{name} must be a number from 0 to 100 (got {value!r})")
        return float(value)

    @classmethod
    def _reject_option(cls, name: str, value: Any, allowed_modes: tuple[str, ...]) -> None:
        """Reject an option passed outside its allowed modes."""
        if value is not None:
            cls._invalid(f"{name} is only accepted in " f"{', '.join(allowed_modes)} mode")

    # ------------------------------------------------------------------ #
    # The shared AST walk
    # ------------------------------------------------------------------ #

    @classmethod
    def _syntax_error(cls, exc: Exception) -> dict[str, Any]:
        """Build the structured payload for unparsable source text."""
        preview = getattr(exc, "text", None)
        if isinstance(preview, str):
            preview = preview.strip()
            if len(preview) > cls.error_preview_chars:
                preview = preview[: cls.error_preview_chars] + "..."
        else:
            preview = ""
        return {
            "error": {
                "type": "syntax_error",
                "message": str(getattr(exc, "msg", None) or exc),
                "line": getattr(exc, "lineno", None),
                "offset": getattr(exc, "offset", None),
                "text": preview,
            }
        }

    @classmethod
    def _scan(cls, tree: ast.Module) -> tuple[bool, list[dict[str, Any]]]:
        """Walk the AST; return (module_docstring, line-sorted rows)."""
        items: list[dict[str, Any]] = []

        def walk_scope(body: list[ast.stmt], prefix: str, in_class: bool, in_function: bool) -> None:
            """Emit rows for one lexical scope, recursing into defs.

            ``prefix`` follows the ``__qualname__`` convention; defs
            met inside control-flow statements belong to this scope;
            anything under a function body is flagged ``is_nested``.
            """
            definitions = _definitions_in(body)
            property_names = {
                node.name
                for node in definitions
                if in_class
                and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and _decorator_tags(list(node.decorator_list))["property_role"] == "getter"
            }
            for node in definitions:
                is_def = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                kind = (
                    "method" if (is_def and in_class) else ("class" if isinstance(node, ast.ClassDef) else "function")
                )
                tags = _decorator_tags(list(node.decorator_list))
                if tags["property_role"] == "accessor" and node.name in property_names:
                    # Property protocol pair: the getter's row is the
                    # single row for the whole property.
                    continue
                items.append(
                    {
                        "kind": kind,
                        "qualname": prefix + node.name,
                        "line": node.lineno,
                        "has_docstring": _has_docstring(node),
                        "is_public": not node.name.startswith("_"),
                        "is_nested": in_function,
                        "is_dunder": _is_dunder(node.name),
                        "is_override": tags["is_override"],
                        "is_abstractmethod": tags["is_abstractmethod"],
                        "is_wraps": tags["is_wraps"],
                        "exempt": tags["is_override"] or tags["is_abstractmethod"] or tags["is_wraps"],
                    }
                )
                if isinstance(node, ast.ClassDef):
                    walk_scope(
                        node.body,
                        prefix + node.name + ".",
                        in_class=True,
                        in_function=in_function,
                    )
                else:
                    walk_scope(
                        node.body,
                        prefix + node.name + ".<locals>.",
                        in_class=False,
                        in_function=True,
                    )

        walk_scope(tree.body, "", in_class=False, in_function=False)
        items.sort(key=lambda row: (row["line"], row["qualname"]))
        return _has_docstring(tree), items

    # ------------------------------------------------------------------ #
    # scan mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_scan(cls, module_docstring: bool, items: list[dict[str, Any]]) -> dict[str, Any]:
        """Return the full inventory (rows capped at max_items)."""
        result: dict[str, Any] = {
            "mode": "scan",
            "module_docstring": module_docstring,
        }
        if len(items) > cls.max_items:
            result["items"] = items[: cls.max_items]
            result["items_truncated"] = True
            result["items_total"] = len(items)
        else:
            result["items"] = items
        return result

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _requiring(cls, row: dict[str, Any]) -> bool:
        """True when a row is part of the audited public API surface."""
        return row["is_public"] and not row["is_nested"] and not row["exempt"]

    @classmethod
    def _coverage(cls, total: int, documented: int) -> float:
        """The reported 1-decimal percentage; 100.0 when total is 0."""
        if total == 0:
            return 100.0
        return round(100.0 * documented / total, 1)

    @classmethod
    def _summarize(cls, module_docstring: bool, items: list[dict[str, Any]]) -> dict[str, Any]:
        """Compute the CI-gate numbers over the audit surface."""
        requiring = [row for row in items if cls._requiring(row)]
        documented = [row for row in requiring if row["has_docstring"]]
        undocumented = [
            {
                "qualname": row["qualname"],
                "line": row["line"],
                "kind": row["kind"],
            }
            for row in requiring
            if not row["has_docstring"]
        ]
        by_kind = {
            kind: {
                "total": sum(1 for row in requiring if row["kind"] == kind),
                "documented": sum(1 for row in documented if row["kind"] == kind),
            }
            for kind in cls.KINDS
        }
        return {
            "mode": "summary",
            "module_docstring": module_docstring,
            "total_public": len(requiring),
            "documented_public": len(documented),
            "exempt_public": sum(1 for row in items if row["is_public"] and not row["is_nested"] and row["exempt"]),
            "coverage_pct": cls._coverage(len(requiring), len(documented)),
            "by_kind": by_kind,
            "undocumented": undocumented[: cls.max_undocumented],
            "undocumented_total": len(undocumented),
            "truncated": len(undocumented) > cls.max_undocumented,
        }

    # ------------------------------------------------------------------ #
    # check mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_check(
        cls,
        summary: dict[str, Any],
        items: list[dict[str, Any]],
        thresholds: tuple[int, float, float],
    ) -> dict[str, Any]:
        """Apply the thresholds; one pass/fail row per gate."""
        min_module, min_public, min_class = thresholds
        class_rows = [row for row in items if cls._requiring(row) and row["kind"] in ("class", "method")]
        class_undocumented = [
            {
                "qualname": row["qualname"],
                "line": row["line"],
                "kind": row["kind"],
            }
            for row in class_rows
            if not row["has_docstring"]
        ]
        class_coverage = cls._coverage(
            len(class_rows),
            len(class_rows) - len(class_undocumented),
        )

        module_passed = int(summary["module_docstring"]) >= min_module
        public_passed = summary["coverage_pct"] >= min_public
        class_passed = class_coverage >= min_class
        checks: list[dict[str, Any]] = [
            {
                "check": "module_docstring",
                "passed": module_passed,
                "threshold": min_module,
                "offenders": [{"qualname": "<module>", "line": 1, "kind": "module"}] if not module_passed else [],
            },
            {
                "check": "public_coverage",
                "passed": public_passed,
                "threshold": min_public,
                "coverage_pct": summary["coverage_pct"],
                "undocumented_total": summary["undocumented_total"],
                "offenders": summary["undocumented"] if not public_passed else [],
            },
            {
                "check": "class_coverage",
                "passed": class_passed,
                "threshold": min_class,
                "coverage_pct": class_coverage,
                "undocumented_total": len(class_undocumented),
                "offenders": class_undocumented[: cls.max_undocumented] if not class_passed else [],
            },
        ]
        return {
            "mode": "check",
            "module_docstring": summary["module_docstring"],
            "passed": all(entry["passed"] for entry in checks),
            "thresholds": {
                "min_module": min_module,
                "min_public": min_public,
                "min_class": min_class,
            },
            "checks": checks,
        }

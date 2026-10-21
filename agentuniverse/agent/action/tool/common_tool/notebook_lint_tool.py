#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: notebook_lint_tool.py

"""Jupyter notebook (.ipynb) *structural* linting tool built purely on
the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the nbformat notebook SCHEMA layer: a .ipynb file is
JSON, so the sibling JsonLintTool (#4018) already covers its generic
JSON quality (duplicate keys, trailing commas, BOM, NaN literals) and
MarkdownLintTool (#4014) already covers the *prose* inside markdown
cells — but neither knows what a notebook *is*. This tool implements
the structure the nbformat v4 specification (4.0-4.5) demands of the
document: cell composition, execution counts, output shapes, mime
bundles, cell ids and kernel metadata, with exact line positions and
no network access and no third-party dependencies.

Every schema fact below was hand-embedded from the official nbformat
v4.5 JSON schema (``nbformat/v4/nbformat.v4.5.schema.json``) and then
cross-verified empirically against ``nbformat.validate`` 5.11 —
the verification oracle of the test suite:

* top level — ``metadata``/``nbformat``/``nbformat_minor``/``cells``
  are all required; the schema sets ``additionalProperties: false``,
  so unknown top-level keys are *rejected* (verified: validate raises
  "Additional properties are not allowed"); ``nbformat`` must be the
  integer 4 (schema ``minimum: 4, maximum: 4`` — 3 and 5 both raise);
  ``nbformat_minor`` an integer >= 0 (negative raises "No schema for
  validating v4.-1 notebooks", minors above the newest known schema
  fall back to the latest — verified VALID at 6 and 99 — so an
  unrecognized minor is reported info-only);
* cells — must be an array of objects; each cell is exactly one of
  ``code`` / ``markdown`` / ``raw`` (``oneOf`` with
  ``additionalProperties: false`` per branch, which the tool mirrors
  per type: ``outputs``/``execution_count`` only belong to code cells,
  ``attachments`` only to markdown/raw — verified: a markdown cell
  carrying ``outputs`` raises "Additional properties are not
  allowed"). Required per type: all cells need ``cell_type``,
  ``metadata``, ``source``; code cells additionally need ``outputs``
  and ``execution_count``; only 4.5+ requires ``id`` — and, the
  direction that surprises people, pre-4.5 schemas have no ``id``
  property at all, so ids on a 4.4 notebook are *rejected* by the
  schema (verified: "Additional properties are not allowed ('id')");
* ``execution_count`` — null or a non-negative integer (verified:
  1.5 raises "is not of type 'integer', 'null'", -1 raises "is less
  than the minimum of 0", and a JSON ``true`` also raises — Python's
  ``isinstance(True, int)`` is true, so the tool excludes ``bool``
  explicitly);
* outputs — ``output_type`` selects one of four shapes:
  ``stream`` → ``name`` string + ``text`` multiline; ``display_data``
  → ``data`` mime bundle + ``metadata`` object; ``execute_result`` →
  ``data`` + ``metadata`` + ``execution_count``; ``error`` →
  ``ename``/``evalue`` strings + ``traceback`` array of strings (all
  verified as required-and-typed by validate); unknown output types
  raise "not valid under any of the given schemas";
* mime bundles — a dict whose values are "multiline strings" (string
  or array of strings; verified ``42`` raises) — with one documented
  exception: the schema's ``patternProperties`` rule
  ``^application/(.*\\+)?json$`` overrides ``additionalProperties``
  and lets JSON mime values be ANY type ("Mimetypes with JSON
  output, can be any type" — verified: validate accepts an object
  payload). Two value checks go *beyond* the schema and are
  therefore reported under distinct codes excluded from the schema
  verdict: a text-form ``application/json`` (or ``+json``) payload
  that does not parse (validate accepts it — verified), and an
  ``image/*`` payload whose text is not base64 (also accepted —
  verified);
* metadata — ``kernelspec`` when present must be an object with
  string ``name`` and ``display_name`` (verified: missing
  ``display_name`` raises); ``language_info`` when present must be an
  object with string ``name`` (the one required field of that
  definition — verified); ``orig_nbformat`` integer >= 1;
  ``metadata.widgets`` is free-form per the schema (no definition
  constrains it) so widget quirks stay info-only;
* cell ids — the real pattern of the v4.5 schema is
  ``^[a-zA-Z0-9-_]+$`` with length 1..64 (hand-embedded verbatim;
  verified: "bad id!" and a 65-character id both raise). Two further
  id rules are *stricter than validate*: nbformat 5.11 *repairs*
  missing ids (``MissingIDFieldWarning``) and duplicate ids
  (``DuplicateCellId``, auto-corrected to a fresh random id) instead
  of raising — verified. The tool reports both as errors under the
  distinct codes ``cell_id_missing`` / ``cell_id_duplicate``,
  documenting that nbformat's own warning says missing ids "will
  become a hard error in future nbformat versions". Those two codes
  (plus every other style/extra check) are excluded from the schema
  agreement verdict so the oracle comparison in the tests counts
  schema strictness only;
* nbformat 4.0-4.5 differences (support matrix, from diffing the six
  per-minor schema files): 4.0-4.4 require identical cell fields and
  forbid ids; 4.5 adds ``id``; notebook metadata gained ``title`` /
  ``authors`` in 4.2 (informational only — notebook metadata allows
  additional properties). No other structural differences exist.

``lint`` mode returns findings ``{line, code, message, severity}``
where ``line`` is the 1-based line of the offending value in the
notebook text, produced by a JSON path→line mapper: a single
recursive-descent scan of the *already-parsed-OK* text records the
start offset of every key, value and container, and each finding path
(e.g. ``('cells', 3, 'outputs', 0, 'execution_count')``) is resolved
through it; when a path is not derivable (a *missing* key has no
position) the containing object's line is used, else 1. JSON syntax
failures mirror ``json.JSONDecodeError`` ``msg``/``pos`` → line (the
same converter the tests cross-check against the exception's own
``lineno``/``colno``).

``summary`` mode describes the notebook: cell counts by type,
executed vs unexecuted code cells (by ``execution_count``), output
totals and error outputs, the maximum execution count with a
monotonicity check (execution counts should never regress within one
kernel session — a smaller count after a bigger one means the
notebook was re-run out of order; each regression is flagged with
both cell indexes), the mime types used across all outputs, and the
id health ``{present, unique, valid}`` with offending cell indexes.

``check_ids`` mode is a read-only id report: per-cell id presence,
real-pattern validity and duplicate groups with cell indexes. It
deliberately never regenerates or rewrites ids — unlike
``nbformat.normalize()``, which silently assigns new (random!) ids —
and says so in its output, because mutating ids breaks external
references (e.g. JupyterLab's cell anchors) and random repair makes
diffs non-deterministic.

Input validation is strict and happens before any computation:
``mode`` must be one of the three, ``notebook`` must be the notebook
*text* of at most 1,000,000 characters; violations raise a
``ValueError``, mirroring the other common tools. For ``lint`` a
notebook that does not parse is a *finding*, not an error;
``summary``/``check_ids`` cannot proceed on a broken document and
return a structured ``error`` payload instead. The tool is
deterministic — output is a pure function of the input, findings
sorted by (line, code, message) — and read-only: the input text is
never modified.
"""

import json
import re
from typing import Any, ClassVar, Dict, FrozenSet, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Input size limit (bounded purely to reject pathological inputs
# early; far above real notebooks).
_MAX_TEXT = 1_000_000

# Newest nbformat minor this tool has schema ground truth for (4.5).
_KNOWN_MINOR_MAX = 5

# Cell types of the nbformat v4 oneOf (hand-embedded from the
# nbformat.v4.5.schema.json definitions cell → oneOf).
_CELL_TYPES = ("code", "markdown", "raw")

# The REAL cell id pattern of the v4.5 schema (definition "cell_id"):
# "type": "string", "pattern": "^[a-zA-Z0-9-_]+$",
# "minLength": 1, "maxLength": 64 — embedded verbatim, verified
# against nbformat.validate ("bad id!" / 65-char id both raise).
_CELL_ID_RE = re.compile(r"\A[a-zA-Z0-9-_]+\Z")
_CELL_ID_MIN = 1
_CELL_ID_MAX = 64
# Canonical style of nbformat's own id generator ([a-z0-9-]) — info
# only, the schema itself accepts the wider charset above.
_CANONICAL_ID_RE = re.compile(r"\A[a-z0-9-]+\Z")

# Fields required by every cell type (schema required lists, minus
# id which is 4.5-only and handled separately).
_COMMON_CELL_REQUIRED = ("cell_type", "metadata", "source")
_CODE_ONLY_REQUIRED = ("outputs", "execution_count")

# Fields each cell type allows (schema additionalProperties: false
# per branch — anything else is rejected by validate).
_COMMON_CELL_ALLOWED = frozenset({"cell_type", "metadata", "source", "id"})
_CELL_ALLOWED = {
    "code": _COMMON_CELL_ALLOWED | {"outputs", "execution_count"},
    "markdown": _COMMON_CELL_ALLOWED | {"attachments"},
    "raw": _COMMON_CELL_ALLOWED | {"attachments"},
}

# Output shapes: output_type -> (required fields, field types).
_OUTPUT_SHAPES: Dict[str, Tuple[Tuple[str, ...], Dict[str, Any]]] = {
    "stream": (
        ("name", "text"),
        {"name": "string", "text": "multiline"},
    ),
    "display_data": (
        ("data", "metadata"),
        {"data": "mimebundle", "metadata": "object"},
    ),
    "execute_result": (
        ("data", "metadata", "execution_count"),
        {"data": "mimebundle", "metadata": "object",
         "execution_count": "execution_count"},
    ),
    "error": (
        ("ename", "evalue", "traceback"),
        {"ename": "string", "evalue": "string",
         "traceback": "string_array"},
    ),
}

# Mime key checks (value level; schema only demands multiline strings
# — the two extra value checks are distinct-code extras).
_JSON_MIME_RE = re.compile(r"\Aapplication/(.*\+)?json\Z")
_IMAGE_MIME_RE = re.compile(r"\Aimage/[a-z0-9.+-]+\Z")
# Base64 alphabet + padding + embedded whitespace (joinable arrays).
_B64_RE = re.compile(r"\A[A-Za-z0-9+/=\s]+\Z")

# Findings whose codes mirror exactly what the nbformat schema (and
# therefore nbformat.validate) rejects. Only these drive the
# ``schema_conformant`` verdict and the test-suite oracle agreement;
# every other code is a documented stricter/extra check.
_SCHEMA_CODES: FrozenSet[str] = frozenset({
    "json_syntax_error",
    "empty_document",
    "root_not_object",
    "required_key_missing",
    "unexpected_top_level_key",
    "nbformat_major_invalid",
    "nbformat_minor_invalid",
    "metadata_invalid",
    "cells_not_array",
    "cell_not_object",
    "cell_type_missing",
    "cell_type_invalid",
    "required_cell_field_missing",
    "unexpected_cell_field",
    "source_invalid_type",
    "source_item_not_string",
    "execution_count_invalid",
    "outputs_not_array",
    "output_not_object",
    "output_type_missing",
    "output_type_unknown",
    "output_field_missing",
    "output_field_invalid",
    "unexpected_output_field",
    "mime_value_invalid",
    "attachments_invalid",
    "attachment_value_invalid",
    "cell_id_invalid",
    "kernelspec_invalid",
    "language_info_invalid",
    "orig_nbformat_invalid",
})

# Keys the top-level notebook object allows (schema properties;
# additionalProperties is false — unknown keys are rejected).
_TOP_ALLOWED = frozenset({"cells", "metadata", "nbformat", "nbformat_minor"})
_TOP_REQUIRED = ("cells", "metadata", "nbformat", "nbformat_minor")

_WS = " \t\r\n"


def _pos_to_line(text: str, pos: int) -> int:
    """Convert a 0-based character offset into a 1-based line number.

    Same convention as ``json.JSONDecodeError.lineno`` (the tests
    cross-verify the two against each other on malformed corpora).
    """
    return text.count("\n", 0, pos) + 1


def _finding(
    code: str, severity: str, line: int, message: str
) -> Dict[str, Any]:
    """Build one ordered finding dict (line first — the contract)."""
    return {
        "line": line,
        "code": code,
        "message": message,
        "severity": severity,
    }


def _is_int(value: Any) -> bool:
    """JSON-Schema 'integer': a true int, never a bool (JSON has no
    bool-as-1; jsonschema rejects ``True`` where integer is demanded
    — verified against nbformat.validate)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _is_multiline(value: Any) -> bool:
    """Schema 'multiline_string': string or array of strings."""
    if isinstance(value, str):
        return True
    if isinstance(value, list):
        return all(isinstance(item, str) for item in value)
    return False


def _is_execution_count(value: Any) -> bool:
    """Schema execution_count: null or non-negative integer."""
    return value is None or (_is_int(value) and value >= 0)


def _multiline_text(value: Any) -> str:
    """Join a multiline string into plain text (empty on bad shape)."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(item for item in value if isinstance(item, str))
    return ""


class _LineIndex:
    """JSON path → line mapper over an *already-parsed-OK* text.

    One recursive-descent scan records the start offset of every
    key token, scalar value and container opener, keyed by the value
    path (``('cells', 0, 'outputs', 2, 'execution_count')``). Lookup
    resolves the exact path, then falls back to the nearest recorded
    ancestor (a *missing* required field has no position of its own —
    the containing cell/object line is the honest answer), else 1.
    """

    def __init__(self, text: str) -> None:
        self._text = text
        self._pos: Dict[Tuple[Any, ...], int] = {}
        self._walk(0, (), first=True)
        # Root object position is always derivable for parsed JSON.
        self._pos.setdefault((), 0)

    # -- scanning -----------------------------------------------------
    def _skip_ws(self, i: int) -> int:
        text = self._text
        n = len(text)
        while i < n and text[i] in _WS:
            i += 1
        return i

    def _scan_string(self, i: int) -> int:
        """Return index just past the string starting at i."""
        text = self._text
        n = len(text)
        j = i + 1
        while j < n:
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == '"':
                return j + 1
            j += 1
        return n  # unreachable: json.loads already succeeded

    def _scan_literal(self, i: int) -> int:
        text = self._text
        n = len(text)
        j = i
        while j < n and (text[j].isalnum() or text[j] in "-+.eE"):
            j += 1
        return j

    def _walk(self, i: int, path: Tuple[Any, ...], first: bool = False) -> int:
        i = self._skip_ws(i)
        text = self._text
        if i >= len(text):
            return i
        c = text[i]
        if c == '"':
            if first:
                self._pos[path] = i  # scalar root
            return self._scan_string(i)
        if c == "{":
            self._pos[path] = i
            j = self._skip_ws(i + 1)
            while j < len(text) and text[j] != "}":
                key_start = j
                j = self._scan_string(j)
                raw = text[key_start:j]
                try:
                    key = json.loads(raw)
                except ValueError:  # pragma: no cover - parsed already
                    key = raw
                key_path = path + (key,)
                self._pos[key_path] = key_start
                j = self._skip_ws(j)
                if j < len(text) and text[j] == ":":
                    j = self._walk(j + 1, key_path)
                j = self._skip_ws(j)
                if j < len(text) and text[j] == ",":
                    j = self._skip_ws(j + 1)
            return j + 1
        if c == "[":
            self._pos[path] = i
            j = self._skip_ws(i + 1)
            idx = 0
            while j < len(text) and text[j] != "]":
                j = self._walk(j, path + (idx,))
                idx += 1
                j = self._skip_ws(j)
                if j < len(text) and text[j] == ",":
                    j = self._skip_ws(j + 1)
            return j + 1
        # true / false / null / number
        if first:
            self._pos[path] = i
        return self._scan_literal(i)

    # -- lookup -------------------------------------------------------
    def line(
        self,
        path: Tuple[Any, ...],
        fallback: Optional[Tuple[Any, ...]] = None,
    ) -> int:
        """Line of the value at ``path``; nearest ancestor otherwise."""
        for probe in (path, fallback):
            if probe is None:
                continue
            for k in range(len(probe), -1, -1):
                pos = self._pos.get(probe[:k])
                if pos is not None:
                    return _pos_to_line(self._text, pos)
        return 1


class NotebookLintTool(Tool):
    """Jupyter notebook (.ipynb JSON) structural linter — pure stdlib.

    Attributes:
        max_text (int): Upper bound on the accepted notebook text;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "notebook_lint_tool"
    description: str = (
        "Jupyter notebook (.ipynb JSON) structural linting tool — "
        "pure Python stdlib, no network required, no third-party "
        "dependencies. Lint a notebook text (mode='lint') against "
        "the nbformat v4 (4.0-4.5) schema layer with exact line "
        "positions via a JSON path-to-line mapper: cell structure "
        "and per-type fields, execution_count null-or-int rules, "
        "output shapes (stream/display_data/execute_result/error), "
        "mime bundle validity, cell id pattern (the real "
        "^[a-zA-Z0-9-_]+$ 1..64 rule of the v4.5 schema) with "
        "duplicate detection, kernelspec/language_info metadata, "
        "and the 4.0-4.5 version matrix (ids introduced in 4.5, "
        "rejected before it). Summarize a notebook (mode='summary': "
        "cell counts by type, executed/unexecuted code cells, "
        "output totals and error outputs, max execution count with "
        "monotonicity regression detection, mime types used, id "
        "health) or audit cell ids read-only (mode='check_ids': "
        "per-cell presence/validity/duplicates with cell indexes — "
        "never regenerates ids, unlike nbformat.normalize)."
    )

    MODES: ClassVar[tuple] = ("lint", "summary", "check_ids")

    max_text: int = _MAX_TEXT

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        notebook: Any = None,
    ) -> Dict[str, Any]:
        """Run one notebook linting operation.

        Args:
            mode (str): One of ``lint`` / ``summary`` / ``check_ids``.
            notebook (str): The .ipynb file **text** (JSON) to
                inspect.

        Returns:
            Dict[str, Any]: For ``lint``: ``findings`` (each
            ``{line, code, message, severity}``) plus a summary and
            the ``schema_conformant`` verdict. For ``summary``: the
            structural statistics of the notebook. For
            ``check_ids``: the read-only id audit.
        """
        if not isinstance(mode, str) or mode not in self.MODES:
            raise ValueError(
                "mode must be one of "
                f"{', '.join(self.MODES)} (got {mode!r})"
            )
        if not isinstance(notebook, str):
            raise ValueError(
                "notebook must be the .ipynb text (a str) to lint "
                f"(got {type(notebook).__name__})"
            )
        if len(notebook) > self.max_text:
            raise ValueError(
                f"notebook exceeds the {self.max_text}-character cap "
                f"({len(notebook)} characters)"
            )

        if mode == "lint":
            return self._lint(notebook)
        if mode == "summary":
            return self._summary(notebook)
        return self._check_ids(notebook)

    # ------------------------------------------------------------------ #
    # shared parse step
    # ------------------------------------------------------------------ #

    def _parse(
        self, notebook: str
    ) -> Tuple[Optional[Any], Optional["_LineIndex"],
               List[Dict[str, Any]], bool]:
        """Parse the notebook text.

        Returns (root, line_index, findings, ok). On failure the
        findings carry the single syntax finding and root/index are
        None.
        """
        if not notebook.strip():
            return None, None, [_finding(
                "empty_document", "error", 1,
                "Notebook is empty (or whitespace-only) — a "
                ".ipynb file must be a JSON object",
            )], False
        try:
            root = json.loads(notebook)
        except json.JSONDecodeError as exc:
            line = _pos_to_line(notebook, exc.pos)
            return None, None, [_finding(
                "json_syntax_error", "error", line,
                f"Notebook is not valid JSON: {exc.msg} "
                f"(line {exc.lineno}, column {exc.colno})",
            )], False
        index = _LineIndex(notebook)
        return root, index, [], True

    # ------------------------------------------------------------------ #
    # lint
    # ------------------------------------------------------------------ #

    def _lint(self, notebook: str) -> Dict[str, Any]:
        root, index, findings, ok = self._parse(notebook)
        if not ok:
            return self._lint_result(findings, notebook)
        if not isinstance(root, dict):
            findings.append(_finding(
                "root_not_object", "error", index.line(()),
                f"Notebook root must be a JSON object, got "
                f"{type(root).__name__} — the nbformat schema "
                "requires the notebook object "
                "{cells, metadata, nbformat, nbformat_minor}",
            ))
            return self._lint_result(findings, notebook)

        minor = self._check_top_level(root, index, findings)
        cells = self._check_cells(root, index, minor, findings)
        self._check_metadata(root, index, findings)
        self._check_style(root, index, cells, findings)

        return self._lint_result(findings, notebook)

    def _lint_result(
        self, findings: List[Dict[str, Any]], notebook: str
    ) -> Dict[str, Any]:
        """Sort findings deterministically and build the verdict."""
        findings.sort(key=lambda f: (f["line"], f["code"], f["message"]))
        code_counts: Dict[str, int] = {}
        severity_counts = {"error": 0, "warning": 0, "info": 0}
        schema_errors = 0
        for f in findings:
            code_counts[f["code"]] = code_counts.get(f["code"], 0) + 1
            severity_counts[f["severity"]] += 1
            if f["code"] in _SCHEMA_CODES:
                schema_errors += 1
        return {
            "mode": "lint",
            "schema_conformant": schema_errors == 0,
            "schema_error_count": schema_errors,
            "findings": findings,
            "summary": {
                "findings": len(findings),
                "severity_counts": severity_counts,
                "rule_counts": dict(sorted(code_counts.items())),
                "lines": len(notebook.splitlines()),
                "chars": len(notebook),
            },
        }

    # -- top level ------------------------------------------------------

    def _check_top_level(
        self,
        root: Dict[str, Any],
        index: "_LineIndex",
        findings: List[Dict[str, Any]],
    ) -> Optional[int]:
        """Validate the notebook object itself; return nbformat_minor
        when derivable (int and >= 0)."""
        for key in _TOP_REQUIRED:
            if key not in root:
                findings.append(_finding(
                    "required_key_missing", "error",
                    index.line(("metadata",) if key == "metadata"
                               else ()),
                    f"Required top-level key {json.dumps(key)} is "
                    "missing — the nbformat schema requires all of "
                    "cells, metadata, nbformat, nbformat_minor",
                ))
        for key in root:
            if key not in _TOP_ALLOWED:
                findings.append(_finding(
                    "unexpected_top_level_key", "error",
                    index.line((key,)),
                    f"Unexpected top-level key {json.dumps(key)} — "
                    "the notebook schema sets additionalProperties: "
                    "false, so nbformat rejects unknown top-level "
                    "keys (verified against nbformat.validate)",
                ))

        major = root.get("nbformat")
        if "nbformat" in root and not (_is_int(major) and major == 4):
            findings.append(_finding(
                "nbformat_major_invalid", "error",
                index.line(("nbformat",)),
                f"nbformat must be the integer 4 (schema minimum 4, "
                f"maximum 4), got {json.dumps(major)}; older "
                "notebooks (v3) must be converted, not linted as-is",
            ))

        minor = root.get("nbformat_minor")
        minor_ok = _is_int(minor) and minor >= 0
        if "nbformat_minor" in root and not minor_ok:
            findings.append(_finding(
                "nbformat_minor_invalid", "error",
                index.line(("nbformat_minor",)),
                f"nbformat_minor must be a non-negative integer, got "
                f"{json.dumps(minor)} (nbformat: 'No schema for "
                "validating v4.-1 notebooks')",
            ))
        if minor_ok and minor > _KNOWN_MINOR_MAX:
            findings.append(_finding(
                "nbformat_minor_unknown", "info",
                index.line(("nbformat_minor",)),
                f"nbformat_minor {minor} is newer than the newest "
                f"schema this tool embeds (4.{_KNOWN_MINOR_MAX}); "
                "nbformat.validate falls back to the latest schema "
                "and accepts it, so checks continue under 4.5 rules",
            ))
        return minor if minor_ok else None

    # -- cells -----------------------------------------------------------

    def _check_cells(
        self,
        root: Dict[str, Any],
        index: "_LineIndex",
        minor: Optional[int],
        findings: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Validate the cells array; return the dict cells."""
        if "cells" not in root:
            return []
        cells = root["cells"]
        if not isinstance(cells, list):
            findings.append(_finding(
                "cells_not_array", "error", index.line(("cells",)),
                f"cells must be an array of cell objects, got "
                f"{type(cells).__name__}",
            ))
            return []
        if not cells:
            findings.append(_finding(
                "empty_cells_list", "info", index.line(("cells",)),
                "cells is an empty array — schema-legal, but the "
                "notebook contains no content",
            ))

        ids_required = minor is not None and minor >= 5
        seen_ids: Dict[str, List[int]] = {}
        dict_cells: List[Dict[str, Any]] = []
        for i, cell in enumerate(cells):
            path = ("cells", i)
            if not isinstance(cell, dict):
                findings.append(_finding(
                    "cell_not_object", "error", index.line(path),
                    f"cells[{i}] must be an object, got "
                    f"{type(cell).__name__}",
                ))
                continue
            dict_cells.append(cell)
            ctype = self._check_one_cell(
                cell, path, index, ids_required, findings)
            cell_id = cell.get("id")
            if isinstance(cell_id, str):
                seen_ids.setdefault(cell_id, []).append(i)

        # Duplicate ids — reported at each repeated occurrence.
        # nbformat 5.11 silently REPAIRS duplicates (DuplicateCellId
        # warning, fresh random id assigned) instead of raising, so
        # this code is deliberately outside the schema-verdict set.
        for cell_id, indexes in sorted(seen_ids.items()):
            if len(indexes) > 1:
                for i in indexes[1:]:
                    findings.append(_finding(
                        "cell_id_duplicate", "error",
                        index.line(("cells", i, "id"), ("cells", i)),
                        f"Duplicate cell id {json.dumps(cell_id)} at "
                        f"cells[{i}] — already used by "
                        f"cells[{indexes[0]}]; nbformat 5.1+ "
                        "auto-corrects "
                        "duplicates with a random id (breaking "
                        "external references), so ids must be made "
                        "unique by hand",
                    ))
        return dict_cells

    def _check_one_cell(
        self,
        cell: Dict[str, Any],
        path: Tuple[Any, ...],
        index: "_LineIndex",
        ids_required: bool,
        findings: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Validate one dict cell; return its cell_type if known."""
        i = path[1]
        ctype = cell.get("cell_type")

        if "cell_type" not in cell:
            findings.append(_finding(
                "cell_type_missing", "error", index.line(path),
                f"cells[{i}] is missing cell_type — every cell must "
                "declare one of code, markdown, raw",
            ))
        elif not isinstance(ctype, str) or ctype not in _CELL_TYPES:
            findings.append(_finding(
                "cell_type_invalid", "error",
                index.line(path + ("cell_type",), path),
                f"cells[{i}] has invalid cell_type "
                f"{json.dumps(ctype)} — the schema oneOf allows "
                "exactly code, markdown, raw",
            ))
            ctype = None

        # Required fields per type (id is 4.5-only and reported
        # under its own distinct code — nbformat silently repairs
        # missing ids instead of raising, so cell_id_missing must
        # stay outside the schema-verdict set).
        required = list(_COMMON_CELL_REQUIRED)
        if ctype == "code":
            required += list(_CODE_ONLY_REQUIRED)
        if ids_required and "id" not in cell:
            findings.append(_finding(
                "cell_id_missing", "error",
                index.line(path),
                f"cells[{i}] has no id — nbformat 4.5+ requires "
                "one per cell; nbformat 5.1+ still auto-assigns a "
                "random id with a warning ('this will become a hard "
                "error in future nbformat versions'), so add the id "
                "explicitly to keep diffs and references stable",
            ))
        for field in required:
            if field not in cell:
                findings.append(_finding(
                    "required_cell_field_missing", "error",
                    index.line(path + (field,), path),
                    f"cells[{i}]"
                    + (f" ({ctype})" if ctype else "")
                    + f" is missing required field {json.dumps(field)}"
                    + (" — required by nbformat 4.5+"
                       if field == "id" else ""),
                ))

        # Allowed fields per type (additionalProperties: false).
        # id exists only in the 4.5 schema — pre-4.5 schemas have no
        # id property, so nbformat REJECTS ids there (verified).
        allowed = set(_CELL_ALLOWED.get(
            ctype, _COMMON_CELL_ALLOWED | {"outputs", "execution_count",
                                           "attachments"}))
        if not ids_required:
            allowed.discard("id")
        for field in cell:
            if field in allowed:
                continue
            line = index.line(path + (field,), path)
            if field == "id":
                findings.append(_finding(
                    "unexpected_cell_field", "error", line,
                    f"cells[{i}] carries an id but the notebook is "
                    "older than nbformat 4.5 — pre-4.5 schemas have "
                    "no id property and nbformat rejects it "
                    "(verified: 'Additional properties are not "
                    "allowed (id)')",
                ))
            elif field in ("outputs", "execution_count"):
                findings.append(_finding(
                    "unexpected_cell_field", "error", line,
                    f"cells[{i}] is a {ctype} cell but carries "
                    f"{json.dumps(field)} — only code cells have "
                    "outputs/execution_count (schema "
                    "additionalProperties: false per branch)",
                ))
            elif field == "attachments":
                findings.append(_finding(
                    "unexpected_cell_field", "error", line,
                    f"cells[{i}] is a code cell but carries "
                    "attachments — only markdown/raw cells may hold "
                    "attachments",
                ))
            else:
                findings.append(_finding(
                    "unexpected_cell_field", "error", line,
                    f"cells[{i}] has unknown field "
                    f"{json.dumps(field)} — the cell schema sets "
                    "additionalProperties: false",
                ))

        # metadata must be an object.
        if "metadata" in cell and not isinstance(cell["metadata"], dict):
            findings.append(_finding(
                "required_cell_field_missing", "error",
                index.line(path + ("metadata",), path),
                f"cells[{i}] metadata must be an object, got "
                f"{type(cell['metadata']).__name__}",
            ))

        # source: multiline string.
        if "source" in cell:
            src = cell["source"]
            src_path = path + ("source",)
            if not _is_multiline(src):
                findings.append(_finding(
                    "source_invalid_type", "error",
                    index.line(src_path, path),
                    f"cells[{i}] source must be a string or an array "
                    f"of strings, got {type(src).__name__}",
                ))
            elif isinstance(src, list):
                for j, item in enumerate(src):
                    if not isinstance(item, str):
                        findings.append(_finding(
                            "source_item_not_string", "error",
                            index.line(src_path + (j,), src_path),
                            f"cells[{i}] source[{j}] must be a "
                            f"string, got {type(item).__name__}",
                        ))
                        break

        # execution_count: null-or-non-negative-int, bool excluded.
        if "execution_count" in cell:
            ec = cell["execution_count"]
            if not _is_execution_count(ec):
                detail = (
                    "a float — JSON Schema integer excludes it"
                    if isinstance(ec, float)
                    else "a boolean — jsonschema treats bool as not "
                         "integer even where Python does"
                    if isinstance(ec, bool)
                    else "negative — schema minimum is 0"
                    if _is_int(ec)
                    else f"of type {type(ec).__name__}"
                )
                findings.append(_finding(
                    "execution_count_invalid", "error",
                    index.line(path + ("execution_count",), path),
                    f"cells[{i}] execution_count must be null or a "
                    f"non-negative integer ({json.dumps(ec)} is "
                    f"{detail})",
                ))

        # id pattern (the REAL v4.5 pattern) — schema error.
        if "id" in cell:
            cid = cell["id"]
            if not isinstance(cid, str) or not _CELL_ID_RE.match(cid) \
                    or not (_CELL_ID_MIN <= len(cid) <= _CELL_ID_MAX):
                why = (
                    "not a string"
                    if not isinstance(cid, str)
                    else "empty (minLength 1)"
                    if len(cid) == 0
                    else f"{len(cid)} characters long (maxLength 64)"
                    if len(cid) > _CELL_ID_MAX
                    else "it matches characters outside "
                         "[a-zA-Z0-9-_]"
                )
                findings.append(_finding(
                    "cell_id_invalid", "error",
                    index.line(path + ("id",), path),
                    f"cells[{i}] id {json.dumps(cid) if isinstance(cid, str) else repr(cid)} "
                    f"is invalid ({why}) — the v4.5 schema demands "
                    "^[a-zA-Z0-9-_]+$ with length 1..64 "
                    "(hand-embedded from the schema's cell_id "
                    "definition)",
                ))
            elif not _CANONICAL_ID_RE.match(cid):
                findings.append(_finding(
                    "cell_id_style", "info",
                    index.line(path + ("id",), path),
                    f"cells[{i}] id {json.dumps(cid)} is "
                    "schema-valid but outside nbformat's canonical "
                    "generator charset [a-z0-9-] — fine for old "
                    "notebooks, new tools should let the generator "
                    "mint ids",
                ))

        # outputs (code only; presence on md/raw flagged above).
        if ctype == "code" and "outputs" in cell:
            self._check_outputs(cell["outputs"], path + ("outputs",),
                                index, findings)

        # attachments (markdown/raw only).
        if ctype in ("markdown", "raw") and "attachments" in cell:
            self._check_attachments(
                cell["attachments"], path + ("attachments",),
                index, findings)
        return ctype

    # -- outputs -----------------------------------------------------------

    def _check_outputs(
        self,
        outputs: Any,
        path: Tuple[Any, ...],
        index: "_LineIndex",
        findings: List[Dict[str, Any]],
    ) -> None:
        i = path[1]
        if not isinstance(outputs, list):
            findings.append(_finding(
                "outputs_not_array", "error", index.line(path),
                f"cells[{i}] outputs must be an array, got "
                f"{type(outputs).__name__}",
            ))
            return
        for j, out in enumerate(outputs):
            opath = path + (j,)
            if not isinstance(out, dict):
                findings.append(_finding(
                    "output_not_object", "error", index.line(opath),
                    f"cells[{i}] outputs[{j}] must be an object, "
                    f"got {type(out).__name__}",
                ))
                continue
            otype = out.get("output_type")
            if "output_type" not in out:
                findings.append(_finding(
                    "output_type_missing", "error",
                    index.line(opath),
                    f"cells[{i}] outputs[{j}] is missing "
                    "output_type",
                ))
                continue
            if not isinstance(otype, str) \
                    or otype not in _OUTPUT_SHAPES:
                findings.append(_finding(
                    "output_type_unknown", "error",
                    index.line(opath + ("output_type",), opath),
                    f"cells[{i}] outputs[{j}] has unknown "
                    f"output_type {json.dumps(otype)} — the schema "
                    "oneOf allows exactly stream, display_data, "
                    "execute_result, error",
                ))
                continue
            required, types = _OUTPUT_SHAPES[otype]
            for field in required:
                if field not in out:
                    findings.append(_finding(
                        "output_field_missing", "error",
                        index.line(opath + (field,), opath),
                        f"cells[{i}] outputs[{j}] ({otype}) is "
                        f"missing required field "
                        f"{json.dumps(field)}",
                    ))
            for field, kind in sorted(types.items()):
                if field not in out:
                    continue
                value = out[field]
                vpath = opath + (field,)
                self._check_output_field(
                    i, j, otype, field, kind, value, vpath,
                    index, findings)
            # additionalProperties: false on every output branch.
            allowed = set(required) | {"output_type"}
            for field in out:
                if field not in allowed:
                    findings.append(_finding(
                        "unexpected_output_field", "error",
                        index.line(opath + (field,), opath),
                        f"cells[{i}] outputs[{j}] ({otype}) has "
                        f"unknown field {json.dumps(field)} — "
                        "output schemas set additionalProperties: "
                        "false",
                    ))
            if otype == "stream":
                name = out.get("name")
                if isinstance(name, str) \
                        and name not in ("stdout", "stderr"):
                    findings.append(_finding(
                        "stream_name_unusual", "info",
                        index.line(opath + ("name",), opath),
                        f"stream name {json.dumps(name)} is not "
                        "stdout/stderr — schema-legal (any string "
                        "is accepted, verified), but frontends only "
                        "render the two standard streams",
                    ))

    def _check_output_field(
        self,
        i: int,
        j: int,
        otype: str,
        field: str,
        kind: str,
        value: Any,
        vpath: Tuple[Any, ...],
        index: "_LineIndex",
        findings: List[Dict[str, Any]],
    ) -> None:
        where = f"cells[{i}] outputs[{j}] ({otype}) {field}"
        if kind == "string":
            if not isinstance(value, str):
                findings.append(_finding(
                    "output_field_invalid", "error",
                    index.line(vpath),
                    f"{where} must be a string, got "
                    f"{type(value).__name__}",
                ))
        elif kind == "multiline":
            if not _is_multiline(value):
                findings.append(_finding(
                    "output_field_invalid", "error",
                    index.line(vpath),
                    f"{where} must be a string or array of strings, "
                    f"got {type(value).__name__}",
                ))
        elif kind == "string_array":
            if not isinstance(value, list) \
                    or not all(isinstance(x, str) for x in value):
                findings.append(_finding(
                    "output_field_invalid", "error",
                    index.line(vpath),
                    f"{where} must be an array of strings "
                    "(the traceback is a list of lines)",
                ))
        elif kind == "object":
            if not isinstance(value, dict):
                findings.append(_finding(
                    "output_field_invalid", "error",
                    index.line(vpath),
                    f"{where} must be an object, got "
                    f"{type(value).__name__}",
                ))
        elif kind == "execution_count":
            if not _is_execution_count(value):
                findings.append(_finding(
                    "output_field_invalid", "error",
                    index.line(vpath),
                    f"{where} must be null or a non-negative "
                    f"integer, got {json.dumps(value)}",
                ))
        elif kind == "mimebundle":
            if not isinstance(value, dict):
                findings.append(_finding(
                    "output_field_invalid", "error",
                    index.line(vpath),
                    f"{where} must be a mime-type keyed object, got "
                    f"{type(value).__name__}",
                ))
                return
            self._check_mime_bundle(
                value, vpath, index, findings)

    def _check_mime_bundle(
        self,
        bundle: Dict[str, Any],
        path: Tuple[Any, ...],
        index: "_LineIndex",
        findings: List[Dict[str, Any]],
    ) -> None:
        """Schema layer: values must be multiline strings.

        Two VALUE checks go beyond the schema (validate accepts any
        multiline payload — both verified) and therefore use
        distinct codes outside the schema-verdict set:
        unparseable application/json payloads and non-base64
        image/* payloads.
        """
        for mime, value in sorted(bundle.items()):
            vpath = path + (mime,)
            # JSON mimes are the schema's documented exception: the
            # patternProperties rule "^application/(.*\\+)?json$"
            # overrides additionalProperties and allows ANY value
            # ("Mimetypes with JSON output, can be any type") —
            # verified: validate accepts an object payload.
            if _JSON_MIME_RE.match(mime):
                if isinstance(value, (str, list)):
                    try:
                        json.loads(_multiline_text(value))
                    except ValueError:
                        findings.append(_finding(
                            "json_mime_unparseable", "warning",
                            index.line(vpath, path),
                            f"Mime entry {json.dumps(mime)} does not "
                            "contain parseable JSON — nbformat accepts "
                            "any payload here (verified), but "
                            "consumers expect JSON mime data to parse",
                        ))
                continue
            if not _is_multiline(value):
                findings.append(_finding(
                    "mime_value_invalid", "error",
                    index.line(vpath, path),
                    f"Mime entry {json.dumps(mime)} must be a string "
                    f"or array of strings, got "
                    f"{type(value).__name__}",
                ))
                continue
            text = _multiline_text(value)
            if _IMAGE_MIME_RE.match(mime) and not _B64_RE.match(text):
                findings.append(_finding(
                    "image_mime_not_base64", "warning",
                    index.line(vpath, path),
                    f"Mime entry {json.dumps(mime)} is not base64-"
                    "encoded — nbformat accepts it (verified), but "
                    "image payloads are base64 by convention and "
                    "will not render",
                ))

    def _check_attachments(
        self,
        attachments: Any,
        path: Tuple[Any, ...],
        index: "_LineIndex",
        findings: List[Dict[str, Any]],
    ) -> None:
        i = path[1]
        if not isinstance(attachments, dict):
            findings.append(_finding(
                "attachments_invalid", "error", index.line(path),
                f"cells[{i}] attachments must be an object keyed by "
                f"filename, got {type(attachments).__name__}",
            ))
            return
        for name in sorted(attachments):
            apath = path + (name,)
            bundle = attachments[name]
            if not isinstance(bundle, dict):
                findings.append(_finding(
                    "attachment_value_invalid", "error",
                    index.line(apath, path),
                    f"Attachment {json.dumps(name)} must be a mime "
                    f"bundle object, got {type(bundle).__name__}",
                ))
                continue
            self._check_mime_bundle(bundle, apath, index, findings)

    # -- notebook metadata ---------------------------------------------------

    def _check_metadata(
        self,
        root: Dict[str, Any],
        index: "_LineIndex",
        findings: List[Dict[str, Any]],
    ) -> None:
        if "metadata" not in root:
            return
        meta = root["metadata"]
        if not isinstance(meta, dict):
            findings.append(_finding(
                "metadata_invalid", "error",
                index.line(("metadata",)),
                f"notebook metadata must be an object, got "
                f"{type(meta).__name__}",
            ))
            return

        if "kernelspec" in meta:
            ks = meta["kernelspec"]
            kpath = ("metadata", "kernelspec")
            if not isinstance(ks, dict):
                findings.append(_finding(
                    "kernelspec_invalid", "error",
                    index.line(kpath, ("metadata",)),
                    f"kernelspec must be an object with name and "
                    f"display_name, got {type(ks).__name__}",
                ))
            else:
                for field in ("name", "display_name"):
                    if field not in ks:
                        findings.append(_finding(
                            "kernelspec_invalid", "error",
                            index.line(kpath + (field,), kpath),
                            f"kernelspec is missing required field "
                            f"{json.dumps(field)} (verified: "
                            "nbformat raises 'display_name is a "
                            "required property')",
                        ))
                    elif not isinstance(ks[field], str):
                        findings.append(_finding(
                            "kernelspec_invalid", "error",
                            index.line(kpath + (field,), kpath),
                            f"kernelspec {field} must be a string, "
                            f"got {type(ks[field]).__name__}",
                        ))

        if "language_info" in meta:
            li = meta["language_info"]
            lpath = ("metadata", "language_info")
            if not isinstance(li, dict):
                findings.append(_finding(
                    "language_info_invalid", "error",
                    index.line(lpath, ("metadata",)),
                    f"language_info must be an object, got "
                    f"{type(li).__name__}",
                ))
            elif "name" not in li:
                findings.append(_finding(
                    "language_info_invalid", "error",
                    index.line(lpath, ("metadata",)),
                    "language_info is missing required field "
                    "\"name\" — the only required field of the "
                    "language_info schema definition",
                ))
            elif not isinstance(li["name"], str):
                findings.append(_finding(
                    "language_info_invalid", "error",
                    index.line(lpath + ("name",), lpath),
                    "language_info name must be a string, got "
                    f"{type(li['name']).__name__}",
                ))

        if "orig_nbformat" in meta:
            onf = meta["orig_nbformat"]
            if not _is_int(onf) or onf < 1:
                findings.append(_finding(
                    "orig_nbformat_invalid", "error",
                    index.line(("metadata", "orig_nbformat"),
                               ("metadata",)),
                    f"orig_nbformat must be an integer >= 1, got "
                    f"{json.dumps(onf)}",
                ))

        if "widgets" in meta:
            findings.append(_finding(
                "widget_metadata_quirk", "info",
                index.line(("metadata", "widgets"), ("metadata",)),
                "metadata.widgets is present — the nbformat schema "
                "leaves it free-form (no definition constrains it), "
                "so this tool does not judge it; note the known "
                "quirk that widget state often survives re-runs "
                "stale (model ids of dead kernels)",
            ))

    # -- style / extra checks --------------------------------------------------

    def _check_style(
        self,
        root: Dict[str, Any],
        index: "_LineIndex",
        dict_cells: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
    ) -> None:
        cells = root.get("cells")
        if not isinstance(cells, list):
            return

        # source representation consistency across the notebook.
        string_cells = sum(
            1 for c in dict_cells if isinstance(c.get("source"), str))
        list_cells = sum(
            1 for c in dict_cells
            if isinstance(c.get("source"), list))
        if string_cells and list_cells:
            findings.append(_finding(
                "source_form_inconsistent", "info",
                index.line(("cells",)),
                f"Notebook mixes source forms — {string_cells} "
                f"cell(s) as string, {list_cells} as array of "
                "lines; both are schema-legal (multiline_string), "
                "but nbformat writes arrays of lines and mixing "
                "hurts diffs",
            ))

        # Trailing-newline convention on array-form sources.
        for i, cell in enumerate(cells):
            if not isinstance(cell, dict):
                continue
            src = cell.get("source")
            if not isinstance(src, list) or len(src) < 2:
                continue
            offending = [
                k for k, line in enumerate(src[:-1])
                if isinstance(line, str) and not line.endswith("\n")
            ]
            if offending:
                findings.append(_finding(
                    "source_trailing_newline", "info",
                    index.line(("cells", i, "source"),
                               ("cells", i)),
                    f"cells[{i}] source lines "
                    f"{offending} do not end with a newline — the "
                    "nbformat convention keeps the trailing \\n on "
                    "every line but the last so joining the array "
                    "reproduces the text exactly",
                ))

        # Execution count monotonicity (one kernel session: counts
        # must never regress; verified semantics: re-running an
        # earlier cell re-numbers it above all others).
        last_max = 0
        for k, cell in enumerate(cells):
            if not isinstance(cell, dict) \
                    or cell.get("cell_type") != "code":
                continue
            ec = cell.get("execution_count")
            if _is_execution_count(ec) and ec is not None:
                if ec < last_max:
                    findings.append(_finding(
                        "execution_count_regression", "warning",
                        index.line(("cells", k, "execution_count"),
                                   ("cells", k)),
                        f"cells[{k}] execution_count {ec} regressed "
                        f"below the earlier maximum {last_max} — "
                        "within one kernel session counts only "
                        "grow; a regression means cells were run "
                        "out of notebook order",
                    ))
                else:
                    last_max = ec

    # ------------------------------------------------------------------ #
    # summary
    # ------------------------------------------------------------------ #

    def _summary(self, notebook: str) -> Dict[str, Any]:
        root, index, findings, ok = self._parse(notebook)
        if not ok:
            return self._error_payload("summary", findings[0])
        if not isinstance(root, dict):
            return self._error_payload("summary", _finding(
                "root_not_object", "error", 1,
                f"Notebook root must be a JSON object, got "
                f"{type(root).__name__}",
            ))
        cells = root.get("cells")
        if not isinstance(cells, list):
            return self._error_payload("summary", _finding(
                "cells_not_array", "error", index.line(("cells",)),
                "cells must be an array of cell objects — nothing "
                f"to summarize (got "
                f"{'missing' if 'cells' not in root else type(cells).__name__})",
            ))

        count = {"total": len(cells), "code": 0, "markdown": 0,
                 "raw": 0, "unknown": 0, "non_object": 0}
        executed = unexecuted = invalid_ec = 0
        total_outputs = error_outputs = 0
        max_ec: Optional[int] = None
        regressions: List[Dict[str, Any]] = []
        mime_types: List[str] = []
        ids_present = 0
        ids_invalid: List[int] = []
        id_occurrences: Dict[str, List[int]] = {}
        last_max = 0

        for i, cell in enumerate(cells):
            if not isinstance(cell, dict):
                count["non_object"] += 1
                continue
            ctype = cell.get("cell_type")
            if ctype in _CELL_TYPES:
                count[ctype] += 1
            else:
                count["unknown"] += 1
            cid = cell.get("id")
            if isinstance(cid, str):
                ids_present += 1
                if not (_CELL_ID_RE.match(cid)
                        and _CELL_ID_MIN <= len(cid) <= _CELL_ID_MAX):
                    ids_invalid.append(i)
                id_occurrences.setdefault(cid, []).append(i)
            else:
                ids_invalid.append(i)

            if ctype != "code":
                continue
            ec = cell.get("execution_count")
            if _is_execution_count(ec):
                if ec is None:
                    unexecuted += 1
                else:
                    executed += 1
                    if max_ec is None or ec > max_ec:
                        max_ec = ec
                    if ec < last_max:
                        regressions.append({
                            "cell_index": i,
                            "execution_count": ec,
                            "previous_max": last_max,
                        })
                    else:
                        last_max = ec
            else:
                invalid_ec += 1

            outputs = cell.get("outputs")
            if isinstance(outputs, list):
                total_outputs += len(outputs)
                for out in outputs:
                    if isinstance(out, dict):
                        if out.get("output_type") == "error":
                            error_outputs += 1
                        data = out.get("data")
                        if isinstance(data, dict):
                            mime_types.extend(
                                m for m in data if isinstance(m, str))

        duplicates = [
            {"id": cid, "cell_indexes": ix}
            for cid, ix in sorted(id_occurrences.items())
            if len(ix) > 1
        ]
        minor = root.get("nbformat_minor")
        result = {
            "mode": "summary",
            "nbformat": root.get("nbformat"),
            "nbformat_minor": minor,
            "cell_count": count,
            "code_cells": count["code"],
            "executed": executed,
            "unexecuted": unexecuted,
            "invalid_execution_counts": invalid_ec,
            "total_outputs": total_outputs,
            "error_outputs": error_outputs,
            "max_execution_count": max_ec,
            "execution_regressions": regressions,
            "mime_types": sorted(set(mime_types)),
            "ids": {
                "present": ids_present == len(cells)
                and len(cells) > 0,
                "unique": not duplicates,
                "valid": not ids_invalid,
                "required": _is_int(minor) and minor >= 5,
                "present_count": ids_present,
                "duplicates": duplicates,
                "invalid_indexes": ids_invalid,
            },
        }
        return result

    # ------------------------------------------------------------------ #
    # check_ids
    # ------------------------------------------------------------------ #

    def _check_ids(self, notebook: str) -> Dict[str, Any]:
        root, index, findings, ok = self._parse(notebook)
        if not ok:
            return self._error_payload("check_ids", findings[0])
        if not isinstance(root, dict):
            return self._error_payload("check_ids", _finding(
                "root_not_object", "error", 1,
                f"Notebook root must be a JSON object, got "
                f"{type(root).__name__}",
            ))
        cells = root.get("cells")
        if not isinstance(cells, list):
            return self._error_payload("check_ids", _finding(
                "cells_not_array", "error", index.line(("cells",)),
                "cells must be an array of cell objects",
            ))

        occurrences: Dict[str, List[int]] = {}
        rows: List[Dict[str, Any]] = []
        for i, cell in enumerate(cells):
            if not isinstance(cell, dict):
                rows.append({
                    "cell_index": i, "cell_type": None,
                    "id": None, "present": False,
                    "pattern_valid": False, "duplicate": False,
                    "duplicates_with": [],
                    "note": "cell is not an object",
                })
                continue
            cid = cell.get("id")
            present = "id" in cell
            valid = (
                isinstance(cid, str) and _CELL_ID_RE.match(cid) is not None
                and _CELL_ID_MIN <= len(cid) <= _CELL_ID_MAX
            )
            if isinstance(cid, str):
                occurrences.setdefault(cid, []).append(i)
            rows.append({
                "cell_index": i,
                "cell_type": cell.get("cell_type"),
                "id": cid,
                "present": present,
                "pattern_valid": valid,
                "duplicate": False,  # filled below
                "duplicates_with": [],
            })

        duplicates = []
        for cid, ix in sorted(occurrences.items()):
            if len(ix) > 1:
                duplicates.append({"id": cid, "cell_indexes": ix})
                for row in rows:
                    if row["id"] == cid:
                        row["duplicate"] = True
                        row["duplicates_with"] = [
                            k for k in ix if k != row["cell_index"]
                        ]

        missing = [r["cell_index"] for r in rows if not r["present"]]
        invalid = [r["cell_index"] for r in rows
                   if r["present"] and not r["pattern_valid"]]
        minor = root.get("nbformat_minor")
        return {
            "mode": "check_ids",
            "read_only": True,
            "mutated": False,
            "note": (
                "Read-only audit: ids are reported, never "
                "regenerated. Unlike nbformat.normalize(), which "
                "silently assigns fresh RANDOM ids to missing/"
                "duplicate entries (breaking external cell "
                "references and making diffs non-deterministic), "
                "this tool does not rewrite the notebook."
            ),
            "id_rule": {
                "required_since": "4.5",
                "pattern": "^[a-zA-Z0-9-_]+$",
                "min_length": _CELL_ID_MIN,
                "max_length": _CELL_ID_MAX,
                "canonical_generator_charset": "[a-z0-9-]",
                "source": "hand-embedded from the nbformat v4.5 "
                          "schema definition cell_id",
            },
            "nbformat_minor": minor,
            "ids_required": _is_int(minor) and minor >= 5,
            "cells": rows,
            "summary": {
                "cell_count": len(rows),
                "present": not missing,
                "missing_indexes": missing,
                "unique": not duplicates,
                "duplicates": duplicates,
                "valid": not invalid,
                "invalid_pattern_indexes": invalid,
            },
        }

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_payload(
        mode: str, finding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Structured error payload for summary / check_ids."""
        return {
            "mode": mode,
            "error": {
                "code": finding["code"],
                "message": finding["message"],
                "line": finding["line"],
            },
        }

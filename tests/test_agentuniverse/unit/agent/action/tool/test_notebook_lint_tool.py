#!/usr/bin/env python3
# -*- coding:utf-8 -*-

r"""Offline unit tests for the NotebookLintTool (issue #252, other tools).

Every ground truth in this file was verified empirically before being
recorded here — against CPython 3.11's ``json`` module and against
``nbformat`` 5.11 (installed into the test venv purely as a TEST
oracle; the tool itself stays stdlib-only):

* ``nbformat.validate(nb, version=4)`` raises ``ValidationError``
  for: missing top-level keys, unknown top-level keys
  (``additionalProperties: false``), ``nbformat`` != 4 (schema
  minimum 4, maximum 4), negative ``nbformat_minor`` ("No schema for
  validating v4.-1 notebooks"), ``cells`` not an array, non-object
  cells (its normalizer even raises TypeError on them — the oracle
  harness counts that as rejection), invalid ``cell_type``, missing
  per-type cell fields, ``outputs`` on markdown cells, ids on
  pre-4.5 notebooks, float/bool/negative ``execution_count``,
  malformed output shapes, non-multiline mime values, kernelspec
  without ``display_name``, ``language_info`` without ``name`` and
  ids violating the real v4.5 pattern ``^[a-zA-Z0-9-_]+$`` (1..64);
* the SAME validate **accepts** (verified, then relied on as the
  documented strictness gap): missing cell ids at 4.5 (repaired with
  a ``MissingIDFieldWarning`` — "will become a hard error in future
  nbformat versions"), duplicate cell ids (repaired with a fresh
  RANDOM id via ``DuplicateCellId``), minors above the newest schema
  (falls back to the latest), any ``stream.name`` string,
  unparseable ``application/json`` payloads, non-base64 ``image/*``
  payloads and free-form ``metadata.widgets`` — the tool reports the
  first two as errors under the DISTINCT codes ``cell_id_missing`` /
  ``cell_id_duplicate`` and the rest info/warning-only, and those
  codes never count toward the schema-conformance verdict;
* ``json.JSONDecodeError`` carries ``msg``/``pos``/``lineno``/
  ``colno`` — the syntax-position tests cross-check the tool's
  pos → line converter against the exception's own ``lineno``.

The oracle test generates 300 seeded notebooks (deterministic
``random.Random``): valid ones across the 4.0-4.5 matrix plus
mutated ones (dropped fields, wrong types, bad ids) and requires the
tool's structural verdict to agree with nbformat.validate on schema
strictness.

No network access, no fixtures on disk — everything is inline.
"""

import copy
import json
import os
import random

import pytest
import yaml

from agentuniverse.agent.action.tool.common_tool import NotebookLintTool
from agentuniverse.agent.action.tool.common_tool.notebook_lint_tool import (
    _CELL_ID_MAX,
    _CELL_ID_MIN,
    _CELL_ID_RE,
    _CODE_ONLY_REQUIRED,
    _COMMON_CELL_REQUIRED,
    _OUTPUT_SHAPES,
    _SCHEMA_CODES,
    _TOP_REQUIRED,
    _LineIndex,
    _pos_to_line,
)

TOOL = NotebookLintTool()

FINDING_KEYS = {"line", "code", "message", "severity"}


def lint(text):
    return TOOL.execute(mode="lint", notebook=text)


def summary(text):
    return TOOL.execute(mode="summary", notebook=text)


def check_ids(text):
    return TOOL.execute(mode="check_ids", notebook=text)


def codes(result):
    return [f["code"] for f in result["findings"]]


def make_nb(minor=5, cells=None, metadata=None):
    """A minimal valid notebook for the given minor."""
    nb = {
        "cells": cells if cells is not None else [],
        "metadata": metadata if metadata is not None else {},
        "nbformat": 4,
        "nbformat_minor": minor,
    }
    return nb


def code_cell(**over):
    cell = {
        "cell_type": "code",
        "metadata": {},
        "source": "print(1)",
        "outputs": [],
        "execution_count": 1,
    }
    cell.update(over)
    return cell


# ---------------------------------------------------------------------- #
# registration / shape / input validation
# ---------------------------------------------------------------------- #

def test_registration_and_metadata():
    assert TOOL.name == "notebook_lint_tool"
    assert TOOL.MODES == ("lint", "summary", "check_ids")
    assert "nbformat" in TOOL.description
    # The yaml config exists and matches the module/class pair.
    yaml_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "..", "..",
        "agentuniverse", "agent", "action", "tool", "common_tool",
        "notebook_lint_tool.yaml",
    )
    with open(os.path.abspath(yaml_path), "r", encoding="utf-8") as fh:
        meta = yaml.safe_load(fh)
    assert meta["name"] == "notebook_lint_tool"
    assert meta["metadata"]["class"] == "NotebookLintTool"
    assert meta["metadata"]["module"].endswith("notebook_lint_tool")
    assert set(meta["args_model_schema"]["required"]) == {
        "mode", "notebook"
    }


def test_finding_shape_and_determinism():
    nb = make_nb(cells=[
        code_cell(id="a1"),
        code_cell(id="a1"),  # duplicate id
    ])
    text = json.dumps(nb, indent=1)
    first = lint(text)
    second = lint(text)
    assert first == second
    for finding in first["findings"]:
        assert set(finding) == FINDING_KEYS
        assert finding["line"] >= 1
        assert finding["severity"] in ("error", "warning", "info")
    # sorted by (line, code, message)
    keys = [(f["line"], f["code"], f["message"])
            for f in first["findings"]]
    assert keys == sorted(keys)


def test_mode_validation():
    for bad in (None, "fix", "lint ", 3):
        with pytest.raises(ValueError, match="mode"):
            TOOL.execute(mode=bad, notebook="{}")


def test_notebook_must_be_text():
    for bad in (None, {"cells": []}, 42, ["x"]):
        with pytest.raises(ValueError, match="notebook"):
            TOOL.execute(mode="lint", notebook=bad)


def test_size_cap():
    pad = "x" * 10
    huge = pad + " " * TOOL.max_text
    with pytest.raises(ValueError, match="cap"):
        TOOL.execute(mode="lint", notebook=huge)


def test_read_only_input_unchanged():
    nb = make_nb(cells=[code_cell(id="dup"), code_cell(id="dup")])
    text = json.dumps(nb, indent=2)
    before = text
    lint(text)
    summary(text)
    check_ids(text)
    assert text == before


# ---------------------------------------------------------------------- #
# clean documents
# ---------------------------------------------------------------------- #

def test_clean_document_4_5():
    nb = make_nb(minor=5, cells=[
        code_cell(id="cell-1", source="x = 1\nx",
                  outputs=[{"output_type": "execute_result",
                            "data": {"text/plain": "1"},
                            "metadata": {}, "execution_count": 1}]),
        {"cell_type": "markdown", "metadata": {}, "source": "# hi",
         "id": "cell-2"},
        {"cell_type": "raw", "metadata": {}, "source": "raw text",
         "id": "cell-3"},
    ], metadata={
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    })
    result = lint(json.dumps(nb, indent=1))
    assert result["findings"] == []
    assert result["schema_conformant"] is True
    assert result["schema_error_count"] == 0


def test_clean_document_4_0_through_4_4():
    for minor in range(0, 5):
        nb = make_nb(minor=minor, cells=[code_cell()])
        result = lint(json.dumps(nb))
        assert result["schema_conformant"] is True, minor
        # pre-4.5 notebooks carry no ids — nothing flagged
        assert codes(result) == [], minor


# ---------------------------------------------------------------------- #
# syntax layer
# ---------------------------------------------------------------------- #

def test_empty_document():
    for text in ("", "   \n  ", "\t"):
        result = lint(text)
        assert codes(result) == ["empty_document"]
        assert result["schema_conformant"] is False


def test_syntax_error_message_and_line():
    text = '{\n  "cells": [oops\n'
    result = lint(text)
    assert len(result["findings"]) == 1
    finding = result["findings"][0]
    assert finding["code"] == "json_syntax_error"
    assert "not valid JSON" in finding["message"]


def test_syntax_line_matches_exception_30_docs():
    """The tool's pos→line converter must agree with the exception's
    own lineno over a 30-document malformed corpus."""
    rng = random.Random(20261021)
    mismatches = []
    base = json.dumps(make_nb(minor=5, cells=[code_cell(id="a")]))
    for i in range(30):
        s = list(base)
        pos = rng.randrange(1, len(s))
        s[pos] = "@" if s[pos] != "@" else "#"
        broken = "".join(s)
        try:
            json.loads(broken)
        except json.JSONDecodeError as exc:
            got = _pos_to_line(broken, exc.pos)
            if got != exc.lineno:
                mismatches.append((i, got, exc.lineno))
    assert not mismatches


def test_root_not_object():
    for text in ("[]", '"cells"', "42", "null", "true"):
        result = lint(text)
        assert codes(result) == ["root_not_object"]
        assert result["schema_conformant"] is False


# ---------------------------------------------------------------------- #
# JSON path → line mapper
# ---------------------------------------------------------------------- #

def _mapped_nb_text():
    nb = make_nb(minor=5, cells=[
        code_cell(id="cell-1", execution_count=7,
                  outputs=[{"output_type": "error",
                            "ename": "ValueError", "evalue": "boom",
                            "traceback": ["tb"]}]),
        {"cell_type": "markdown", "metadata": {}, "source": "# t",
         "id": "cell-2"},
    ])
    return json.dumps(nb, indent=2)


def test_line_index_exact_lines():
    text = _mapped_nb_text()
    lines = text.splitlines()
    index = _LineIndex(text)

    def line_of(snippet):
        for k, line in enumerate(lines):
            if snippet in line:
                return k + 1
        raise AssertionError(snippet)

    # top-level value
    assert index.line(("nbformat",)) == line_of('"nbformat"')
    assert index.line(("cells",)) == line_of('"cells"')
    # nested cell values
    assert index.line(
        ("cells", 0, "execution_count")) == line_of('"execution_count"')
    assert index.line(("cells", 0, "id")) == line_of('"cell-1"')
    # deep output path
    assert index.line(
        ("cells", 0, "outputs", 0, "ename")) == line_of('"ValueError"')
    # a missing key falls back to the containing object, else 1
    assert index.line(("cells", 0, "nope"), ("cells", 0)) == \
        line_of('"cell_type"') - 1  # object opens one line before
    assert index.line(("nope", "deep")) == 1


def test_findings_carry_true_lines():
    text = _mapped_nb_text()
    lines = text.splitlines()
    ec_line = next(k + 1 for k, l in enumerate(lines)
                   if '"execution_count": 7' in l)
    ename_line = next(k + 1 for k, l in enumerate(lines)
                      if '"ValueError"' in l)

    broken = json.loads(text)
    broken["cells"][0]["execution_count"] = 1.5
    broken["cells"][0]["outputs"][0]["ename"] = 42
    broken_text = json.dumps(broken, indent=2)
    broken_lines = broken_text.splitlines()
    ec_line = next(k + 1 for k, l in enumerate(broken_lines)
                   if '"execution_count": 1.5' in l)
    ename_line = next(k + 1 for k, l in enumerate(broken_lines)
                      if '"ename": 42' in l)
    result = lint(broken_text)
    by_code = {f["code"]: f["line"] for f in result["findings"]}
    assert by_code["execution_count_invalid"] == ec_line
    assert by_code["output_field_invalid"] == ename_line


# ---------------------------------------------------------------------- #
# hand-embedded nbformat 4.5 spec ground truths
# ---------------------------------------------------------------------- #

def test_spec_top_level_ground_truth():
    """Hand-embedded from nbformat.v4.5.schema.json: required
    [cells, metadata, nbformat, nbformat_minor], additionalProperties
    false, nbformat == 4, nbformat_minor integer >= 0."""
    assert set(_TOP_REQUIRED) == {
        "cells", "metadata", "nbformat", "nbformat_minor"
    }
    for key in _TOP_REQUIRED:
        nb = make_nb()
        del nb[key]
        result = lint(json.dumps(nb))
        assert "required_key_missing" in codes(result), key
        assert result["schema_conformant"] is False
    # unknown top-level key — schema additionalProperties: false
    nb = make_nb()
    nb["unknown_extra"] = 1
    result = lint(json.dumps(nb))
    assert "unexpected_top_level_key" in codes(result)
    assert result["schema_conformant"] is False


def test_spec_cell_id_real_pattern():
    """The REAL v4.5 cell_id definition: ^[a-zA-Z0-9-_]+$, length
    1..64 (not the narrower [a-z0-9-] generator charset)."""
    assert _CELL_ID_MIN == 1 and _CELL_ID_MAX == 64
    for good in ("a", "abc-123", "A_b-C9", "x" * 64, "-"):
        assert _CELL_ID_RE.match(good), good
    for bad in ("", "bad id!", "id/1", "café"):
        assert _CELL_ID_RE.match(bad) is None, bad
    nb = make_nb(minor=5, cells=[code_cell(id="bad id!")])
    result = lint(json.dumps(nb))
    assert "cell_id_invalid" in codes(result)
    assert result["schema_conformant"] is False
    # maxLength 64 is enforced beside the pattern (schema has both)
    nb = make_nb(minor=5, cells=[code_cell(id="x" * 65)])
    result = lint(json.dumps(nb))
    assert "cell_id_invalid" in codes(result)
    assert "65 characters" in result["findings"][0]["message"]


def test_spec_per_type_required_fields():
    assert set(_COMMON_CELL_REQUIRED) == {
        "cell_type", "metadata", "source"
    }
    assert set(_CODE_ONLY_REQUIRED) == {"outputs", "execution_count"}
    for field in _COMMON_CELL_REQUIRED:
        cell = code_cell(id="a1")
        del cell[field]
        nb = make_nb(cells=[cell])
        result = lint(json.dumps(nb))
        assert "required_cell_field_missing" in codes(result), field
    for field in _CODE_ONLY_REQUIRED:
        cell = code_cell(id="a1")
        del cell[field]
        nb = make_nb(cells=[cell])
        result = lint(json.dumps(nb))
        assert "required_cell_field_missing" in codes(result), field


def test_spec_output_shapes():
    """Verified against the schema oneOf (all four branches
    additionalProperties: false) and nbformat.validate."""
    assert set(_OUTPUT_SHAPES) == {
        "stream", "display_data", "execute_result", "error"
    }
    assert _OUTPUT_SHAPES["stream"][0] == ("name", "text")
    assert _OUTPUT_SHAPES["display_data"][0] == ("data", "metadata")
    assert _OUTPUT_SHAPES["execute_result"][0] == (
        "data", "metadata", "execution_count")
    assert _OUTPUT_SHAPES["error"][0] == (
        "ename", "evalue", "traceback")


def test_spec_version_matrix_ids():
    """Ids: required since 4.5 — and REJECTED before it (pre-4.5
    schemas have no id property; verified 'Additional properties
    are not allowed (id)')."""
    for minor in range(0, 5):
        nb = make_nb(minor=minor, cells=[code_cell(id="a1")])
        result = lint(json.dumps(nb))
        assert "unexpected_cell_field" in codes(result), minor
        assert result["schema_conformant"] is False, minor
    # 4.5 without id: schema-validated as OK by nbformat (auto
    # repair) — the tool flags it under a DISTINCT stricter code.
    nb = make_nb(minor=5, cells=[code_cell()])
    result = lint(json.dumps(nb))
    assert codes(result) == ["cell_id_missing"]
    assert result["schema_conformant"] is True
    assert "cell_id_missing" not in _SCHEMA_CODES


def test_spec_minor_version_bounds():
    nb = make_nb(minor=-1)
    assert "nbformat_minor_invalid" in codes(lint(json.dumps(nb)))
    nb = make_nb(minor="4")
    assert "nbformat_minor_invalid" in codes(lint(json.dumps(nb)))
    nb = make_nb(minor=1.5)
    assert "nbformat_minor_invalid" in codes(lint(json.dumps(nb)))
    # unknown-but-valid minors: info only (validate falls back)
    nb = make_nb(minor=9, cells=[code_cell(id="a1")])
    result = lint(json.dumps(nb))
    assert codes(result) == ["nbformat_minor_unknown"]
    assert result["schema_conformant"] is True
    nb["nbformat"] = 5
    assert "nbformat_major_invalid" in codes(lint(json.dumps(nb)))


def test_spec_execution_count_ground_truth():
    for bad in (1.5, -1, True, "3", [], {}):
        nb = make_nb(cells=[code_cell(id="a1", execution_count=bad)])
        result = lint(json.dumps(nb))
        assert "execution_count_invalid" in codes(result), bad
        assert result["schema_conformant"] is False, bad
    for good in (0, 1, 999, None):
        nb = make_nb(minor=5, cells=[code_cell(id="a1",
                                               execution_count=good)])
        assert lint(json.dumps(nb))["schema_conformant"] is True, good


def test_spec_markdown_raw_exclusive_fields():
    md = {"cell_type": "markdown", "metadata": {}, "source": "# t",
          "outputs": []}
    nb = make_nb(minor=5, cells=[dict(md, id="m1")])
    result = lint(json.dumps(nb))
    assert "unexpected_cell_field" in codes(result)
    assert result["schema_conformant"] is False

    raw = {"cell_type": "raw", "metadata": {}, "source": "r",
           "execution_count": None, "id": "r1"}
    nb = make_nb(minor=5, cells=[raw])
    result = lint(json.dumps(nb))
    assert "unexpected_cell_field" in codes(result)

    code = code_cell(id="c1",
                     attachments={"img.png": {"image/png": "aGk="}})
    nb = make_nb(minor=5, cells=[code])
    result = lint(json.dumps(nb))
    assert "unexpected_cell_field" in codes(result)


def test_spec_output_type_rules():
    base = code_cell(id="c1")
    # missing output_type
    nb = make_nb(minor=5, cells=[dict(base, outputs=[{}])])
    assert "output_type_missing" in codes(lint(json.dumps(nb)))
    # unknown type
    nb = make_nb(minor=5, cells=[
        dict(base, outputs=[{"output_type": "weird"}])])
    result = lint(json.dumps(nb))
    assert "output_type_unknown" in codes(result)
    assert result["schema_conformant"] is False
    # per-type missing fields
    for otype, field in (("error", "traceback"),
                         ("stream", "name"),
                         ("display_data", "metadata"),
                         ("execute_result", "execution_count")):
        out = {"output_type": otype, "ename": "E", "evalue": "v",
               "traceback": [], "name": "stdout", "text": "t",
               "data": {"text/plain": "x"}, "metadata": {},
               "execution_count": 1}
        del out[field]
        nb = make_nb(minor=5, cells=[dict(base, outputs=[out])])
        assert "output_field_missing" in codes(
            lint(json.dumps(nb))), (otype, field)
    # wrong types inside outputs
    nb = make_nb(minor=5, cells=[dict(base, outputs=[
        {"output_type": "error", "ename": "E", "evalue": "v",
         "traceback": "not-a-list"}])])
    result = lint(json.dumps(nb))
    assert "output_field_invalid" in codes(result)
    assert result["schema_conformant"] is False
    # extra field on an output (additionalProperties: false)
    nb = make_nb(minor=5, cells=[dict(base, outputs=[
        {"output_type": "stream", "name": "stdout", "text": "t",
         "extra": 1}])])
    assert "unexpected_output_field" in codes(lint(json.dumps(nb)))
    # non-object / non-array outputs
    nb = make_nb(minor=5, cells=[dict(base, outputs="nope")])
    assert "outputs_not_array" in codes(lint(json.dumps(nb)))
    nb = make_nb(minor=5, cells=[dict(base, outputs=["nope"])])
    assert "output_not_object" in codes(lint(json.dumps(nb)))


def test_spec_metadata_ground_truth():
    nb = make_nb(minor=5, metadata={"kernelspec": {"name": "k"}})
    result = lint(json.dumps(nb))
    assert "kernelspec_invalid" in codes(result)
    assert result["schema_conformant"] is False

    nb = make_nb(minor=5, metadata={"language_info": {"pygments_lexer": "x"}})
    assert "language_info_invalid" in codes(lint(json.dumps(nb)))

    nb = make_nb(minor=5, metadata={"orig_nbformat": 0})
    assert "orig_nbformat_invalid" in codes(lint(json.dumps(nb)))

    nb = make_nb(minor=5, metadata=[1, 2])
    assert "metadata_invalid" in codes(lint(json.dumps(nb)))


def test_stricter_codes_excluded_from_schema_verdict():
    """The documented stricter-than-validate checks must never count
    toward schema conformance (nbformat auto-repairs these)."""
    for code in ("cell_id_missing", "cell_id_duplicate",
                 "execution_count_regression", "source_form_inconsistent",
                 "source_trailing_newline", "json_mime_unparseable",
                 "image_mime_not_base64", "stream_name_unusual",
                 "widget_metadata_quirk", "nbformat_minor_unknown",
                 "cell_id_style", "empty_cells_list"):
        assert code not in _SCHEMA_CODES, code


# ---------------------------------------------------------------------- #
# stricter / extra checks
# ---------------------------------------------------------------------- #

def test_duplicate_ids_reported_with_index():
    nb = make_nb(minor=5, cells=[
        code_cell(id="same"), code_cell(id="same", execution_count=2)])
    result = lint(json.dumps(nb, indent=1))
    dup = [f for f in result["findings"]
           if f["code"] == "cell_id_duplicate"]
    assert len(dup) == 1
    assert "cells[1]" in dup[0]["message"]
    assert "cells[0]" in dup[0]["message"]
    assert result["schema_conformant"] is True


def test_execution_count_regression():
    nb = make_nb(minor=5, cells=[
        code_cell(id="a", execution_count=5),
        code_cell(id="b", execution_count=3),
        code_cell(id="c", execution_count=None),
        code_cell(id="d", execution_count=6),
    ])
    result = lint(json.dumps(nb))
    reg = [f for f in result["findings"]
           if f["code"] == "execution_count_regression"]
    assert len(reg) == 1
    assert "cells[1]" in reg[0]["message"]
    assert result["schema_conformant"] is True


def test_source_form_and_trailing_newline():
    nb = make_nb(minor=5, cells=[
        code_cell(id="a", source="print(1)"),
        code_cell(id="b", source=["x = 1", "x"]),
    ])
    result = lint(json.dumps(nb))
    got = codes(result)
    assert "source_form_inconsistent" in got
    assert "source_trailing_newline" in got
    assert result["schema_conformant"] is True


def test_mime_value_extras():
    out = {"output_type": "execute_result",
           "data": {"application/json": "{bad", "image/png": "not b64!",
                    "text/plain": ["ok"]},
           "metadata": {}, "execution_count": 1}
    nb = make_nb(minor=5, cells=[code_cell(id="a", outputs=[out])])
    result = lint(json.dumps(nb))
    got = codes(result)
    assert "json_mime_unparseable" in got
    assert "image_mime_not_base64" in got
    assert result["schema_conformant"] is True  # schema accepts both
    # base64 payload with whitespace is fine
    out["data"]["image/png"] = "aGVs\nbG8="
    nb = make_nb(minor=5, cells=[code_cell(id="a", outputs=[out])])
    got = codes(lint(json.dumps(nb)))
    assert "image_mime_not_base64" not in got


def test_mime_value_schema_level():
    out = {"output_type": "execute_result",
           "data": {"text/plain": 42}, "metadata": {}, "execution_count": 1}
    nb = make_nb(minor=5, cells=[code_cell(id="a", outputs=[out])])
    result = lint(json.dumps(nb))
    assert "mime_value_invalid" in codes(result)
    assert result["schema_conformant"] is False


def test_attachments():
    good = {"cell_type": "markdown", "metadata": {}, "source": "# t",
            "id": "m1", "attachments": {"img.png": {"image/png": "aGk="}}}
    nb = make_nb(minor=5, cells=[good])
    assert lint(json.dumps(nb))["schema_conformant"] is True
    bad = dict(good, attachments={"img.png": "not-a-bundle"})
    nb = make_nb(minor=5, cells=[bad])
    assert "attachment_value_invalid" in codes(lint(json.dumps(nb)))
    bad = dict(good, attachments="nope")
    nb = make_nb(minor=5, cells=[bad])
    assert "attachments_invalid" in codes(lint(json.dumps(nb)))


def test_spec_cell_metadata_fields():
    """Typed cell-metadata fields, hand-embedded from the per-minor
    schema matrix ({code,markdown,raw}_cell -> properties.metadata;
    verified against nbformat.validate): name non-empty string, tags
    unique comma-free strings, collapsed boolean, scrolled enum
    true/false/"auto" (code cells), format string (raw cells),
    jupyter object (4.3+), execution object of string values (4.4+,
    code cells). A field not defined for the (cell type, minor) sits
    under additionalProperties: true and must NOT be judged."""
    def meta_cell(md, minor=5, ctype="code"):
        cell = {"cell_type": ctype, "metadata": md, "source": "x"}
        if ctype == "code":
            cell.update(outputs=[], execution_count=1)
        if minor >= 5:
            cell["id"] = "a1"
        return make_nb(minor=minor, cells=[cell])

    rejects = [
        {"tags": "x"},                       # not an array
        {"tags": ["a,b"]},                   # comma inside a tag
        {"tags": ["a", "a"]},                # uniqueItems
        {"tags": [1]},                       # item not a string
        {"name": 7}, {"name": ""},           # pattern ^.+$
        {"collapsed": "yes"}, {"collapsed": 1},   # bool identity
        {"scrolled": "nope"}, {"scrolled": 1},    # enum, 1 != True
        {"execution": "fast"},
        {"execution": {"shell.execute_reply": 5}},
        {"jupyter": 3},
    ]
    for md in rejects:
        result = lint(json.dumps(meta_cell(md)))
        assert "cell_metadata_invalid" in codes(result), md
        assert result["schema_conformant"] is False, md

    accepts = [
        {"tags": []}, {"tags": ["a", "b", "gämma"]},
        {"name": " "}, {"name": "cell name"},
        {"collapsed": True}, {"collapsed": False},
        {"scrolled": True}, {"scrolled": False}, {"scrolled": "auto"},
        {"jupyter": {"source_hidden": "yes"}},  # schema quirk: nested
        {"execution": {"iopub.status.busy": "2026-01-01T00:00:00Z"}},
    ]
    for md in accepts:
        result = lint(json.dumps(meta_cell(md)))
        assert result["schema_conformant"] is True, md

    # fields on the WRONG cell type ride on additionalProperties —
    # code-only fields on a markdown cell are schema-legal extras.
    wrong_type = {"collapsed": "yes", "format": 5, "execution": "fast"}
    nb = make_nb(minor=5, cells=[
        {"cell_type": "markdown", "metadata": wrong_type,
         "source": "x", "id": "m1"}])
    assert lint(json.dumps(nb))["schema_conformant"] is True

    # per-minor gates: jupyter typed from 4.3, execution from 4.4.
    for minor, md, want in ((2, {"jupyter": 5}, "accept"),
                            (3, {"jupyter": 5}, "reject"),
                            (3, {"execution": "fast"}, "accept"),
                            (4, {"execution": "fast"}, "reject")):
        result = lint(json.dumps(meta_cell(md, minor=minor)))
        got = "reject" if result["schema_conformant"] is False \
            else "accept"
        assert got == want, (minor, md)

    # format belongs to raw cells only — on raw it is enforced.
    nb = make_nb(minor=5, cells=[
        {"cell_type": "raw", "metadata": {"format": 5},
         "source": "x", "id": "r1"}])
    assert "cell_metadata_invalid" in codes(lint(json.dumps(nb)))
    nb = make_nb(minor=5, cells=[
        {"cell_type": "raw", "metadata": {"format": "text/plain"},
         "source": "x", "id": "r1"}])
    assert lint(json.dumps(nb))["schema_conformant"] is True


def test_spec_notebook_metadata_fields():
    """Notebook-level typed fields: language_info sub-fields in every
    minor; title (string) / authors (array) only since 4.2 — the same
    wrong value is schema-legal before 4.2 (verified against
    nbformat.validate); authors ELEMENTS are unconstrained (the
    official schema says "item", not "items")."""
    good_cells = [code_cell(id="a1")]
    rejects = [
        {"language_info": {"name": "py", "codemirror_mode": 5}},
        {"language_info": {"name": "py", "file_extension": 7}},
        {"language_info": {"name": "py", "mimetype": []}},
        {"language_info": {"name": "py", "pygments_lexer": True}},
        {"title": 5},
        {"authors": "x"},
    ]
    for meta in rejects:
        nb = make_nb(minor=5, cells=good_cells, metadata=meta)
        result = lint(json.dumps(nb))
        assert result["schema_conformant"] is False, meta
        assert codes(result) == [
            "language_info_invalid" if "language_info" in meta
            else "metadata_invalid"], meta
    accepts = [
        {"language_info": {"name": "py",
                           "codemirror_mode": {"mode": "python"}}},
        {"language_info": {"name": "py", "pygments_lexer": "ipython3"}},
        {"authors": [1, 2]},      # item typo: elements unconstrained
        {"title": "My notebook"},
    ]
    for meta in accepts:
        nb = make_nb(minor=5, cells=good_cells, metadata=meta)
        assert lint(json.dumps(nb))["schema_conformant"] is True, meta
    # the pre-4.2 trap: title/authors untyped before 4.2
    old = make_nb(minor=1, cells=[code_cell()], metadata={"title": 5,
                                                          "authors": "x"})
    assert lint(json.dumps(old))["schema_conformant"] is True
    # 4.2 is exactly where they become typed
    edge = make_nb(minor=2, cells=[code_cell()], metadata={"title": 5})
    assert lint(json.dumps(edge))["schema_conformant"] is False


def test_source_mixed_list_reports_item():
    """A mixed source list must point at the exact offending item
    (source_item_not_string), not collapse into the coarse
    source_invalid_type at the source key line."""
    nb = make_nb(minor=5, cells=[code_cell(
        id="a1", source=["first\n", 2, "third\n"])])
    text = json.dumps(nb, indent=2)
    result = lint(text)
    got = codes(result)
    assert "source_item_not_string" in got
    assert "source_invalid_type" not in got
    assert result["schema_conformant"] is False
    finding = next(f for f in result["findings"]
                   if f["code"] == "source_item_not_string")
    item_line = next(k + 1 for k, l in enumerate(text.splitlines())
                     if l.strip() == "2,")
    assert finding["line"] == item_line


def test_widget_metadata_info_only():
    nb = make_nb(minor=5, metadata={"widgets": {"state": {"x": "y"}}},
                 cells=[code_cell(id="a")])
    result = lint(json.dumps(nb))
    assert "widget_metadata_quirk" in codes(result)
    assert result["schema_conformant"] is True


# ---------------------------------------------------------------------- #
# summary mode
# ---------------------------------------------------------------------- #

def test_summary_hand_verified():
    nb = make_nb(minor=5, cells=[
        code_cell(id="a", execution_count=1),
        code_cell(id="b", execution_count=None),
        code_cell(id="c", execution_count=5,
                  outputs=[
                      {"output_type": "error", "ename": "E",
                       "evalue": "v", "traceback": ["t"]},
                      {"output_type": "stream", "name": "stdout",
                       "text": "hi"},
                      {"output_type": "display_data",
                       "data": {"text/html": "<b/>",
                                "image/png": "aGk="},
                       "metadata": {}}]),
        {"cell_type": "markdown", "metadata": {}, "source": "# t",
         "id": "m"},
    ])
    s = summary(json.dumps(nb))
    assert s["cell_count"] == {"total": 4, "code": 3, "markdown": 1,
                               "raw": 0, "unknown": 0, "non_object": 0}
    assert s["code_cells"] == 3
    assert s["executed"] == 2
    assert s["unexecuted"] == 1
    assert s["error_outputs"] == 1
    assert s["total_outputs"] == 3
    assert s["max_execution_count"] == 5
    assert s["execution_regressions"] == []
    assert s["mime_types"] == ["image/png", "text/html"]
    assert s["ids"] == {
        "present": True, "unique": True, "valid": True,
        "required": True, "present_count": 4, "duplicates": [],
        "invalid_indexes": [],
    }


def test_summary_regression_flagged():
    nb = make_nb(minor=5, cells=[
        code_cell(id="a", execution_count=4),
        code_cell(id="b", execution_count=2),
    ])
    s = summary(json.dumps(nb))
    assert s["execution_regressions"] == [
        {"cell_index": 1, "execution_count": 2, "previous_max": 4}
    ]
    assert s["max_execution_count"] == 4


def test_summary_broken_documents():
    assert "error" in summary("{bad")
    assert "error" in summary("")
    nb = make_nb()
    nb["cells"] = {}
    assert summary(json.dumps(nb))["error"]["code"] == "cells_not_array"


# ---------------------------------------------------------------------- #
# check_ids mode
# ---------------------------------------------------------------------- #

def test_check_ids_report_and_read_only():
    nb = make_nb(minor=5, cells=[
        code_cell(id="good-1"),
        code_cell(id="bad id!"),
        code_cell(),                       # missing id
        code_cell(id="good-1"),            # duplicate
    ])
    text = json.dumps(nb, indent=1)
    result = check_ids(text)
    assert result["read_only"] is True
    assert result["mutated"] is False
    assert "never" in result["note"] and "normalize" in result["note"]
    assert result["ids_required"] is True
    rule = result["id_rule"]
    assert rule["pattern"] == "^[a-zA-Z0-9-_]+$"
    assert rule["required_since"] == "4.5"
    s = result["summary"]
    assert s["cell_count"] == 4
    assert s["missing_indexes"] == [2]
    assert s["invalid_pattern_indexes"] == [1]
    assert s["duplicates"] == [
        {"id": "good-1", "cell_indexes": [0, 3]}
    ]
    assert s["present"] is False
    assert s["unique"] is False
    assert s["valid"] is False
    row1 = result["cells"][1]
    assert row1["pattern_valid"] is False
    row3 = result["cells"][3]
    assert row3["duplicate"] is True and row3["duplicates_with"] == [0]
    assert text == json.dumps(nb, indent=1)  # untouched


def test_check_ids_pre_4_5():
    nb = make_nb(minor=4, cells=[code_cell()])
    result = check_ids(json.dumps(nb))
    assert result["ids_required"] is False
    assert result["summary"]["present"] is False  # no ids — by design


def test_check_ids_broken_documents():
    assert "error" in check_ids("{bad")
    assert "error" in check_ids("")


# ---------------------------------------------------------------------- #
# THE nbformat ORACLE — 300 seeded notebooks
# ---------------------------------------------------------------------- #

_ORACLE_TOTAL = 300


def _oracle_validate(nb):
    """nbformat.validate(nb, version=4) verdict: rejects (any of
    ValidationError, or the TypeError/KeyError its normalizer raises
    on non-object cells / missing cells — counted as rejection) or
    accepts. Works on a deep copy because validate MUTATES the
    notebook (auto-normalization)."""
    nbformat = pytest.importorskip(
        "nbformat", reason="nbformat is the TEST-only oracle"
    )
    import warnings
    from jsonschema import ValidationError
    probe = copy.deepcopy(nb)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            nbformat.validate(probe, version=4)
            return True
        except ValidationError:
            return False
        except Exception:  # TypeError/KeyError from the normalizer
            return False


def _rand_source(rng):
    if rng.random() < 0.5:
        return "\n".join(rng.choice(
            ["print(1)", "x = 2", "# comment", "df.head()"])
            for _ in range(rng.randrange(1, 4)))
    return [line + "\n" for line in
            ["alpha = 1", "beta = alpha + 1"][:rng.randrange(1, 3)]]


def _rand_id(rng):
    return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789-")
                   for _ in range(rng.randrange(1, 12)))


def _rand_output(rng):
    kind = rng.choice(["stream", "display_data", "execute_result",
                       "error"])
    if kind == "stream":
        return {"output_type": "stream",
                "name": rng.choice(["stdout", "stderr"]),
                "text": rng.choice(["hi", ["h", "i"]])}
    if kind == "display_data":
        return {"output_type": "display_data",
                "data": rng.choice([
                    {"text/plain": "1"},
                    {"text/html": "<b>x</b>", "text/plain": ["x"]},
                    {"image/png": "aGVsbG8="},
                    {"application/json": {"k": [1, 2]}},
                ]),
                "metadata": {}}
    if kind == "execute_result":
        return {"output_type": "execute_result",
                "data": {"text/plain": "42"},
                "metadata": {},
                "execution_count": rng.randrange(0, 30)}
    return {"output_type": "error", "ename": "ValueError",
            "evalue": "boom", "traceback": ["line"]}


def _rand_cell(rng, minor, index):
    ctype = rng.choice(["code", "code", "markdown", "raw"])
    cell = {"cell_type": ctype, "metadata": {}, "source": _rand_source(rng)}
    if minor == 5:
        cell["id"] = _rand_id(rng) + f"-{index}"
    if ctype == "code":
        cell["outputs"] = [
            _rand_output(rng)
            for _ in range(rng.randrange(0, 3))
        ]
        cell["execution_count"] = rng.choice(
            [None, rng.randrange(0, 30)])
    elif rng.random() < 0.2:
        cell["attachments"] = {"img.png": {"image/png": "aGVsbG8="}}
    return cell


def _rand_notebook(rng):
    minor = rng.choice([5, 5, 5, 4, 3, 2, 1, 0])
    nb = {
        "cells": [_rand_cell(rng, minor, i)
                  for i in range(rng.randrange(1, 6))],
        "metadata": rng.choice([
            {},
            {"kernelspec": {"name": "python3",
                            "display_name": "Python 3"}},
            {"kernelspec": {"name": "python3",
                            "display_name": "Python 3"},
             "language_info": {"name": "python"}},
        ]),
        "nbformat": 4,
        "nbformat_minor": minor,
    }
    return nb


def _mutate(nb, rng):
    """One documented mutation: dropped fields, wrong types, bad
    ids. Returns a label for adjudication."""
    choice = rng.choice(
        ["drop_top", "drop_cell", "drop_output", "drop_meta",
         "wrong_type", "bad_id", "duplicate_id"])
    if choice == "drop_top" and nb:
        key = rng.choice(list(nb))
        del nb[key]
        return f"drop_top:{key}"
    if choice == "drop_meta" and isinstance(nb.get("metadata"), dict):
        meta = nb["metadata"]
        if not meta:
            return _mutate(nb, rng)
        key = rng.choice(list(meta))
        if isinstance(meta[key], dict) and meta[key]:
            sub = rng.choice(list(meta[key]))
            del meta[key][sub]
            return f"drop_meta:{key}.{sub}"
        del meta[key]
        return f"drop_meta:{key}"
    cells = nb.get("cells")
    if not isinstance(cells, list) or not cells:
        return _mutate(nb, rng)
    i = rng.randrange(len(cells))
    if choice == "drop_cell":
        cell = cells[i]
        if not isinstance(cell, dict) or not cell:
            return _mutate(nb, rng)
        key = rng.choice(list(cell))
        del cell[key]
        return f"drop_cell[{i}]:{key}"
    if choice == "drop_output":
        cell = cells[i]
        outputs = cell.get("outputs") if isinstance(cell, dict) else None
        if not isinstance(outputs, list) or not outputs \
                or not isinstance(outputs[0], dict):
            return _mutate(nb, rng)
        out = rng.choice(outputs)
        key = rng.choice(list(out))
        del out[key]
        return f"drop_output[{i}]:{key}"
    if choice == "wrong_type":
        where = rng.choice(["execution_count", "source", "cells",
                            "cell", "nbformat", "minor", "output"])
        bad = rng.choice([1.5, -1, True, "3", [], {}, "x"])
        if where == "execution_count" and isinstance(cells[i], dict):
            cells[i]["execution_count"] = bad
        elif where == "source" and isinstance(cells[i], dict):
            cells[i]["source"] = bad
        elif where == "cells":
            nb["cells"] = bad
        elif where == "cell":
            cells[i] = bad
        elif where == "nbformat":
            nb["nbformat"] = bad
        elif where == "minor":
            nb["nbformat_minor"] = bad
        elif isinstance(cells[i], dict):
            outputs = cells[i].get("outputs")
            if isinstance(outputs, list) and outputs:
                outputs[rng.randrange(len(outputs))] = bad
            else:
                cells[i]["outputs"] = bad
        return f"wrong_type:{where}:{bad!r}"
    # bad_id / duplicate_id
    cell = cells[i]
    if not isinstance(cell, dict):
        return _mutate(nb, rng)
    if choice == "bad_id":
        cell["id"] = rng.choice(["bad id!", "", "x" * 65, "ok-id"])
        return f"bad_id[{i}]"
    cell["id"] = cells[0].get("id") if isinstance(cells[0], dict) else "x"
    if cell["id"] is None:
        cell["id"] = "dup-id"
    return f"duplicate_id[{i}]"


def test_nbformat_oracle_agreement_300_seeded_notebooks():
    """The structural verdict must agree with nbformat.validate on
    schema strictness over 300 seeded notebooks (valid + mutated).

    Adjudication rules (documented in the tool):
    * tool verdict = any finding whose code is in _SCHEMA_CODES;
      the stricter extras (cell_id_missing / cell_id_duplicate /
      style / regression / mime-value checks ...) never count;
    * oracle verdict = validate raises or not (its normalizer's
      TypeError/KeyError crashes count as rejection);
    * unparseable JSON cannot reach validate — the tool's
      json_syntax_error finding defines that class alone.
    """
    rng = random.Random(252)
    generated = 0
    valid_count = mutated_count = 0
    for seed in range(_ORACLE_TOTAL):
        local = random.Random(252_000 + seed)
        nb = _rand_notebook(local)
        label = "valid"
        if seed % 3 != 0:  # 2/3 mutated, 1/3 clean
            label = _mutate(nb, local)
            mutated_count += 1
        else:
            valid_count += 1
        text = json.dumps(nb, indent=1)

        try:
            parsed = json.loads(text)
        except ValueError:
            # only the tool sees this class; oracle cannot parse
            result = lint(text)
            assert codes(result) == ["json_syntax_error"]
            continue
        generated += 1

        oracle_accepts = _oracle_validate(parsed)
        result = lint(text)
        tool_conformant = result["schema_conformant"]

        if tool_conformant != oracle_accepts:
            schema_findings = [f["code"] for f in result["findings"]
                               if f["code"] in _SCHEMA_CODES]
            pytest.fail(
                f"seed {seed} ({label}): tool={tool_conformant} "
                f"oracle={oracle_accepts} "
                f"schema_findings={schema_findings} "
                f"all={[f['code'] for f in result['findings']]} "
                f"nb={text[:400]}"
            )
        if not oracle_accepts:
            assert result["schema_error_count"] >= 1, seed

    assert generated >= 250  # the corpus really reached the oracle
    assert mutated_count >= 150 and valid_count >= 90


def test_oracle_strictness_gap_is_only_ids():
    """Where the tool is deliberately stricter than validate (ids),
    nbformat must still ACCEPT (auto-repair) — the documented gap."""
    nb = make_nb(minor=5, cells=[code_cell()])
    assert _oracle_validate(nb) is True
    assert codes(lint(json.dumps(nb))) == ["cell_id_missing"]

    nb = make_nb(minor=5, cells=[code_cell(id="d"), code_cell(id="d")])
    assert _oracle_validate(nb) is True
    assert "cell_id_duplicate" in codes(lint(json.dumps(nb)))


# ---------------------------------------------------------------------- #
# self-review oracle: 200 FRESH seeds over the metadata-field layer
# (found missing by a hostile re-probe; seeds deliberately disjoint
# from the 252/252_000 corpus above)
# ---------------------------------------------------------------------- #

_META_FIELDS = ("name", "tags", "collapsed", "scrolled", "jupyter",
                "execution", "format")


def _meta_field_value(rng):
    """A typed-field value: usually schema-VALID, sometimes a wrong
    type/pattern/enemy (the class the re-probe caught), plus
    bool-identity traps where Python 1 == True must NOT pass."""
    return rng.choice([
        # valid
        "cell name", " ", ["a", "b-2"], [], True, False, "auto",
        {"source_hidden": True}, {"iopub.status.busy": "t"},
        # hostile
        "", 7, ["a,b"], ["a", "a"], [1], "yes", "nope",
        {"zzz": 5}, "fast", {"k": {"deep": 1}}, 3,
    ])


def test_nbformat_oracle_metadata_layer_200_fresh_seeds():
    """Second differential corpus, hostile to the typed metadata
    layer: verdicts must agree with nbformat.validate exactly.

    (Found and fixed by the hostile re-probe: the first version of
    this tool validated NO cell-metadata field — 38 of 200 fresh
    seeds disagreed with validate; this test pins the fixed layer.)"""
    total = 200
    valid_count = 0
    for seed in range(total):
        rng = random.Random(515_000 + seed * 3)
        minor = rng.choice([5, 5, 4, 3, 2, 1, 0, 6])
        cells = []
        for i in range(rng.randrange(1, 4)):
            ctype = rng.choice(["code", "markdown", "raw"])
            md = {}
            for field in rng.sample(
                    _META_FIELDS, rng.randrange(0, len(_META_FIELDS))):
                md[field] = _meta_field_value(rng)
            cell = {"cell_type": ctype, "metadata": md,
                    "source": rng.choice(["x", ["a\n", "b"]])}
            if minor >= 5:
                cell["id"] = f"c{i}"
            if ctype == "code":
                cell["outputs"] = []
                cell["execution_count"] = 1
            cells.append(cell)
        meta = rng.choice([
            {},
            {"kernelspec": {"name": "python3",
                            "display_name": "Python 3"}},
            {"language_info": {
                "name": "python",
                rng.choice(["codemirror_mode", "file_extension",
                            "mimetype", "pygments_lexer"]):
                    _meta_field_value(rng)}},
            {"title": rng.choice(["t", 5, []])},
            {"authors": rng.choice([[{"name": "a"}], [1, 2], "x"])},
        ])
        nb = {"cells": cells, "metadata": meta, "nbformat": 4,
              "nbformat_minor": minor}
        text = json.dumps(nb, indent=rng.randrange(0, 3))

        oracle_ok = _oracle_validate(json.loads(text))
        tool_ok = lint(text)["schema_conformant"]
        if oracle_ok:
            valid_count += 1
        assert tool_ok == oracle_ok, (
            f"seed {seed}: tool={tool_ok} oracle={oracle_ok} "
            f"minor={minor} meta={meta} cells={json.dumps(cells)} "
            f"findings={codes(lint(text))}"
        )
    assert valid_count >= 15  # the corpus contains real clean docs

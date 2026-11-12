#!/usr/bin/env python3
# -*- coding:utf-8 -*-

r"""Offline unit tests for the JsonLintTool (issue #252, other tools).

Every ground truth in this file was verified empirically against the
interpreter actually running the tests (CPython 3.11) before being
recorded here:

* ``json.JSONDecodeError`` carries ``msg``/``doc``/``pos``/``lineno``
  /``colno`` — the position tests cross-check the tool's own
  pos → line/col converter against the exception's attributes over a
  30-document malformed corpus;
* ``json.loads`` **silently keeps the last value** of duplicate keys;
* ``json.loads`` **accepts** the non-standard ``NaN`` / ``Infinity`` /
  ``-Infinity`` literals by default, while ``json.dumps(...,
  allow_nan=False)`` refuses them (the strictness note the tool
  quotes);
* ``json.loads`` **rejects** raw control characters inside strings
  (strict default) but accepts their ``\uXXXX`` escapes;
* ``json.loads`` rejects a leading UTF-8 BOM with "Unexpected UTF-8
  BOM";
* json5-style trailing commas are rejected with "Expecting value" /
  "Expecting property name..." at the closing bracket — which is how
  the tool classifies them.

No network access, no fixtures on disk — everything is inline.
"""

import json
import math
import os
import sys
import time

import pytest
import yaml

from agentuniverse.agent.action.tool.common_tool import JsonLintTool
from agentuniverse.agent.action.tool.common_tool.json_lint_tool import (
    _pos_to_line_col,
)

TOOL = JsonLintTool()

FINDING_KEYS = {"code", "severity", "line", "col", "message"}


def lint(text):
    return TOOL.execute(mode="lint", document=text)


def profile(text):
    return TOOL.execute(mode="profile", document=text)


def fix_hints(text):
    return TOOL.execute(mode="fix_hints", document=text)


def codes(result):
    return [f["code"] for f in result["findings"]]


# ------------------------------------------------------------------ #
# Registration and shape
# ------------------------------------------------------------------ #

def test_registration_and_metadata():
    assert JsonLintTool is not None
    assert TOOL.name == "json_lint_tool"
    assert TOOL.MODES == ("lint", "profile", "fix_hints")
    assert "JSON" in TOOL.description
    # The yaml config exists and matches the module/class pair.
    yaml_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "..", "..",
        "agentuniverse", "agent", "action", "tool", "common_tool",
        "json_lint_tool.yaml",
    )
    with open(os.path.abspath(yaml_path), "r", encoding="utf-8") as fh:
        meta = yaml.safe_load(fh)
    assert meta["name"] == "json_lint_tool"
    assert meta["metadata"]["class"] == "JsonLintTool"
    assert meta["metadata"]["module"].endswith("json_lint_tool")
    assert set(meta["args_model_schema"]["properties"]["mode"]["enum"]) \
        == {"lint", "profile", "fix_hints"}


def test_finding_shape_and_determinism():
    doc = '{"a": 1, "a": 2, "b": NaN}\n'
    r1 = lint(doc)
    r2 = lint(doc)
    assert r1 == r2  # deterministic: pure function of the input
    for f in r1["findings"]:
        assert set(f.keys()) == FINDING_KEYS
        assert f["severity"] in ("error", "warning", "info")
        assert isinstance(f["line"], int) and f["line"] >= 1
        assert isinstance(f["col"], int) and f["col"] >= 1


# ------------------------------------------------------------------ #
# Strict parameter validation (ValueError matrix)
# ------------------------------------------------------------------ #

def test_mode_validation():
    for bad in (None, "", "linting", "LINT", 1, ["lint"]):
        with pytest.raises(ValueError, match="mode must be one of"):
            TOOL.execute(mode=bad, document="{}")


def test_document_must_be_text():
    # Parsed values cannot be linted: duplicate keys and formatting
    # are lost on parse — the error says exactly that.
    for bad in (None, {"a": 1}, [1, 2], 42, 1.5, True):
        with pytest.raises(ValueError, match="must be the JSON text"):
            TOOL.execute(mode="lint", document=bad)


def test_size_cap():
    with pytest.raises(ValueError, match="exceeds the .*-character cap"):
        lint("[" + ",".join(["1"] * 500_001) + "]")  # > 1,000,000 chars
    # Exactly at the cap is accepted (1,000,000 characters of a
    # string document).
    doc = '"' + "x" * 999_998 + '"'
    assert len(doc) == 1_000_000
    assert lint(doc)["valid_json"] is True


# ------------------------------------------------------------------ #
# Clean documents and the summary block
# ------------------------------------------------------------------ #

def test_clean_document():
    result = lint('{"name": "au", "version": 1}')
    assert result["findings"] == []
    assert result["valid_json"] is True
    assert result["summary"]["findings"] == 0
    assert result["summary"]["severity_counts"] == {
        "error": 0, "warning": 0, "info": 0}
    assert result["summary"]["rule_counts"] == {}
    assert result["summary"]["chars"] == len('{"name": "au", "version": 1}')


def test_summary_matches_findings():
    doc = '{"a": 1, "a": 2, "b": 1.0, "c": NaN}'
    result = lint(doc)
    counts = result["summary"]["rule_counts"]
    assert sum(result["summary"]["severity_counts"].values()) \
        == result["summary"]["findings"] == len(result["findings"])
    assert sum(counts.values()) == len(result["findings"])
    assert result["valid_json"] is True  # no error-severity findings
    assert counts == {
        "duplicate_key": 1,
        "mixed_number_formats": 1,
        "non_rfc_number_literal": 1,
    }


# ------------------------------------------------------------------ #
# Syntax rule classification (empirically verified message zoo)
# ------------------------------------------------------------------ #

SYNTAX_MATRIX = [
    # (document, expected code)
    ('{"a":}', "syntax_error"),                    # Expecting value
    ('{"a" 1}', "syntax_error"),                   # Expecting ':' delimiter
    ('[1 2]', "syntax_error"),                     # Expecting ',' delimiter
    ('"unterminated', "syntax_error"),             # Unterminated string
    ('{"a": "\\q"}', "syntax_error"),              # Invalid \escape
    ("{'a': 1}", "syntax_error"),                  # single quotes
    ('nul', "syntax_error"),                       # truncated literal
    ('[1 2', "syntax_error"),                      # truncated array
    ('{"a": 01}', "syntax_error"),                 # leading zero
    ('[1, 2,, 3]', "syntax_error"),                # double comma is NOT
    ('[1,', "syntax_error"),                       #   a trailing comma
    ('[1, 2, ]', "trailing_comma_like"),
    ('[1,]', "trailing_comma_like"),
    ('{"a":1,}', "trailing_comma_like"),
    ('[\n  1,\n]\n', "trailing_comma_like"),       # multi-line shape
    ('{\n  "a": 1,\n}\n', "trailing_comma_like"),
    ('["a\nb"]', "string_unescaped_control_char"),  # raw newline in string
    ('"tab\there"', "string_unescaped_control_char"),
    ('["\\u0000"]', None),                          # escaped form is LEGAL
]


@pytest.mark.parametrize("doc,expected", SYNTAX_MATRIX)
def test_syntax_classification(doc, expected):
    result = lint(doc)
    if expected is None:
        assert "syntax_error" not in codes(result)
        assert "string_unescaped_control_char" not in codes(result)
        assert "trailing_comma_like" not in codes(result)
    else:
        assert expected in codes(result)
        finding = next(f for f in result["findings"] if f["code"] == expected)
        assert finding["severity"] == "error"
        assert result["valid_json"] is False


def test_syntax_error_position_exact():
    # Ground truth captured from json.JSONDecodeError on this
    # interpreter: pos 18 → line 3, col 7.
    result = lint('{\n  "a": 1,\n  "b" 2\n}')
    f = result["findings"][0]
    assert (f["line"], f["col"]) == (3, 7)
    assert "Expecting ':' delimiter" in f["message"]

    # Tab-indented document: col counts characters since the last \n.
    result = lint('{\n\t"a" 1}')
    f = result["findings"][0]
    assert (f["line"], f["col"]) == (2, 6)

    # Trailing comma finding sits at the closing bracket.
    result = lint('[1, 2, ]')
    f = result["findings"][0]
    assert f["code"] == "trailing_comma_like"
    assert (f["line"], f["col"]) == (1, 8)

    # Control character finding sits at the offending character.
    result = lint('["a\nb"]')
    f = result["findings"][0]
    assert f["code"] == "string_unescaped_control_char"
    assert (f["line"], f["col"]) == (1, 4)


def test_syntax_error_still_runs_text_level_rules():
    # A malformed document still reports a 5000+ character line.
    doc = '{"a": "' + "x" * 5001 + '" oops}'
    result = lint(doc)
    assert "syntax_error" in codes(result)
    assert "very_long_lines" in codes(result)


# ------------------------------------------------------------------ #
# Position converter vs the real exception (30 malformed docs)
# ------------------------------------------------------------------ #

MALFORMED_30 = [
    '{', '}', '[', ']', '{"a"}', '{"a":}', '{"a" 1}', '{a: 1}',
    "{'a': 1}", '[1 2]', '[1,,2]', '[1,]', '[,1]', '{"a":1,}', '{"a":,}',
    '"unterminated', '"bad\\escape"', 'tru', 'nul', 'fals', 'NaNx', '01',
    '{"a": "raw\ttab"}', '[[1, 2], {"b" 2}]', '{"a": [1, 2} ', '- ',
    '{"a": 1} {"b": 2}', '[}]', '{"a": 1,, "b": 2}', '{"k" v}',
]


def test_converter_agrees_with_exception_30_docs():
    seen = 0
    for doc in MALFORMED_30:
        try:
            json.loads(doc)
        except json.JSONDecodeError as exc:
            seen += 1
            # The exception itself carries lineno/colno on this
            # interpreter; our converter must agree exactly.
            assert (exc.lineno, exc.colno) \
                == _pos_to_line_col(exc.doc, exc.pos), doc
            # ... and so must the finding the tool reports.
            finding = next(
                f for f in lint(doc)["findings"]
                if f["code"] in ("syntax_error", "trailing_comma_like",
                                 "string_unescaped_control_char")
            )
            assert (finding["line"], finding["col"]) \
                == (exc.lineno, exc.colno), doc
    assert seen == 30  # every corpus member really is malformed


# ------------------------------------------------------------------ #
# BOM rule
# ------------------------------------------------------------------ #

def test_bom_rejected_and_linting_continues():
    doc = "﻿" + '{"a": 1, "a": 2}'
    result = lint(doc)
    bom = next(f for f in result["findings"] if f["code"] == "bom_not_allowed")
    assert bom["severity"] == "error"
    assert (bom["line"], bom["col"]) == (1, 1)
    assert "RFC 8259" in bom["message"]
    # The rest of the document is still linted after the sigil.
    assert "duplicate_key" in codes(result)
    assert result["valid_json"] is False
    # Ground truth: json.loads itself rejects the BOM.
    with pytest.raises(json.JSONDecodeError, match="Unexpected UTF-8 BOM"):
        json.loads(doc)


def test_bom_only_document():
    result = lint("﻿")
    assert sorted(codes(result)) == ["bom_not_allowed", "empty_document"]


def test_bom_positions_address_the_original_text():
    """Positions address the text the caller passed: the sigil occupies
    line 1 column 1, so every other line-1 finding shifts right by one
    column while the BOM finding itself does not move."""
    doc = "﻿" + '{"a": 1, "a": 2}'
    result = lint(doc)
    dup = next(f for f in result["findings"] if f["code"] == "duplicate_key")
    assert (dup["line"], dup["col"]) == (1, 11)
    bom = next(f for f in result["findings"] if f["code"] == "bom_not_allowed")
    assert (bom["line"], bom["col"]) == (1, 1)

    r = fix_hints("﻿" + '{"a": NaN, "b": 1.0}')
    by_code = {h["code"]: h for h in r["hints"]}
    assert (by_code["non_rfc_number_literal"]["line"],
            by_code["non_rfc_number_literal"]["col"]) == (1, 8)
    assert (by_code["mixed_number_formats"]["line"],
            by_code["mixed_number_formats"]["col"]) == (1, 18)
    assert (by_code["bom_not_allowed"]["line"],
            by_code["bom_not_allowed"]["col"]) == (1, 1)
    assert r["fixed_text"] == '{"a": NaN, "b": 1.0}'

    broken = fix_hints("﻿" + '{"a":}')
    assert broken["error"]["code"] == "syntax_error"
    assert (broken["error"]["line"], broken["error"]["col"]) == (1, 7)


# ------------------------------------------------------------------ #
# Empty and scalar-root documents
# ------------------------------------------------------------------ #

def test_empty_document():
    for doc in ("", "   ", "\n\n  \t "):
        result = lint(doc)
        assert codes(result) == ["empty_document"]
        assert result["findings"][0]["severity"] == "error"
        assert result["valid_json"] is False


def test_scalar_only_document():
    for doc, py in (("42", int), ('"hi"', str), ("true", bool),
                    ("null", type(None)), ("1.5", float)):
        result = lint(doc)
        assert codes(result) == ["scalar_only_document"]
        f = result["findings"][0]
        assert f["severity"] == "info"
        assert result["valid_json"] is True  # legal JSON, after all
        assert isinstance(json.loads(doc), py)
    # Containers are not flagged.
    assert lint('{"a": 1}')['findings'] == []
    assert lint('[]')['findings'] == []


# ------------------------------------------------------------------ #
# Duplicate keys: silent last-wins truth + text positions
# ------------------------------------------------------------------ #

def test_duplicate_key_ground_truth_last_wins():
    # The very behavior the tool exists to surface.
    assert json.loads('{"a": 1, "a": 2}') == {"a": 2}
    pairs = json.loads('{"a": 1, "a": 2}',
                       object_pairs_hook=lambda p: p)
    assert pairs == [("a", 1), ("a", 2)]  # the hook sees every pair


def test_duplicate_key_finding_position():
    result = lint('{"a": 1, "a": 2}')
    assert codes(result) == ["duplicate_key"]
    f = result["findings"][0]
    assert f["severity"] == "warning"
    assert (f["line"], f["col"]) == (1, 10)  # second occurrence
    assert "LAST value" in f["message"]

    # Multi-line: the second occurrence is on line 3, col 3.
    result = lint('{\n  "a": 1,\n  "a": 2\n}')
    assert (result["findings"][0]["line"], result["findings"][0]["col"]) \
        == (3, 3)


def test_duplicate_key_three_occurrences_one_finding():
    result = lint('{"a": 1, "a": 2, "a": 3}')
    dup = [f for f in result["findings"] if f["code"] == "duplicate_key"]
    assert len(dup) == 1
    assert "appears 3 times" in dup[0]["message"]


DUP_CORPUS = [
    # (document, duplicated names — hook truth)
    ('{"a": 1, "a": 2}', ["a"]),
    ('{"a": 1, "\\u0061": 2}', ["a"]),          # escape spelling collision
    ('{"中文": 1, "中文": 2}', ["中文"]),          # CJK raw
    ('{"\\u4e2d\\u6587": 1, "中文": 2}', ["中文"]),  # CJK escape vs raw
    ('{"a\\"b": 1, "a\\"b": 2}', ['a"b']),      # escaped quote in the name
    ('{"a": 1, "b": 2}', []),
    ('{"a": {"x": 1}, "b": {"x": 2}}', []),      # same name, other objects
    ('{"a": {"x": 1, "x": 2}}', ["x"]),          # nested object dup
    ('[{"k": 1, "k": 2}]', ["k"]),               # dup inside an array item
    ('{"a": "x, [1] {z} y", "a": 2}', ["a"]),    # structural chars in values
    ('{"a": 1, "A": 2}', []),                    # case differs: no dup
    ('{"": 1, "": 2}', [""]),                     # empty-name dup
]


@pytest.mark.parametrize("doc,expected_names", DUP_CORPUS)
def test_duplicate_scanner_matches_hook_truth(doc, expected_names):
    # Independent hook truth: which names repeat inside one object.
    seen_per_object = []

    def hook(pairs):
        names = [n for n, _ in pairs]
        seen_per_object.append([n for n in set(names)
                                if names.count(n) > 1])
        return dict(pairs)

    json.loads(doc, object_pairs_hook=hook)
    truth = sorted(n for dups in seen_per_object for n in dups)

    result = lint(doc)
    dup_findings = [f for f in result["findings"]
                    if f["code"] == "duplicate_key"]
    assert len(dup_findings) == len(truth)
    for name in truth:
        needle = json.dumps(name, ensure_ascii=False)
        assert any(needle in f["message"] for f in dup_findings), (doc, name)
    # And no false positives beyond the truth.
    for f in dup_findings:
        assert any(json.dumps(n, ensure_ascii=False) in f["message"]
                   for n in truth), (doc, f)


def test_no_duplicate_finding_without_dup():
    result = lint('{"a": 1, "b": 2, "c": {"a": 3}}')
    assert "duplicate_key" not in codes(result)


# ------------------------------------------------------------------ #
# NaN / Infinity literals — accepted by loads, flagged as non-RFC
# ------------------------------------------------------------------ #

def test_nan_infinity_acceptance_ground_truth():
    # Empirical: json.loads ACCEPTS these by default...
    parsed = json.loads("[NaN, Infinity, -Infinity]")
    assert math.isnan(parsed[0]) and parsed[1] == math.inf \
        and parsed[2] == -math.inf
    # ...while strict serialization refuses them (the tool's note).
    with pytest.raises(ValueError, match="not JSON compliant"):
        json.dumps(float("nan"), allow_nan=False)


def test_nan_infinity_flagged_with_positions():
    result = lint("[NaN, Infinity, -Infinity]")
    assert result["valid_json"] is True  # parses — that is the trap
    nan = [f for f in result["findings"]
           if f["code"] == "non_rfc_number_literal"]
    assert [(f["line"], f["col"]) for f in nan] \
        == [(1, 2), (1, 7), (1, 17)]
    for f in nan:
        assert f["severity"] == "info"
        assert "RFC 8259" in f["message"]
        assert "allow_nan=False" in f["message"]

    # Multi-line position: {"x": NaN} with the value on line 2.
    result = lint('{\n "x": NaN\n}')
    f = next(f for f in result["findings"]
             if f["code"] == "non_rfc_number_literal")
    assert (f["line"], f["col"]) == (2, 7)


# ------------------------------------------------------------------ #
# Mixed number formats (integer-valued floats)
# ------------------------------------------------------------------ #

def test_mixed_number_formats():
    result = lint('{"a": 1.0, "b": 2e2, "c": 1.5, "d": 3, "e": -0.5}')
    mixed = [f for f in result["findings"]
             if f["code"] == "mixed_number_formats"]
    assert [(f["line"], f["col"]) for f in mixed] == [(1, 7), (1, 17)]
    assert "1.0" in mixed[0]["message"] and "'1'" not in mixed[0]["message"]
    assert "2e2" in mixed[1]["message"]
    # 1.5 / 3 / -0.5 are not integer-valued floats — no finding.
    assert len(mixed) == 2


def test_overflowing_float_not_flagged():
    # 1e400 parses to inf — flagged by nothing here (not NaN literal,
    # not an integer-valued float; it IS accepted by loads).
    result = lint("[1e400]")
    assert codes(result) == []
    assert math.isinf(json.loads("[1e400]")[0])


# ------------------------------------------------------------------ #
# Very long lines
# ------------------------------------------------------------------ #

def test_long_line_threshold_boundary():
    # Exactly 5000 characters: clean. 5010: one finding.
    doc = '{"a": "' + "x" * 4991 + '"}'
    assert len(doc) == 5000
    assert lint(doc)["findings"] == []

    doc = '{"a": "' + "x" * 5001 + '"}'
    assert len(doc) == 5010
    result = lint(doc)
    assert codes(result) == ["very_long_lines"]
    f = result["findings"][0]
    assert f["severity"] == "info"
    assert (f["line"], f["col"]) == (1, 1)
    assert "5010 characters" in f["message"]


def test_long_line_only_offending_line():
    doc = '{"a": 1,\n "b": "' + "y" * 6000 + '",\n "c": 2}\n'
    result = lint(doc)
    assert codes(result) == ["very_long_lines"]
    assert result["findings"][0]["line"] == 2


def test_line_convention_counts_newlines_only():
    """Every position rule counts \\n only, exactly like
    json.JSONDecodeError — so the line-length rule and the summary must
    too: raw U+2028 inside a string is legal JSON (>= U+0020) and must
    NOT split a line the way str.splitlines() would."""
    sep = "\u2028"
    doc = '["' + "x" * 3000 + sep + "y" * 3000 + '"]'
    assert isinstance(json.loads(doc), list)  # parses; sep is in-string
    assert len(doc.split("\n")) == 1
    assert len(doc.splitlines()) == 2
    result = lint(doc)
    assert codes(result) == ["very_long_lines"]
    assert result["findings"][0]["line"] == 1
    assert "6005 characters" in result["findings"][0]["message"]
    assert result["summary"]["lines"] == 1

    assert lint('{"a": 1}\r\n')["summary"]["lines"] == 2


# ------------------------------------------------------------------ #
# Deep nesting
# ------------------------------------------------------------------ #

def _nest(depth):
    """An object chain of the given container depth."""
    return '{"a":' * depth + "1" + "}" * depth


def test_deep_nesting_threshold():
    assert lint(_nest(12))["findings"] == []  # depth 12: clean

    result = lint(_nest(13))
    assert codes(result) == ["deeply_nested"]
    f = result["findings"][0]
    assert f["severity"] == "info"
    assert "depth 13" in f["message"]
    assert "threshold 12" in f["message"]

    arr_doc = "[" * 13 + "1" + "]" * 13
    assert codes(lint(arr_doc)) == ["deeply_nested"]
    assert lint("[" * 12 + "1" + "]" * 12)["findings"] == []


def test_nesting_beyond_parser_limit_reported_not_raised():
    """Ground truth: the C json scanner recurses per container level,
    so past the interpreter recursion limit json.loads dies with
    RecursionError (NOT JSONDecodeError). The tool reports that as a
    classified finding/error payload in every mode — leaking
    RecursionError out of execute() would crash the caller."""
    depth = sys.getrecursionlimit() * 3
    assert depth > 12

    for doc in ("[" * depth + "1" + "]" * depth,
                '{"a":' * depth + "1" + "}" * depth):
        with pytest.raises(RecursionError):
            json.loads(doc)

        result = lint(doc)
        assert result["valid_json"] is False
        assert "nesting_exceeds_parser_limit" in codes(result)
        finding = next(f for f in result["findings"]
                       if f["code"] == "nesting_exceeds_parser_limit")
        assert finding["severity"] == "error"
        assert (finding["line"], finding["col"]) == (1, 1)

        assert profile(doc)["error"]["code"] \
            == "nesting_exceeds_parser_limit"
        assert fix_hints(doc)["error"]["code"] \
            == "nesting_exceeds_parser_limit"

    ok_doc = "[" * 50 + "1" + "]" * 50
    assert profile(ok_doc)["max_depth"] == 50


# ------------------------------------------------------------------ #
# Inconsistent key case (heuristic)
# ------------------------------------------------------------------ #

def test_inconsistent_key_case():
    result = lint('{"firstName": 1, "last_name": 2}')
    assert codes(result) == ["inconsistent_key_case"]
    f = result["findings"][0]
    assert f["severity"] == "info"
    assert (f["line"], f["col"]) == (1, 1)  # at the object's brace
    assert "camelCase" in f["message"] and "snake_case" in f["message"]

    # Uniform objects and pattern-free keys stay clean.
    for doc in ('{"firstName": 1, "lastName": 2}',
                '{"first_name": 1, "last_name": 2}',
                '{"XML": 1, "a": 2, "B2": 3}',
                '{"single": 1}'):
        assert lint(doc)["findings"] == [], doc


def test_inconsistent_key_case_per_object_only():
    # Mixed styles in DIFFERENT objects are fine (per-object rule).
    doc = '{"outer_camel": 1, "inner": {"snake_case": 2}}'
    assert lint(doc)["findings"] == []


# ------------------------------------------------------------------ #
# profile mode — hand-verified arithmetic
# ------------------------------------------------------------------ #

PROFILE_DOC = (
    '{"name": "au", "version": 1, "ratio": 0.5,'
    ' "tags": ["a", "bc"],'
    ' "nested": {"deep": [1, 2, 3], "ok": true, "nope": null}}'
)


def test_profile_hand_verified():
    p = profile(PROFILE_DOC)
    assert p["mode"] == "profile"
    # type_counts — counted by hand over the fixture:
    assert p["type_counts"] == {
        "object": 2, "array": 2, "string": 3,
        "number": 5, "boolean": 1, "null": 1,
    }
    assert p["numbers"] == {"int": 4, "float": 1}
    assert p["max_depth"] == 3  # root obj / nested obj+tags arr / deep arr
    assert p["keys"]["total"] == 8
    assert p["keys"]["distinct"] == 8
    assert p["keys"]["distinct_names"] == sorted([
        "name", "version", "ratio", "tags", "nested",
        "deep", "ok", "nope",
    ])
    # arrays: tags len 2, deep len 3 → min 2, max 3, total 5, avg 2.5
    assert p["arrays"] == {
        "count": 2, "min_len": 2, "max_len": 3, "total_len": 5,
        "avg_len": 2.5,
    }
    # strings: "au"(2), "a"(1), "bc"(2) → min 1, max 2, total 5,
    # avg round(5/3, 2) == 1.67
    assert p["strings"] == {
        "count": 3, "min_len": 1, "max_len": 2, "total_len": 5,
        "avg_len": 1.67,
    }


def test_profile_scalar_and_empty_and_broken():
    p = profile("42")
    assert p["type_counts"] == {
        "object": 0, "array": 0, "string": 0,
        "number": 1, "boolean": 0, "null": 0,
    }
    assert p["max_depth"] == 0
    assert p["keys"] == {"total": 0, "distinct": 0, "distinct_names": []}
    assert p["arrays"] == {"count": 0}
    assert p["strings"] == {"count": 0}

    assert profile("")["error"]["code"] == "empty_document"
    assert profile("﻿{}")["error"]["code"] == "bom_not_allowed"
    err = profile('{"a":}')
    assert err["error"]["code"] == "syntax_error"
    assert err["error"]["line"] == 1 and err["error"]["col"] == 6


def test_profile_duplicate_keys_merge_like_loads():
    # Profile walks the parsed value — duplicates already collapsed
    # (last wins), exactly like json.loads itself.
    p = profile('{"a": 1, "a": {"x": 1}}')
    assert p["keys"]["total"] == 2
    assert p["keys"]["distinct_names"] == ["a", "x"]


def test_profile_nan_counts_as_float():
    p = profile('{"a": NaN, "b": 1}')
    assert p["numbers"] == {"int": 1, "float": 1}


# ------------------------------------------------------------------ #
# fix_hints mode — safe textual fixes only
# ------------------------------------------------------------------ #

def test_fix_hints_bom_strip_and_re_lint():
    doc = "﻿" + '{"a": NaN}'
    r = fix_hints(doc)
    assert r["fixed_text"] == '{"a": NaN}'
    assert len(r["hints"]) == 2
    bom = next(h for h in r["hints"] if h["code"] == "bom_not_allowed")
    assert bom["applied"] is True

    # Apply the one applied hint and re-lint: the BOM finding is
    # gone, the NaN info legitimately remains.
    re_lint = lint(r["fixed_text"])
    assert "bom_not_allowed" not in codes(re_lint)
    assert "non_rfc_number_literal" in codes(re_lint)
    assert re_lint["valid_json"] is True


def test_fix_hints_nan_position_never_applied():
    r = fix_hints('{"a": NaN, "b": Infinity}')
    assert r["fixed_text"] is None  # nothing auto-applied
    hints = [h for h in r["hints"]
             if h["code"] == "non_rfc_number_literal"]
    assert [(h["line"], h["col"]) for h in hints] == [(1, 7), (1, 17)]
    assert all(h["suggestion"] == "null" and h["applied"] is False
               for h in hints)
    assert "never applied automatically" in r["note"]


def test_fix_hints_mixed_number_suggestion_only():
    r = fix_hints('{"a": 1.0, "b": 2e2}')
    hints = [h for h in r["hints"] if h["code"] == "mixed_number_formats"]
    assert [h["suggestion"] for h in hints] == ["1", "200"]
    assert all(h["applied"] is False for h in hints)


def test_fix_hints_clean_and_broken():
    r = fix_hints('{"a": 1}')
    assert r["hints"] == [] and r["fixed_text"] is None

    r = fix_hints('{"a":}')
    assert r["error"]["code"] == "syntax_error"
    assert "fix the syntax error first" in r["error"]["message"]


def test_fix_hints_empty_and_bom_only_mirror_profile():
    """Empty and BOM-only documents are classified exactly like the
    other two modes classify them — never as a bare syntax_error."""
    for empty_doc in ("", "   ", "\n\t"):
        assert fix_hints(empty_doc)["error"]["code"] == "empty_document"
    assert fix_hints("﻿")["error"]["code"] == "bom_not_allowed"


def test_fix_hints_deterministic_order():
    doc = '{"b": NaN, "a": 1.0, "c": NaN}'
    assert fix_hints(doc) == fix_hints(doc)
    r = fix_hints(doc)
    assert [(h["line"], h["col"]) for h in r["hints"]] \
        == [(1, 7), (1, 17), (1, 27)]


# ------------------------------------------------------------------ #
# Unicode content beyond keys
# ------------------------------------------------------------------ #

def test_unicode_values_and_escapes_clean():
    doc = '{"msg": "中文测试 \\u00e9 \\n\\t", "emoji": "🎉"}'
    result = lint(doc)
    assert result["findings"] == []
    assert result["valid_json"] is True


def test_scan_stays_linear_on_huge_single_line():
    """The raw-text scan carries the current line incrementally; a
    one-line document with hundreds of thousands of tokens must lint
    in one pass, not recompute line/col from the text prefix per token
    (the quadratic shape this regression pins out took tens of seconds
    on 300k characters before the fix)."""
    doc = "[" + ",".join("1" for _ in range(150_000)) + "]"
    assert len(doc) == 300_001
    start = time.monotonic()
    result = lint(doc)
    elapsed = time.monotonic() - start
    assert codes(result) == ["very_long_lines"]
    assert elapsed < 5.0

    keys_doc = "{" + ",".join(f'"k{i}": {i}' for i in range(40_000)) + "}"
    start = time.monotonic()
    result = lint(keys_doc)
    elapsed = time.monotonic() - start
    assert result["valid_json"] is True
    assert elapsed < 5.0


def test_cjk_duplicate_key_across_escape_forms():
    # The decoded name is identical — the hook confirms it, the
    # scanner still locates the second spelling in the text.
    doc = '{"\\u4e2d\\u6587": 1, "中文": 2}'
    result = lint(doc)
    assert codes(result) == ["duplicate_key"]
    assert (result["findings"][0]["line"],
            result["findings"][0]["col"]) == (1, 21)


# ------------------------------------------------------------------ #
# Cross-rule document — everything fires together
# ------------------------------------------------------------------ #

def test_kitchen_sink():
    doc = (
        "﻿"
        '{\n'
        '  "firstName": "au", "last_name": 1,\n'
        '  "v": 1.0, "v": 2,\n'
        '  "bad": NaN\n'
        "}"
    )
    result = lint(doc)
    rule_counts = result["summary"]["rule_counts"]
    assert rule_counts.get("bom_not_allowed") == 1
    assert rule_counts.get("duplicate_key") == 1
    assert rule_counts.get("inconsistent_key_case") == 1
    assert rule_counts.get("mixed_number_formats") == 1
    assert rule_counts.get("non_rfc_number_literal") == 1
    assert result["valid_json"] is False  # the BOM is an error
    # Findings sorted by (line, col, code).
    keys = [(f["line"], f["col"], f["code"]) for f in result["findings"]]
    assert keys == sorted(keys)

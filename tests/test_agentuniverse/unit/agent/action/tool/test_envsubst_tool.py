#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_envsubst_tool.py

"""Offline unit tests for EnvsubstTool, with a real-bash oracle.

The tool itself is built purely on the standard library and never
spawns a process; the ORACLE side of this suite does run the real
``bash`` binary (tests only — the tool's runtime stays stdlib-only and
eval-free) to pin the parameter-expansion semantics byte-for-byte.

Oracle harness, honestly documented
-----------------------------------
Comparing against bash directly is subtle: naively injecting a
template into a ``bash -c`` command line is injection-prone, and the
``envsubst`` binary only understands the basic ``$VAR`` / ``${VAR}``
forms — none of the parameter-expansion dialect.  The harness instead
REBUILDS the template with the mapping applied by real bash: it
re-splits the template with the tool's own scanner (so the split the
oracle sees is exactly the split the tool produced — splitting is
pinned separately by analyze-mode unit tests), emits every literal
piece as a single-quoted shell word, passes every expansion token
*verbatim* inside double quotes, and lets bash concatenate them with
``printf '%s'``.  The expansion semantics therefore come from real
bash; only the literal/expansion splitting is trusted to the tool.
For seeded cases whose literal text contains no ``"`` and no ``\\``
the harness additionally feeds the ENTIRE template to bash as one
double-quoted word — a splitter-independent cross-check — and asserts
both oracles agree.

Bash invocation details: the binary is located once (``$ENVSUBST_TEST_BASH``,
then common bash-5 paths, then ``/bin/bash``); a UTF-8 ``LC_ALL`` is
pinned when the platform has one (so ``${#VAR}`` counts characters as
the tool does); negative substring lengths (bash >= 4.2) are
feature-detected and those cases are skipped on bash 3.2.  Cases are
batched — each wrapped in a subshell so a triggered ``:?`` guard
aborts only that case — with per-case sentinels carrying the exit
status.  Everything is deterministic: fixed seeds, no clock.
"""

import os
import random
import re
import subprocess
import time
import unittest

from agentuniverse.agent.action.tool.common_tool import EnvsubstTool
from agentuniverse.agent.action.tool.common_tool.envsubst_tool import (
    MAX_ENV_VARS,
    MAX_TEMPLATE_CHARS,
    MAX_VALUE_CHARS,
    EnvsubstTool as DirectEnvsubstTool,
    _Parser,
    _TemplateError,
)

# --------------------------------------------------------------------- #
# bash oracle harness
# --------------------------------------------------------------------- #


def _find_bash():
    override = os.environ.get("ENVSUBST_TEST_BASH")
    candidates = []
    if override:
        candidates.append(override)
    candidates += [
        "/opt/homebrew/bin/bash",
        "/usr/local/bin/bash",
        "/usr/bin/bash",
        "/bin/bash",
    ]
    for path in candidates:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def _run_bash(script, env, timeout=30):
    full_env = dict(env)
    if _UTF8_LOCALE:
        full_env["LC_ALL"] = _UTF8_LOCALE
    proc = subprocess.run(
        [BASH, "-c", script],
        env=full_env,
        capture_output=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


BASH = _find_bash()


def _detect_utf8_locale():
    if not BASH:
        return None
    for locale in ("C.UTF-8", "en_US.UTF-8", "en_US.utf8"):
        try:
            proc = subprocess.run(
                [BASH, "-c", 'printf %s "${#M}"'],
                env={"M": "héllo", "LC_ALL": locale},
                capture_output=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if proc.returncode == 0 and proc.stdout == b"5":
            return locale
    return None


_UTF8_LOCALE = _detect_utf8_locale() if BASH else None


def _supports_negative_length():
    if not BASH:
        return False
    try:
        proc = subprocess.run(
            [BASH, "-c", 'printf %s "${S:2:-1}"'],
            env={"S": "abcdef"},
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0 and proc.stdout == b"cde"


_HAS_NEGATIVE_LENGTH = _supports_negative_length()

# Bash-3.2 (the macOS default) lacks negative substring lengths; the
# seeded corpus filters those cases when running against it.
NEGATIVE_LENGTH_SKIP = not _HAS_NEGATIVE_LENGTH


def tool_split(template):
    """Split a template with the tool's scanner into oracle pieces."""
    nodes = _Parser(template).parse()
    return [
        ("lit", payload) if kind == "lit" else ("exp", payload["source"])
        for kind, payload in nodes
    ]


def _render_pieces(pieces):
    parts = []
    for kind, text in pieces:
        if kind == "lit":
            parts.append("'" + text.replace("'", "'\\''") + "'")
        else:
            parts.append('"' + text + '"')
    return " ".join(parts)


def bash_expand(template, env, whole_template=False):
    """Run the oracle for one template. Returns (rc, text_bytes).

    whole_template=True feeds the entire template as a single
    double-quoted word (only safe when the literal text contains no
    double quote and no backslash).
    """
    if whole_template:
        assert '"' not in template and "\\" not in template
        pieces = [("exp", template)]
    else:
        try:
            pieces = tool_split(template)
        except _TemplateError:
            # The scanner itself rejects; fall back to feeding the raw
            # template to bash when it is safe to wrap, so genuinely
            # invalid templates can still be compared.
            if '"' in template or "\\" in template:
                return None, b""
            pieces = [("exp", template)]
    script = "printf '%s' " + _render_pieces(pieces)
    rc, out, _ = _run_bash(script, env)
    return rc, out


def bash_expand_batch(cases):
    """Run many (template, env) oracle cases in a few bash processes.

    Each case runs in a subshell with its own exported variables (a
    triggered :? aborts only that case); a per-case sentinel carries
    the exit status.  Returns a list of (rc, stdout_bytes) aligned
    with `cases`.
    """
    results = []
    batch_size = 50
    counter = 0

    def render_case(tpl, env, sentinel):
        exports = "".join(
            "export %s=%s; " % (key, "'" + value.replace("'", "'\\''") + "'")
            for key, value in env.items()
        )
        pieces = tool_split(tpl)
        return (
            "( %sprintf '%%s' %s ) 2>/dev/null; rc=$?; "
            "printf '\\n@@RC='\"$rc\"':%s@@\\n'"
            % (exports, _render_pieces(pieces), sentinel)
        )

    for start in range(0, len(cases), batch_size):
        chunk = cases[start : start + batch_size]
        lines = []
        sentinels = []
        for idx, (tpl, env) in enumerate(chunk):
            sentinel = "__ENVSUBST_ORACLE_%d_%d__" % (counter, idx)
            sentinels.append(sentinel)
            lines.append(render_case(tpl, env, sentinel))
        rc, out, _ = _run_bash("\n".join(lines), {}, timeout=120)
        assert rc == 0, "oracle batch script itself failed"
        for sentinel in sentinels:
            pattern = re.compile(
                rb"\n@@RC=(\d+):" + re.escape(sentinel.encode()) + rb"@@\n"
            )
            match = pattern.search(out)
            assert match, "oracle sentinel %s not found" % sentinel
            results.append((int(match.group(1)), out[: match.start()]))
            out = out[match.end() :]
        counter += 1
    return results


# --------------------------------------------------------------------- #
# deterministic seeded corpus generator
# --------------------------------------------------------------------- #

_NAMES = ["A", "B2", "C_D", "X"]
_VALUES = [
    "",
    "0",
    "abcabc",
    "a*b",
    "hello World",
    "abcdef",
    "a.c",
    "x\\*",
    "it's",
    'say "hi"',
    "héllo" if _UTF8_LOCALE else "hello",
    "a]b",
    "a-b",
    "[x",
    "*",
    "?",
    "a b",
    "ABC",
    "zZa",
    "$dollar",
    "tab\there",
    "line1\nline2",
    "%",
    "%%s",
]
_LITERALS = [
    "",
    " ",
    "x",
    "a b",
    "-",
    "}",
    "{",
    "|",
    ".",
    "\n",
    "]",
    "it's fine",
    'say "hi"',
    "100%",
    "a\\b",
    "café" if _UTF8_LOCALE else "cafe",
    "...",
    "say",
    "Asay",
]
_WORDS = [
    "d",
    "",
    "a b",
    "'q'",
    '"d"',
    "\\$X",
    "\\}",
    "\\x",
    "\\\\",
    "it\\'s",
    "${A}",
    "$A",
    "${A:-inner}",
    "${B2:+alt}",
    "*",
    "?",
    "[a-c]",
    "a*",
    "\\*",
    "%s",
    "  ",
    "a\\'b",
    '\\"q\\"',
    "$B2tail",
    "${A}x",
]
_SUBSTR_SPECS = [
    "0", "1", "2", "3", "100", " -2", " -3", " +1", "-6", "-100",
    ":1", ":2", ":3", ":100", ":0",
    ":-1", ":-2", ":-100",
]


def _negative_length_allowed(spec):
    return (":-" not in spec) or not NEGATIVE_LENGTH_SKIP


def _rand_expansion(rng):
    kind = rng.randrange(13)
    name = rng.choice(_NAMES)
    if kind == 0:
        return "$" + name
    if kind == 1:
        return "${%s}" % name
    if kind == 2:
        return "${#%s}" % name
    if kind == 3:
        return "${%s%s%s}" % (name, rng.choice([":-", "-"]), rng.choice(_WORDS))
    if kind == 4:
        return "${%s%s%s}" % (name, rng.choice([":=", "="]), rng.choice(_WORDS))
    if kind == 5:
        return "${%s%s%s}" % (name, rng.choice([":+", "+"]), rng.choice(_WORDS))
    if kind == 6:
        pattern = rng.choice(["", "[a-z]", "*", "?", "[a-l]"])
        return "${%s%s%s}" % (
            name,
            rng.choice(["^", "^^", ",", ",,"]),
            pattern,
        )
    if kind == 7:
        pattern = rng.choice(
            ["", "*", "*.c", "[a-c]*", "?b", "\\*", "b?c*", "[!a-c]", "%s", "[", "]", "-", "a-b"]
        )
        return "${%s%s%s}" % (
            name,
            rng.choice(["%", "%%", "#", "##"]),
            pattern,
        )
    if kind == 8:
        while True:
            spec = rng.choice(_SUBSTR_SPECS)
            if _negative_length_allowed(spec):
                break
        return "${%s:%s}" % (name, spec)
    if kind == 9:
        return "${%s%s${%s}}" % (
            name,
            rng.choice([":-", "-"]),
            rng.choice(_NAMES),
        )
    if kind == 10:
        return "$%s$%s" % (rng.choice(_NAMES), rng.choice(_NAMES))
    if kind == 11:
        return "${%s:-%s}" % (
            name,
            rng.choice(["${A}", "$B2", "x${A:-d}y"]),
        )
    return "${%s%s%s}" % (
        name,
        rng.choice([":?", "?"]),
        rng.choice(["", "m", "${A}"]),
    )


def _seeded_corpus(count, seed=20261021):
    """Deterministic (template, env) pairs covering the subset grammar."""
    rng = random.Random(seed)
    corpus = []
    for _ in range(count):
        pieces = []
        for _ in range(rng.randrange(1, 6)):
            pieces.append(("lit", rng.choice(_LITERALS)))
            pieces.append(("exp", _rand_expansion(rng)))
        pieces.append(("lit", rng.choice(_LITERALS)))
        template = "".join(text for _, text in pieces)
        env = {}
        for name in _NAMES:
            roll = rng.random()
            if roll < 0.45:
                env[name] = rng.choice(_VALUES)
            elif roll < 0.55:
                env[name] = ""  # explicitly empty (set vs unset battery)
        corpus.append((template, env))
    return corpus


# --------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------- #


@unittest.skipIf(BASH is None, "no bash binary available for the oracle")
class EnvsubstToolUnitTestCase(unittest.TestCase):
    """Deterministic offline tests (no bash required)."""

    def setUp(self) -> None:
        self.tool = EnvsubstTool()

    def expand(self, template, **env):
        return self.tool.execute(mode="expand", template=template, env=env)

    # -- expand: basics --------------------------------------------- #

    def test_basic_forms(self):
        self.assertEqual(
            self.expand("Hello ${NAME} and $OTHER end", NAME="x")["text"],
            "Hello x and  end",
        )
        self.assertEqual(self.expand("no refs")["text"], "no refs")
        self.assertEqual(self.expand("")["text"], "")

    def test_unresolved_and_expanded_tracking(self):
        result = self.expand("${A} ${B:-bee} $C", A="a", C="")
        self.assertEqual(result["expanded"], ["A", "C"])
        # C is present with an empty value -> resolved; B fell back to
        # its default -> unresolved WITH the default that applied.
        self.assertEqual(
            result["unresolved"],
            [
                {"name": "B", "default": "bee", "forms": ["default_colon"]},
            ],
        )

    def test_assignments_reported_and_env_not_mutated(self):
        env = {"KEEP": "k", "SET": "already"}
        result = self.tool.execute(
            mode="expand",
            template="${NEW:=fresh}/${SET:=nope}/${PLAIN=z}",
            env=env,
        )
        # SET is set non-empty -> untouched; PLAIN fires on unset.
        self.assertEqual(result["text"], "fresh/already/z")
        self.assertEqual(
            result["assignments"],
            [
                {"name": "NEW", "value": "fresh"},
                {"name": "PLAIN", "value": "z"},
            ],
        )
        self.assertEqual(env, {"KEEP": "k", "SET": "already"})

    def test_assign_persists_within_template(self):
        result = self.expand("${A:=one}/${A}/${A:=two}")
        self.assertEqual(result["text"], "one/one/one")
        self.assertEqual(
            result["assignments"], [{"name": "A", "value": "one"}]
        )

    def test_guard_error_payload(self):
        result = self.expand("${MISSING:?custom message}")
        self.assertEqual(
            result["error"],
            {
                "type": "required_variable_missing",
                "var": "MISSING",
                "message": "custom message",
            },
        )
        result = self.expand("${MISSING:?}")
        self.assertEqual(
            result["error"]["message"], "parameter null or not set"
        )
        result = self.expand("${MISSING?}")
        self.assertEqual(result["error"]["message"], "parameter not set")

    def test_guard_empty_vs_unset(self):
        self.assertIn("text", self.expand("${V?m}", V=""))
        self.assertIn("error", self.expand("${V:?m}", V=""))

    def test_length_form(self):
        self.assertEqual(self.expand("${#V}", V="abc")["text"], "3")
        self.assertEqual(self.expand("${#V}")["text"], "0")

    def test_strip_forms(self):
        env = {"V": "abcabc"}
        self.assertEqual(self.expand("${V%b*c}", **env)["text"], "abca")
        self.assertEqual(self.expand("${V%%b*c}", **env)["text"], "a")
        self.assertEqual(self.expand("${V#a*b}", **env)["text"], "cabc")
        self.assertEqual(self.expand("${V##a*b}", **env)["text"], "c")
        self.assertEqual(self.expand("${V%}", **env)["text"], "abcabc")

    def test_substring_forms(self):
        env = {"S": "abcdef"}
        self.assertEqual(self.expand("${S:2}", **env)["text"], "cdef")
        self.assertEqual(self.expand("${S:2:3}", **env)["text"], "cde")
        self.assertEqual(self.expand("${S: -3}", **env)["text"], "def")
        self.assertEqual(self.expand("${S: 2 : 3 }", **env)["text"], "cde")
        self.assertEqual(self.expand("${S::2}", **env)["text"], "ab")
        self.assertEqual(self.expand("${S:100}", **env)["text"], "")
        self.assertEqual(self.expand("${S: -100}", **env)["text"], "")

    def test_substring_negative_length(self):
        env = {"S": "abcdef"}
        if not _HAS_NEGATIVE_LENGTH:
            self.skipTest("bash lacks negative substring lengths")
        self.assertEqual(self.expand("${S:2:-1}", **env)["text"], "cde")
        self.assertEqual(self.expand("${S:0:-2}", **env)["text"], "abcd")
        self.assertEqual(self.expand("${S:0:-6}", **env)["text"], "")
        result = self.expand("${S:5:-3}", **env)
        self.assertEqual(result["error"]["type"], "invalid_template")
        self.assertIn("substring expression < 0", result["error"]["message"])

    def test_substring_unset_short_circuits(self):
        # bash skips the whole expression for unset variables.
        result = self.expand("${X:0:-2}")
        self.assertEqual(result["text"], "")

    def test_case_forms(self):
        env = {"C": "hello World"}
        self.assertEqual(self.expand("${C^}", **env)["text"], "Hello World")
        self.assertEqual(self.expand("${C^^}", **env)["text"], "HELLO WORLD")
        self.assertEqual(self.expand("${C,}", **env)["text"], "hello World")
        self.assertEqual(self.expand("${C,,}", **env)["text"], "hello world")
        self.assertEqual(
            self.expand("${C^^[a-l]}", **env)["text"], "HELLo WorLD"
        )

    def test_quoting_in_words(self):
        self.assertEqual(self.expand('${V:-"d"}')["text"], "d")
        self.assertEqual(self.expand("${V:-'d'}")["text"], "'d'")
        self.assertEqual(self.expand("${V:-a b}")["text"], "a b")
        self.assertEqual(self.expand("${V:-\\$X}")["text"], "$X")
        self.assertEqual(self.expand("${V:-a\\}b}")["text"], "a}b")
        self.assertEqual(self.expand("${V:-\\x}")["text"], "\\x")
        self.assertEqual(self.expand("${V:-it\\'s}")["text"], "it\\'s")

    def test_nested_expansion(self):
        self.assertEqual(self.expand("${A:-${B:-c}}")["text"], "c")
        self.assertEqual(
            self.expand("${A:-${B:-c}}", B="bee")["text"], "bee"
        )
        self.assertEqual(self.expand("${A:-${B:-c}}", A="ay")["text"], "ay")
        self.assertEqual(
            self.expand("x${D2:-inner}y")["text"], "xinnery"
        )

    def test_lone_dollar_is_literal(self):
        self.assertEqual(self.expand("$ x")["text"], "$ x")
        self.assertEqual(self.expand("$")["text"], "$")
        self.assertEqual(self.expand("a$}")["text"], "a$}")
        self.assertEqual(self.expand("a$b")["text"], "a")  # b is a name

    def test_name_boundary_absorbs_following_text(self):
        result = self.expand("$Asay")
        self.assertEqual(result["text"], "")
        analysis = self.tool.execute(mode="analyze", template="$Asay")
        self.assertEqual(
            [v["name"] for v in analysis["variables"]], ["Asay"]
        )

    # -- analyze ------------------------------------------------------ #

    def test_analyze_reports(self):
        analysis = self.tool.execute(
            mode="analyze",
            template="${A} ${B:-b} ${C:?need} $D ${A:-a2} ${E:-${F}}",
        )
        self.assertEqual(
            [v["name"] for v in analysis["variables"]], ["A", "B", "C", "D", "E", "F"]
        )
        by_name = {v["name"]: v for v in analysis["variables"]}
        self.assertEqual(
            by_name["A"]["forms_used"], ["basic", "default_colon"]
        )
        self.assertEqual(by_name["A"]["occurrences"], 2)
        self.assertEqual(analysis["required"], ["A", "D"])
        self.assertEqual(analysis["optional_with_default"], {"B": "b", "A": "a2", "E": "${F}"})
        self.assertEqual(analysis["conditionally_required"], ["C"])
        self.assertEqual(analysis["referenced_in_defaults"], ["F"])
        self.assertIn("basic", analysis["expansion_forms_exercised"])
        self.assertIn("error_colon", analysis["expansion_forms_exercised"])

    def test_analyze_empty_template(self):
        analysis = self.tool.execute(mode="analyze", template="")
        self.assertEqual(analysis["variables"], [])
        self.assertEqual(analysis["required"], [])

    # -- check_env ---------------------------------------------------- #

    def test_check_env_reports(self):
        audit = self.tool.execute(
            mode="check_env",
            template="${A} ${B:-b} ${C:?need C}",
            env={"B": "1", "EXTRA": "z"},
        )
        self.assertFalse(audit["ok"])
        self.assertEqual(
            audit["missing_required"], [{"name": "A", "forms": ["basic"]}]
        )
        self.assertEqual(
            audit["triggered_error_forms"],
            [
                {
                    "name": "C",
                    "unset_or_empty": "unset",
                    "message": "need C",
                }
            ],
        )
        self.assertEqual(audit["unused"], ["EXTRA"])

    def test_check_env_empty_var_guard_distinguishes(self):
        audit = self.tool.execute(
            mode="check_env", template="${V:?m}", env={"V": ""}
        )
        self.assertEqual(
            audit["triggered_error_forms"][0]["unset_or_empty"], "empty"
        )
        audit = self.tool.execute(
            mode="check_env", template="${V?m}", env={"V": ""}
        )
        self.assertEqual(audit["triggered_error_forms"], [])
        self.assertTrue(audit["ok"])

    def test_check_env_shadowing(self):
        audit = self.tool.execute(
            mode="check_env",
            template="${V:=default}",
            env={"V": "", "PATH": "/bin"},
        )
        kinds = {(note["kind"], note["name"]) for note in audit["shadowing"]}
        self.assertIn(("assignment_overwrites", "V"), kinds)
        self.assertIn(("reserved_name", "PATH"), kinds)

    def test_check_env_ok(self):
        audit = self.tool.execute(
            mode="check_env", template="${A} ${B:-b}", env={"A": "1"}
        )
        self.assertTrue(audit["ok"])
        self.assertEqual(audit["missing_required"], [])
        self.assertEqual(audit["unused"], [])

    # -- quote --------------------------------------------------------- #

    def test_quote_mode(self):
        result = self.tool.execute(
            mode="quote", template="it's $MODE", env={"MODE": "live"}
        )
        self.assertEqual(result["text"], "it's live")
        self.assertEqual(result["quoted"], "'it'\\''s live'")

    def test_quote_empty(self):
        result = self.tool.execute(
            mode="quote", template="${UNSET}", env={}
        )
        self.assertEqual(result["text"], "")
        self.assertEqual(result["quoted"], "''")

    # -- validation errors --------------------------------------------- #

    def assert_invalid(self, **kwargs):
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_mode_validation(self):
        self.assert_invalid(mode="nonsense", template="x", env={})
        self.assert_invalid(template="x", env={})

    def test_template_validation(self):
        self.assert_invalid(mode="expand", template=None, env={})
        self.assert_invalid(mode="expand", template=5, env={})
        self.assert_invalid(mode="expand", template="a\x00b", env={})
        self.assert_invalid(
            mode="expand", template="x" * (MAX_TEMPLATE_CHARS + 1), env={}
        )

    def test_env_validation(self):
        self.assert_invalid(mode="expand", template="x", env=None)
        self.assert_invalid(mode="expand", template="x", env=["A"])
        self.assert_invalid(mode="expand", template="x", env={"1A": "v"})
        self.assert_invalid(mode="expand", template="x", env={"A": 5})
        self.assert_invalid(mode="expand", template="x", env={"A": None})
        self.assert_invalid(mode="expand", template="x", env={"A": True})
        self.assert_invalid(mode="expand", template="x", env={"A": "v\x00"})
        self.assert_invalid(
            mode="expand", template="x", env={"A": "v" * (MAX_VALUE_CHARS + 1)}
        )
        self.assert_invalid(
            mode="expand",
            template="x",
            env={"V%d" % i: "v" for i in range(MAX_ENV_VARS + 1)},
        )

    # -- structured content errors -------------------------------------- #

    def assert_error(self, template, error_type, env=None):
        result = self.tool.execute(
            mode="expand", template=template, env=env or {}
        )
        self.assertEqual(result["error"]["type"], error_type, template)
        return result["error"]

    def test_not_supported_constructs(self):
        for template in [
            "x $(cmd) y",
            "x `cmd` y",
            "x $((1+1)) y",
            "x <(cmd) y",
            "x >(cmd) y",
            "$1", "$0", "$?", "$$", "$@", "$*", "$#", "$!",
            "${1}", "${?}", "${@}",
            "${!V}",
            "${V[0]}",
            "${V@Q}",
            "${V/a/b}",
            "${V:-$(cmd)}",
            "${V:2-3}",
            "${V:${#X}}",
        ]:
            error = self.assert_error(template, "not_supported", env={"V": "v"})
            self.assertIn("position", error)

    def test_invalid_templates(self):
        for template in [
            "${V",
            "${}",
            "${1V}",
            "${V:}",
            "${V:x}",
            "${V:1:x}",
            "${#V:2}",
            "${V:-unterminated",
            "${V%unterminated",
        ]:
            self.assert_error(template, "invalid_template", env={"V": "abcdef"})

    def test_depth_cap(self):
        inner = "${X}"
        template = "${A:-" * 7 + inner + "}" * 7
        result = self.tool.execute(mode="expand", template=template, env={})
        self.assertIn("text", result)  # depth 8 exactly: allowed
        template = "${A:-" * 8 + inner + "}" * 8
        result = self.tool.execute(mode="expand", template=template, env={})
        self.assertEqual(result["error"]["type"], "not_supported")

    # -- determinism ------------------------------------------------------ #

    def test_deterministic(self):
        template = "${A:-${B:-c}} ${A:0:2} ${A^^} $B"
        env = {"A": "aXbX", "B": ""}
        first = self.tool.execute(mode="expand", template=template, env=env)
        for _ in range(5):
            again = self.tool.execute(mode="expand", template=template, env=env)
            self.assertEqual(first, again)

    def test_direct_class_import(self):
        self.assertIs(DirectEnvsubstTool, EnvsubstTool)

    def test_yaml_exists(self):
        from agentuniverse.agent.action.tool.common_tool import (
            envsubst_tool as module,
        )

        yaml_path = os.path.join(
            os.path.dirname(module.__file__), "envsubst_tool.yaml"
        )
        self.assertTrue(os.path.isfile(yaml_path))


@unittest.skipIf(BASH is None, "no bash binary available for the oracle")
class EnvsubstBashOracleTestCase(unittest.TestCase):
    """Byte-for-byte comparisons against the real bash binary."""

    def setUp(self) -> None:
        self.tool = EnvsubstTool()

    def test_seeded_corpus_500_matches_bash(self):
        corpus = _seeded_corpus(500)
        results = bash_expand_batch(corpus)
        for (template, env), (rc, out) in zip(corpus, results):
            result = self.tool.execute(
                mode="expand", template=template, env=env
            )
            if "error" in result:
                self.assertNotEqual(
                    rc,
                    0,
                    "tool errored but bash succeeded: %r %r" % (template, env),
                )
                continue
            self.assertEqual(rc, 0, "bash failed: %r %r" % (template, env))
            self.assertEqual(
                result["text"].encode(),
                out,
                "template=%r env=%r" % (template, env),
            )

    def test_seeded_corpus_whole_template_cross_check(self):
        """Splitter-independent oracle: entire template in one dq word
        (only for cases whose literals contain no double quote or
        backslash)."""
        checked = 0
        for template, env in _seeded_corpus(120, seed=424242):
            if '"' in template or "\\" in template or "`" in template:
                continue
            result = self.tool.execute(
                mode="expand", template=template, env=env
            )
            rc, out = bash_expand(template, env, whole_template=True)
            if "error" in result:
                self.assertNotEqual(rc, 0)
                continue
            self.assertEqual(rc, 0, template)
            self.assertEqual(
                result["text"].encode(), out, "template=%r env=%r" % (template, env)
            )
            checked += 1
        self.assertGreater(checked, 40)

    def test_unset_vs_empty_battery(self):
        """Hand cases pinning :- vs - and := vs = and :+ vs + and :? vs ?,
        each verified against real bash."""
        specs = [
            (":-", "unset", "d"), ("-", "unset", "d"),
            (":=", "unset", "d"), ("=", "unset", "d"),
            (":+", "unset", ""), ("+", "unset", ""),
            (":?", "unset", None), ("?", "unset", None),
        ]
        cases = []
        for op, state, expected in specs:
            for name in ("V",):
                template = "${V%s%s}" % (op, "d" if op not in (":?", "?") else "m")
                for var_value in (None, "", "x"):
                    cases.append((template, op, state, var_value, expected))
        self.assertEqual(len(cases), 24)
        table = {}
        for template, op, _, var_value, _ in cases:
            env = {} if var_value is None else {"V": var_value}
            result = self.tool.execute(
                mode="expand", template=template, env=env
            )
            rc, out = bash_expand(template, env)
            if "error" in result:
                self.assertNotEqual(rc, 0, template)
                table[(template, var_value)] = ("ERROR", rc)
            else:
                self.assertEqual(rc, 0, template)
                self.assertEqual(
                    result["text"].encode(),
                    out,
                    "%r env=%r" % (template, env),
                )
                table[(template, var_value)] = (result["text"], rc)
        # Pin the classic distinctions explicitly.
        self.assertEqual(table[("${V:-d}", None)], ("d", 0))
        self.assertEqual(table[("${V:-d}", "")], ("d", 0))
        self.assertEqual(table[("${V:-d}", "x")], ("x", 0))
        self.assertEqual(table[("${V-d}", None)], ("d", 0))
        self.assertEqual(table[("${V-d}", "")], ("", 0))
        self.assertEqual(table[("${V-d}", "x")], ("x", 0))
        self.assertEqual(table[("${V:=d}", None)], ("d", 0))
        self.assertEqual(table[("${V=d}", "")], ("", 0))
        self.assertEqual(table[("${V:+d}", "")], ("", 0))
        self.assertEqual(table[("${V+d}", "")], ("d", 0))
        self.assertEqual(table[("${V+d}", None)], ("", 0))
        self.assertEqual(table[("${V?m}", "")][1], 0)  # ? tolerates empty
        self.assertEqual(table[("${V:?m}", "")], ("ERROR", 127))

    def test_unset_vs_empty_hand_table(self):
        """More hand-pinned expectations, each also bash-verified."""
        hand = [
            ("${V:-d}", None, "d"), ("${V:-d}", "", "d"),
            ("${V:-d}", "x", "x"),
            ("${V-d}", None, "d"), ("${V-d}", "", ""), ("${V-d}", "x", "x"),
            ("${V:=d}|${V}", None, "d|d"), ("${V=d}|${V}", "", "|"),
            ("${V:=d}|${V}", "", "d|d"),
            ("${V:+a}", None, ""), ("${V:+a}", "", ""), ("${V:+a}", "x", "a"),
            ("${V+a}", None, ""), ("${V+a}", "", "a"), ("${V+a}", "x", "a"),
            ("$V", None, ""), ("$V", "", ""), ("$V", "x", "x"),
            ("${#V}", None, "0"), ("${#V}", "", "0"), ("${#V}", "abc", "3"),
            ("${V%b*c}", None, ""), ("${V%b*c}", "abcabc", "abca"),
            ("${V:1}", None, ""), ("${V:1}", "abc", "bc"),
            ("${V^^}", None, ""), ("${V^^}", "ab", "AB"),
            ("${V:-}", None, ""), ("${V:=}", None, ""),
            ("${V:-${W:-z}}", None, "z"),
            ("${V:-$W}", None, ""), ("${V:-${W}}", None, ""),
            ("${V-d} tail", None, "d tail"),
            ("${V:- multi word}", None, " multi word"),
            ("${V:+${W:-y}}", None, ""),
            ("$V tail", None, " tail"),
            ("${V#}", None, ""), ("${V%}", None, ""),
        ]
        for template, var_value, expected in hand:
            env = {} if var_value is None else {"V": var_value}
            result = self.tool.execute(
                mode="expand", template=template, env=env
            )
            self.assertEqual(
                result["text"], expected, "%r env=%r" % (template, env)
            )
            rc, out = bash_expand(template, env)
            self.assertEqual(rc, 0, template)
            self.assertEqual(out.decode(), expected, template)

    def test_rejection_battery(self):
        """60 templates the tool must reject; each also probed in bash.

        For not_supported constructs bash may well succeed (that is
        the point: we refuse to run what bash would execute, or refuse
        parameters that have no template meaning); for invalid
        templates bash must fail too.
        """
        not_supported = [
            "echo $(id)", "$(cat /etc/passwd)", "a`id`b", "`echo x`",
            "$((1+1))", "x $((RANDOM)) y", "<(sort file)", ">(logger)",
            "cmd 2>($x)", "${V:-$(x)}", "${V:-`x`}", "${V:-$((1))}",
            "${V%$(x)}", "$1", "$2", "$0", "$9", "$?", "$$", "$!", "$@",
            "$*", "$#", "${1}", "${0}", "${10}", "${?}", "${$}", "${#}",
            "${!V}", "${!V:-d}", "${V[0]}", "${V[@]}", "${V@Q}",
            "${V/a/b}", "${V//a/b}", "${V/#a/b}", "${V/%a/b}",
            "${V:2-3}", "${V:1+1}", "${V:${#X}}", "${V:${X}}",
            "${V:-${W:-$(x)}}", "${V:-$1}", "${V:-$?}",
        ]
        invalid = [
            "${V", "${", "${V:-", "${V%", "${V%%", "${}",
            "${1V}", "${V V}", "${V:}", "${V:x}", "${V:1:x}",
            "${V:1:1:1}", "${#V:2}", "${V:-${W", "${V:x:y}",
        ]
        # bash computes (not rejects) these arithmetic-flavored specs;
        # the tool refuses arithmetic by contract (documented divergence)
        arithmetic_flavored = {
            "${V:x}", "${V:1:x}", "${V:1:1:1}", "${V:x:y}",
        }
        self.assertEqual(len(not_supported) + len(invalid), 60)
        for template in not_supported:
            result = self.tool.execute(
                mode="expand", template=template, env={"V": "v", "X": "1"}
            )
            self.assertEqual(
                result.get("error", {}).get("type"),
                "not_supported",
                template,
            )
        for template in invalid:
            result = self.tool.execute(
                mode="expand", template=template, env={"V": "v"}
            )
            self.assertEqual(
                result.get("error", {}).get("type"),
                "invalid_template",
                template,
            )
            if template in arithmetic_flavored:
                continue
            # bash rejects these too (bad substitution / EOF family)
            rc, _ = bash_expand(template, {"V": "v"})
            self.assertNotEqual(rc, 0, template)

    def test_quote_battery_200(self):
        """quote() output must reproduce the text byte-for-byte in bash."""
        rng = random.Random(99991)
        texts = [
            "", " ", "plain", "it's", 'say "hi"', "$HOME", "$(cmd)", "`x`",
            "a\\b", "line1\nline2", "héllo" if _UTF8_LOCALE else "hello",
            "*", "?", "[a-z]", "  padded  ", "'", "''", "\\", "a'b'c",
            "}'\"", "${VAR}", "$$", "%s %d", "\t", "café bar",
        ]
        alphabet = ["a", "'", '"', "\\", "$", "`", "\n", " ", "é", "*", "}", "{", "?"]
        while len(texts) < 200:
            texts.append(
                "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 12)))
            )
        for text in texts:
            quoted = "'" + text.replace("'", "'\\''") + "'"
            rc, out, _ = _run_bash("printf '%s' " + quoted, {})
            self.assertEqual(rc, 0)
            self.assertEqual(out.decode(), text, "quoted=%r" % quoted)
        # and the tool's quote mode produces exactly that form
        template = "it's ${MODE}"
        result = self.tool.execute(
            mode="quote", template=template, env={"MODE": "live"}
        )
        self.assertEqual(result["quoted"], "'it'\\''s live'")
        rc, out, _ = _run_bash(
            "printf '%s' " + result["quoted"], {"MODE": "live"}
        )
        self.assertEqual(out.decode(), "it's live")

    def test_envsubst_binary_superset_note(self):
        """The basic forms agree with GNU envsubst when it is present."""
        import shutil

        envsubst = shutil.which("envsubst")
        if not envsubst:
            self.skipTest("GNU envsubst not installed")
        for template, env in [
            ("$A-${B}", {"A": "1", "B": "2"}),
            ("x${A}y", {"A": ""}),
            ("$A$B$", {"A": "a"}),
        ]:
            proc = subprocess.run(
                [envsubst], input=template.encode(),
                env=env, capture_output=True, timeout=10,
            )
            result = self.tool.execute(
                mode="expand", template=template, env=env
            )
            self.assertEqual(result["text"].encode(), proc.stdout)


@unittest.skipIf(BASH is None, "no bash binary available for the oracle")
class EnvsubstPathologicalTestCase(unittest.TestCase):
    """Caps and performance envelopes."""

    def setUp(self) -> None:
        self.tool = EnvsubstTool()

    def test_megabyte_template_under_2s(self):
        chunk = "x" * 1024 * 1024  # 1 MiB literal
        template = chunk + "${A:-d}" + chunk[:1000]
        start = time.monotonic()
        result = self.tool.execute(
            mode="expand", template=template, env={}
        )
        elapsed = time.monotonic() - start
        self.assertEqual(result["text"], chunk + "d" + chunk[:1000])
        self.assertLess(elapsed, 2.0, "1MiB template took %.2fs" % elapsed)

    def test_10k_variable_mapping(self):
        env = {"V%04d" % i: "val%d" % i for i in range(10_000)}
        template = " ".join("${V%04d:-x}" % i for i in range(0, 10_000, 10))
        start = time.monotonic()
        result = self.tool.execute(
            mode="expand", template=template, env=env
        )
        elapsed = time.monotonic() - start
        self.assertEqual(
            result["text"], " ".join("val%d" % i for i in range(0, 10_000, 10))
        )
        self.assertLess(elapsed, 10.0)

    def test_10k_expansion_references(self):
        template = "$A" * 10_000
        result = self.tool.execute(
            mode="expand", template=template, env={"A": "z"}
        )
        self.assertEqual(result["text"], "z" * 10_000)
        self.assertEqual(len(result["expanded"]), 1)

    def test_pattern_on_large_value(self):
        value = "a" * 99_999 + "b"
        result = self.tool.execute(
            mode="expand", template="${V%%a*b}", env={"V": value}
        )
        self.assertEqual(result["text"], "")
        result = self.tool.execute(
            mode="expand", template="${V%a*b}", env={"V": value}
        )
        self.assertEqual(result["text"], "a" * 99_998)  # shortest "ab"

    def test_caps_rejected_quickly(self):
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="expand", template="x" * (MAX_TEMPLATE_CHARS + 1), env={}
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="expand",
                template="x",
                env={"V%d" % i: "v" for i in range(MAX_ENV_VARS + 1)},
            )

    def test_deep_nesting_rejected_at_cap(self):
        inner = "${X}"
        template = "${A:-" * 9 + inner + "}" * 9
        result = self.tool.execute(mode="expand", template=template, env={})
        self.assertEqual(result["error"]["type"], "not_supported")
        self.assertIn("nesting", result["error"]["message"])


class EnvsubstScannerUnitTestCase(unittest.TestCase):
    """Pin the scanner's splitting rules via the parser directly."""

    def test_split_sources(self):
        nodes = _Parser("a${B:-c}d$E f").parse()
        sources = [payload["source"] for k, payload in nodes if k == "ref"]
        lits = [payload for k, payload in nodes if k == "lit"]
        self.assertEqual(sources, ["${B:-c}", "$E"])
        self.assertEqual(lits, ["a", "d", " f"])

    def test_bare_name_absorbs(self):
        nodes = _Parser("$Asay tail").parse()
        self.assertEqual(nodes[0][1]["name"], "Asay")

    def test_dollar_brace_in_literal(self):
        nodes = _Parser("} { $ notanexp").parse()
        self.assertEqual(nodes[0][1], "} { $ notanexp")

    def test_scanner_errors_carry_positions(self):
        with self.assertRaises(_TemplateError) as ctx:
            _Parser("abc ${V:-d").parse()
        self.assertEqual(ctx.exception.kind, "invalid")
        self.assertEqual(ctx.exception.position, 4)  # the '$' of the form


if __name__ == "__main__":
    unittest.main()

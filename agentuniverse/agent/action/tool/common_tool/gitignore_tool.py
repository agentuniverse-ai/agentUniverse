#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: gitignore_tool.py

r"""Gitignore rule semantics: pattern matching, rule hygiene
analysis, linting and explanation — pure Python stdlib, no
subprocess, no filesystem access, no network.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) at the **ignore-rule layer**: agents that review
generated .gitignore files, debug "why is git ignoring (or not
ignoring) this file" reports, or sanitize ignore rule sets need to
ask gitignore-shaped questions — "is this path ignored by these
rules, and by which rule exactly?", "which of my negation rules
are silently dead?", "what does this ``**`` actually do?". This
tool answers them with a faithful re-implementation of git's own
matching pipeline, not an approximation.

The algorithm is hand-embedded from the git sources (``wildmatch.c``
``dowild`` — the pattern matcher behind gitignore; ``dir.c``
``add_patterns_from_buffer`` / ``trim_trailing_spaces`` /
``parse_path_pattern`` / ``match_basename`` / ``match_pathname`` /
``last_matching_pattern_from_list`` / the ``prep_exclude``
leading-directory walk; ``builtin/check-ignore.c``) and from
gitignore(5). Matching runs on UTF-8 **bytes**, exactly like git's
8-bit-clean wildmatch — so ``?`` matches one byte, character-class
ranges compare byte values, and case is significant
(``core.ignoreCase=false`` is the documented default here). The
test suite pins parity against the REAL ``git`` binary via
``git check-ignore -v --no-index`` on hundreds of seeded
(ruleset, path) pairs; the runtime never invokes git.

Four modes:

* ``match`` — ``rules`` (gitignore syntax: ``#`` comments, blank
  lines, trailing-space handling — unescaped trailing spaces are
  ignored, ``\ `` keeps a literal space — per gitignore(5)) plus a
  relative ``path`` into the decisive-rule verdict:
  ``{matched, rule_index, rule_line, rule_text, negated,
  effective, matched_on, matched_directory, matching_rules,
  explanation}``. ``effective`` is the ignore verdict AFTER
  negation resolution. The pipeline mirrors ``git check-ignore``:
  each leading directory of the path is checked as a directory
  (an ignored directory kills its whole subtree — negations below
  it are dead, the classic ``doc/`` + ``!doc/readme.md`` trap);
  otherwise the LAST matching rule for the full path wins
  (gitignore(5): "the last matching pattern decides the outcome").
* ``analyze`` — ``rules`` into rule-set hygiene:
  ``rule_count``, ``dead_rules`` (each with ``blocked_by`` and a
  reason — reachability is computed honestly per
  last-match-wins: an identical later rule shadows an earlier one;
  a later rule whose pattern provably covers every path a negation
  matches kills that negation; a negation whose every match lies
  inside a provably ignored directory is dead because git never
  descends into ignored directories), ``contradictions``
  (identical patterns with opposite polarity that fight),
  ``duplicates``, ``trailing_space_traps`` (rules silently
  weakened because git drops unescaped trailing spaces),
  ``missing_final_newline`` (git still honors the final line — the
  reader appends a virtual newline — but POSIX text conventions
  and third-party parsers may not), ``any_depth_patterns``
  (slash-free patterns match at ANY depth — info only, the user
  may have wanted a ``/``-anchored rule), and ``escaping_errors``
  (dangling backslashes, escaped trailing spaces, escapes of
  ordinary characters — the Windows path-separator mistake).
* ``lint`` — ``rules`` into ordered findings
  ``{line, code, message, severity}`` covering invalid globs
  (unterminated ``[`` classes, empty ``[]``, malformed
  ``[:posix:]`` names — each makes the pattern dead in git's
  matcher), never-matching patterns (dangling trailing backslash,
  empty interior segments ``a//b``, empty pattern), reversed
  character ranges (``[z-a]`` — the range can never match
  anything), redundant ``**`` (consecutive stars outside the three
  special positions — leading ``**/``, trailing ``/**``, middle
  ``/**/`` — behave as a single ``*``, verified against real
  git), duplicate rules and duplicate negations, the ``/**/``
  matches-zero-or-more-directories semantics note, and Windows
  path-separator mistakes (``\`` is an escape in gitignore, so
  ``build\temp`` matches a file literally named ``buildtemp``).
* ``explain`` — one ``rule`` into its structure:
  ``{negated, anchored, dir_only, segments ([{kind: literal /
  wildcard / doublestar / class / negation, text, matches}]),
  example_matches (3 deterministic, verified with the matcher),
  example_misses (2, likewise verified non-matches)}``.

Semantics guaranteed (each pinned against the real git binary in
the test suite): a leading ``/`` anchors to the .gitignore's own
directory; a trailing ``/`` restricts a rule to directories; a
pattern containing a ``/`` anywhere else is anchored too, while a
slash-free pattern matches its basename at any depth; ``*`` never
crosses ``/`` and ``?`` never matches ``/``; ``**`` is special
only as leading ``**/``, trailing ``/**`` and middle ``/**/``
(where it matches zero or more directories — ``a/**/b`` matches
``a/b``); ``[abc]`` classes support ranges, ``!``/``^`` negation,
backslash escapes and the POSIX ``[:alpha:]`` family, and never
match ``/``; ``\`` escapes any character; ``#`` starts a comment
unless escaped; a leading ``!`` negates unless escaped; unescaped
trailing spaces are dropped, ``\ `` keeps one; CRLF line endings
and a UTF-8 BOM are handled like git handles them.

Determinism: fixed scan orders, bounded detail lists, at most one
finding per code per rule line — the same input always yields
byte-identical output.

Input validation is strict and happens before any work: wrong
parameter types raise ``ValueError`` (echoed values are truncated
to a bounded preview); ``rules`` is capped at ``max_rules_chars``
characters (default 65,536) and ``max_rule_lines`` lines (default
4,096 — both real overridable fields on the tool instance);
``path`` must be relative, slash-separated, 1-``max_path_chars``
characters with at most ``max_path_segments`` components, without
empty / ``.`` / ``..`` components or backslashes (one trailing
``/`` is allowed and asserts a directory, mirroring the
check-ignore CLI; an explicit ``is_dir`` argument overrides).

Division of labor inside the family (see the Distinction section
of the PR): **PathLintTool** (#4036) lints the *path string* for
cross-platform portability; this tool implements *git ignore-rule
semantics* — negation ordering, directory-only rules, anchoring,
``**`` behavior and rule-set reachability — a layer no other
integrated tool covers.
"""

from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict, Field

from agentuniverse.agent.action.tool.tool import Tool

# ------------------------------------------------------------------ #
# Limits (reject pathological inputs before any work)
# ------------------------------------------------------------------ #

_MAX_RULES_CHARS = 65_536
_MAX_RULE_LINES = 4_096
_MAX_PATH_CHARS = 4_096
_MAX_PATH_SEGMENTS = 64
_MAX_RULE_CHARS = 1_024
# How many list entries findings/messages echo before switching
# to a bounded "+k more" (bounded output).
_DETAIL_LIMIT = 12
_MATCH_LIST_LIMIT = 32
# Cap on the character set computed for a simple class (covers
# lattice + explain examples stay bounded and fast).
_MAX_CLASS_CHARS = 1_024

# Characters for which a backslash escape is meaningful.
_SPECIAL_ESCAPE = frozenset("*?[]!#\\/ ")
# The POSIX class names wildmatch.c knows.
_POSIX_CLASSES = frozenset(
    {"alnum", "alpha", "blank", "cntrl", "digit", "graph", "lower",
     "print", "punct", "space", "upper", "xdigit"}
)

# ------------------------------------------------------------------ #
# wildmatch translation — git's wildmatch.c dowild(), run on
# UTF-8 bytes exactly like git's 8-bit-clean C matcher.
# ------------------------------------------------------------------ #

_WM_MATCH = 0
_WM_NOMATCH = 1
_WM_ABORT_ALL = -1
_WM_ABORT_TO_STARSTAR = -2

_GLOB_SPECIAL = frozenset(b"*?[\\")


def _posix_class_member(name: str, byte: int) -> bool:
    """POSIX class membership with wildmatch.c's ASCII-only ctypes."""
    c = chr(byte)
    if not c.isascii():
        return False
    if name == "alnum":
        return c.isalnum()
    if name == "alpha":
        return c.isalpha()
    if name == "blank":
        return c in (" ", "\t")
    if name == "cntrl":
        return ord(c) < 32 or ord(c) == 127
    if name == "digit":
        return c.isdigit()
    if name == "graph":
        return c.isprintable() and not c.isspace()
    if name == "lower":
        return c.islower()
    if name == "print":
        return c.isprintable()
    if name == "punct":
        return c.isprintable() and not c.isalnum() and not c.isspace()
    if name == "space":
        return c.isspace()
    if name == "upper":
        return c.isupper()
    if name == "xdigit":
        return c in "0123456789abcdefABCDEF"
    raise KeyError(name)


def _dowild(pat: bytes, pi: int, text: bytes, ti: int, pathname: bool) -> int:
    """Python translation of git wildmatch.c dowild() (no casefold).

    ``pat``/``text`` are UTF-8 byte strings; ``pi``/``ti`` are the
    current indices. Returns one of the four WM_* codes.
    """
    plen = len(pat)
    tlen = len(text)
    while pi < plen:
        p_ch = pat[pi]
        t_ch = text[ti] if ti < tlen else -1  # -1 stands for C NUL
        if t_ch == -1 and p_ch != ord("*"):
            return _WM_ABORT_ALL
        if p_ch == ord("\\"):
            # Literal match with the following character.
            pi += 1
            p_ch = pat[pi] if pi < plen else -1
            if t_ch != p_ch:
                return _WM_NOMATCH
            pi += 1
            ti += 1
            continue
        if p_ch == ord("?"):
            # Match anything but '/' under WM_PATHNAME.
            if pathname and t_ch == ord("/"):
                return _WM_NOMATCH
            pi += 1
            ti += 1
            continue
        if p_ch == ord("*"):
            pi += 1
            if pi < plen and pat[pi] == ord("*"):
                prev_index = pi  # index of the SECOND star of the run
                pi += 1
                while pi < plen and pat[pi] == ord("*"):
                    pi += 1
                if not pathname:
                    match_slash = True
                else:
                    prev_ok = prev_index < 2 or pat[prev_index - 2] == ord("/")
                    cur = pat[pi] if pi < plen else -1
                    nxt = pat[pi + 1] if pi + 1 < plen else -1
                    after_ok = (
                        cur == -1
                        or cur == ord("/")
                        or (cur == ord("\\") and nxt == ord("/"))
                    )
                    if prev_ok and after_ok:
                        # '/**/' also matches zero directories.
                        if cur == ord("/"):
                            if _dowild(pat, pi + 1, text, ti, pathname) == _WM_MATCH:
                                return _WM_MATCH
                        match_slash = True
                    else:
                        match_slash = False
            else:
                match_slash = not pathname
            if pi >= plen:
                # Trailing '**' matches everything; trailing '*'
                # only when no slash remains.
                if not match_slash and b"/" in text[ti:]:
                    return _WM_ABORT_TO_STARSTAR
                return _WM_MATCH
            if not match_slash and pat[pi] == ord("/"):
                # One '*' followed by '/' consumes text up to the
                # next '/' (the slash itself by the loop increment).
                slash = text.find(b"/", ti)
                if slash == -1:
                    return _WM_ABORT_ALL
                ti = slash
                pi += 1
                ti += 1
                continue
            while True:
                if t_ch == -1:
                    break
                if pat[pi] not in _GLOB_SPECIAL:
                    lit = pat[pi]
                    # Skip ahead to the next occurrence of the
                    # literal (a single '*' never matches '/').
                    while t_ch != -1 and (match_slash or t_ch != ord("/")):
                        if t_ch == lit:
                            break
                        ti += 1
                        t_ch = text[ti] if ti < tlen else -1
                    if t_ch != lit:
                        return _WM_ABORT_ALL if match_slash else _WM_ABORT_TO_STARSTAR
                matched = _dowild(pat, pi, text, ti, pathname)
                if matched != _WM_NOMATCH:
                    if not match_slash or matched != _WM_ABORT_TO_STARSTAR:
                        return matched
                elif not match_slash and t_ch == ord("/"):
                    return _WM_ABORT_TO_STARSTAR
                ti += 1
                t_ch = text[ti] if ti < tlen else -1
            return _WM_ABORT_ALL
        if p_ch == ord("["):
            pi += 1
            p_ch = pat[pi] if pi < plen else -1
            if p_ch == ord("^"):
                p_ch = ord("!")
            negated = p_ch == ord("!")
            if negated:
                pi += 1
                p_ch = pat[pi] if pi < plen else -1
            prev_ch = 0  # C's 0 means "no previous character"
            matched = False
            while True:  # C do-while over the class items
                if p_ch == -1:
                    return _WM_ABORT_ALL
                if p_ch == ord("\\"):
                    pi += 1
                    p_ch = pat[pi] if pi < plen else -1
                    if p_ch == -1:
                        return _WM_ABORT_ALL
                    if t_ch == p_ch:
                        matched = True
                elif (
                    p_ch == ord("-")
                    and prev_ch != 0
                    and pi + 1 < plen
                    and pat[pi + 1] != ord("]")
                ):
                    pi += 1
                    p_ch = pat[pi]
                    if p_ch == ord("\\"):
                        pi += 1
                        p_ch = pat[pi] if pi < plen else -1
                        if p_ch == -1:
                            return _WM_ABORT_ALL
                    if t_ch != -1 and t_ch <= p_ch and t_ch >= prev_ch:
                        matched = True
                    p_ch = 0  # resets prev_ch on the next tick
                elif p_ch == ord("[") and pi + 1 < plen and pat[pi + 1] == ord(":"):
                    s = pi + 2
                    p2 = s
                    while p2 < plen and pat[p2] != ord("]"):
                        p2 += 1
                    if p2 >= plen:
                        return _WM_ABORT_ALL
                    if p2 - 1 < s or pat[p2 - 1] != ord(":"):
                        # No ':]' — treat like a normal set.
                        pi = s - 2
                        p_ch = ord("[")
                        if t_ch == p_ch:
                            matched = True
                    else:
                        name = pat[s:p2 - 1].decode("latin-1")
                        if name not in _POSIX_CLASSES:
                            return _WM_ABORT_ALL  # malformed [:name:]
                        if t_ch != -1 and _posix_class_member(name, t_ch):
                            matched = True
                        pi = p2
                        p_ch = 0
                elif t_ch == p_ch:
                    matched = True
                # C label 'next:'
                prev_ch = p_ch
                pi += 1
                p_ch = pat[pi] if pi < plen else -1
                if p_ch == ord("]"):
                    break
            if matched == negated or (pathname and t_ch == ord("/")):
                return _WM_NOMATCH
            pi += 1
            ti += 1
            continue
        # default: literal character comparison (byte values)
        if t_ch != p_ch:
            return _WM_NOMATCH
        pi += 1
        ti += 1
    return _WM_MATCH if ti >= tlen else _WM_NOMATCH


def _wildmatch(pattern: str, text: str, pathname: bool) -> bool:
    """wildmatch(pattern, text, WM_PATHNAME?) == WM_MATCH (no fold)."""
    return (
        _dowild(pattern.encode("utf-8"), 0, text.encode("utf-8"), 0, pathname)
        == _WM_MATCH
    )


# ------------------------------------------------------------------ #
# Rule parsing — dir.c add_patterns_from_buffer() +
# trim_trailing_spaces() + parse_path_pattern(), mirrored.
# ------------------------------------------------------------------ #


def _trim_trailing_spaces(s: str) -> str:
    """dir.c trim_trailing_spaces(): drop unescaped trailing ' '.

    A trailing backslash aborts the scan (the string is returned
    untrimmed); a backslash-escaped character resets the trailing
    space marker, so 'foo\\ ' keeps its (escaped) space.
    """
    last_space = -1
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == " ":
            if last_space < 0:
                last_space = i
        elif c == "\\":
            i += 1
            if i >= n:
                return s  # dangling backslash: no trimming at all
            last_space = -1
        else:
            last_space = -1
        i += 1
    if last_space >= 0:
        return s[:last_space]
    return s


class _Rule:
    """One parsed gitignore rule (a non-comment, non-blank line)."""

    __slots__ = (
        "index",
        "line",
        "source",
        "raw_line",
        "negated",
        "mustbedir",
        "core",
        "match_pat",
        "nodir",
        "space_trimmed",
    )

    def __init__(self, index: int, line: int, raw_line: str, source: str) -> None:
        self.index = index
        self.line = line
        self.raw_line = raw_line
        self.source = source  # trimmed rule text, as git stores it
        core = source
        negated = False
        if core.startswith("!"):
            negated = True
            core = core[1:]
        mustbedir = False
        if core.endswith("/"):
            mustbedir = True
            core = core[:-1]
        self.negated = negated
        self.mustbedir = mustbedir
        self.core = core  # after '!' and trailing '/' handling
        self.match_pat = core[1:] if core.startswith("/") else core
        self.nodir = "/" not in core
        self.space_trimmed = source != raw_line


def _parse_rules(text: str) -> List[_Rule]:
    """Parse rules text exactly like git reads a .gitignore file.

    Mirrors the reader appending a virtual trailing newline, the
    UTF-8 BOM skip, the CRLF strip of a '\\r' directly before the
    newline, the '#'-comment skip, trim_trailing_spaces, and
    parse_path_pattern. Blank lines produce no rule; a spaces-only
    line produces an (unmatchable) empty rule, exactly like git.
    """
    buf = text
    if buf.startswith("\ufeff"):
        buf = buf[1:]
    if not buf.endswith("\n"):
        buf += "\n"
    rules: List[_Rule] = []
    lineno = 1
    entry = 0
    for i, ch in enumerate(buf):
        if ch != "\n":
            continue
        raw = buf[entry:i]
        if i > 0 and buf[i - 1] == "\r":
            raw = raw[:-1]
        if raw and not raw.startswith("#"):
            trimmed = _trim_trailing_spaces(raw)
            rules.append(_Rule(len(rules), lineno, raw, trimmed))
        lineno += 1
        entry = i + 1
    return rules


# ------------------------------------------------------------------ #
# Matching — dir.c match_basename()/match_pathname() +
# last_matching_pattern_from_list() + the prep_exclude()
# leading-directory walk, mirroring builtin/check-ignore.c.
# ------------------------------------------------------------------ #


def _rule_matches(rule: _Rule, path: str, is_dir: bool) -> bool:
    """Would this rule match ``path`` (a normalized relative path)?

    ``is_dir`` mirrors the dtype resolution check-ignore performs
    (MUSTBEDIR rules only apply to directories). Slash-free rules
    match the basename at any depth, exactly like match_basename();
    slash-bearing rules are anchored to the .gitignore's directory
    (match_pathname() strips the single leading '/').
    """
    if rule.mustbedir and not is_dir:
        return False
    if rule.nodir:
        basename = path.rsplit("/", 1)[-1]
        return _wildmatch(rule.core, basename, pathname=False)
    return _wildmatch(rule.match_pat, path, pathname=True)


class _Verdict:
    """Decisive result, mirroring check-ignore's reporting."""

    __slots__ = ("rule", "via", "directory")

    def __init__(self, rule: _Rule, via: str, directory: Optional[str]) -> None:
        self.rule = rule
        self.via = via  # "path" or "directory"
        self.directory = directory


def _check_ignore(rules: List[_Rule], path: str, is_dir: bool) -> Optional[_Verdict]:
    """The check-ignore pipeline: leading-directory walk, then the
    last matching rule for the full path.

    * Each leading directory is checked as a directory; a
      non-negated last match kills the whole subtree (git never
      descends into ignored directories — negations below it are
      dead). A negated match merely un-ignores that directory and
      the walk continues.
    * Otherwise the LAST rule matching the full path decides; a
      negation makes the path not-ignored.
    """
    components = path.split("/")
    for k in range(1, len(components)):
        directory = "/".join(components[:k])
        for rule in reversed(rules):
            if _rule_matches(rule, directory, True):
                if not rule.negated:
                    return _Verdict(rule, "directory", directory)
                break  # un-ignored at this level: keep walking
    for rule in reversed(rules):
        if _rule_matches(rule, path, is_dir):
            return _Verdict(rule, "path", None)
    return None


# ------------------------------------------------------------------ #
# Structural scans (lint / analyze / explain helpers)
# ------------------------------------------------------------------ #


class _ClassFacts:
    __slots__ = ("start", "unterminated", "bad_posix", "reversed_ranges")

    def __init__(self, start: int) -> None:
        self.start = start
        self.unterminated = False
        self.bad_posix = False
        self.reversed_ranges: List[str] = []


def _scan_rule(core: str) -> Dict[str, Any]:
    """Left-to-right structural scan of a rule's match pattern.

    Returns the facts used by lint/analyze: star runs with their
    wildmatch specialness, character-class facts, escapes, a
    dangling backslash, and empty path segments.
    """
    facts: Dict[str, Any] = {
        "star_runs": [],  # {start, end, special}
        "classes": [],  # _ClassFacts
        "escapes": [],  # (index, escaped_char)
        "dangling_backslash": False,
        "escaped_space_end": False,
        "empty_segment": False,
        "mid_doublestar_slash": False,  # '/**/' present
        "segments": [],
    }
    n = len(core)
    segments: List[str] = []
    cur = []
    i = 0
    while i < n:
        c = core[i]
        if c == "\\":
            if i + 1 >= n:
                facts["dangling_backslash"] = True
                i += 1
                continue
            nxt = core[i + 1]
            facts["escapes"].append((i, nxt))
            if nxt == " " and i + 2 >= n:
                facts["escaped_space_end"] = True
            cur.append(core[i : i + 2])
            i += 2
            continue
        if c == "*":
            j = i
            while j < n and core[j] == "*":
                j += 1
            run_len = j - i
            prev_ok = i == 0 or core[i - 1] == "/"
            k = j
            after = core[k] if k < n else ""
            after_ok = after == "" or after == "/" or (
                after == "\\" and k + 1 < n and core[k + 1] == "/"
            )
            if run_len >= 2:
                facts["star_runs"].append(
                    {"start": i, "end": j, "special": prev_ok and after_ok}
                )
                if prev_ok and after == "/" and i > 0:
                    facts["mid_doublestar_slash"] = True
            cur.append(core[i:j])
            i = j
            continue
        if c == "[":
            cf = _ClassFacts(i)
            pi = i + 1
            if pi < n and core[pi] in "!^":
                pi += 1
            prev: Optional[str] = None
            closed = False
            while pi < n:
                pc = core[pi]
                if pc == "\\":
                    if pi + 1 >= n:
                        break
                    pi += 2
                    prev = "x"
                    continue
                if (
                    pc == "-"
                    and prev is not None
                    and pi + 1 < n
                    and core[pi + 1] != "]"
                ):
                    hi = core[pi + 1]
                    if hi == "\\":
                        hi = core[pi + 2] if pi + 2 < n else ""
                    if hi and ord(hi) < ord(prev):
                        cf.reversed_ranges.append(f"{prev}-{hi}")
                    prev = None
                    pi += 2
                    continue
                if pc == "[" and pi + 1 < n and core[pi + 1] == ":":
                    s = pi + 2
                    p2 = s
                    while p2 < n and core[p2] != "]":
                        p2 += 1
                    if p2 >= n:
                        break  # matcher aborts: class never closes
                    if p2 - 1 >= s and core[p2 - 1] == ":":
                        name = core[s:p2 - 1]
                        if name not in _POSIX_CLASSES:
                            cf.bad_posix = True
                        pi = p2 + 1
                        prev = None
                        continue
                    # no ':]': the '[' is an ordinary item
                    prev = "["
                    pi += 1
                    continue
                if pc == "]":
                    closed = True
                    pi += 1
                    break
                prev = pc
                pi += 1
            cf.unterminated = not closed
            facts["classes"].append(cf)
            i = pi
            continue
        if c == "/":
            segments.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    segments.append("".join(cur))
    facts["segments"] = segments
    if any(s == "" for s in segments) and len(segments) > 1:
        facts["empty_segment"] = True
    return facts


# ------------------------------------------------------------------ #
# Pattern cover lattice — a sound sufficient condition for
# "rule Q matches every path rule P matches" (used to prove dead
# negations honestly, per last-match-wins).
# ------------------------------------------------------------------ #


def _split_unescaped(s: str) -> List[str]:
    """Split on unescaped '/' (a '\\/' pair stays inside a part)."""
    parts: List[str] = []
    cur: List[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            cur.append(s[i : i + 2])
            i += 2
            continue
        if c == "/":
            parts.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    parts.append("".join(cur))
    return parts


def _class_extent(segment: str, start: int) -> Optional[int]:
    """Index just past the closing ']' of the class opening at
    ``start``, mirroring the matcher's class walk (POSIX
    '[:name:]' groups, escapes, ranges); None when unterminated."""
    n = len(segment)
    pi = start + 1
    if pi < n and segment[pi] in "!^":
        pi += 1
    prev = 0
    while pi < n:
        c = segment[pi]
        if c == "\\":
            if pi + 1 >= n:
                return None
            pi += 2
            prev = 1
            continue
        if c == "-" and prev and pi + 1 < n and segment[pi + 1] != "]":
            pi += 2
            prev = 0
            continue
        if c == "[" and pi + 1 < n and segment[pi + 1] == ":":
            s = pi + 2
            p2 = s
            while p2 < n and segment[p2] != "]":
                p2 += 1
            if p2 >= n:
                return None
            if p2 - 1 >= s and segment[p2 - 1] == ":":
                pi = p2 + 1
                prev = 0
                continue
            pi += 1  # ordinary '[' item
            prev = 2
            continue
        if c == "]":
            return pi + 1
        prev = 3
        pi += 1
    return None


def _segment_atoms(segment: str) -> Optional[List[Tuple[str, str]]]:
    """Tokenize a segment into (kind, text) atoms.

    kind: 'literal' (escape-normalized), 'star' (a whole '*' run),
    'question', 'class' (text includes the brackets). Returns None
    when the segment is dead (unterminated class or dangling
    backslash) — the cover question is then moot.
    """
    atoms: List[Tuple[str, str]] = []
    lit: List[str] = []
    i = 0
    n = len(segment)

    def flush() -> None:
        if lit:
            atoms.append(("literal", "".join(lit)))
            del lit[:]

    while i < n:
        c = segment[i]
        if c == "\\":
            if i + 1 >= n:
                return None  # dangling backslash: dead pattern
            lit.append(segment[i + 1])
            i += 2
            continue
        if c == "*":
            flush()
            j = i
            while j < n and segment[j] == "*":
                j += 1
            atoms.append(("star", segment[i:j]))
            i = j
            continue
        if c == "?":
            flush()
            atoms.append(("question", "?"))
            i += 1
            continue
        if c == "[":
            extent = _class_extent(segment, i)
            if extent is None:
                return None  # unterminated class: dead pattern
            flush()
            atoms.append(("class", segment[i:extent]))
            i = extent
            continue
        lit.append(c)
        i += 1
    flush()
    return atoms


class _SimpleClass:
    """Members of a simple '[...]' class (no POSIX classes)."""

    __slots__ = ("negated", "items")

    def __init__(self, negated: bool, items: frozenset) -> None:
        self.negated = negated
        self.items = items


def _class_chars(text: str) -> Optional[_SimpleClass]:
    """Compute a class's character set; None when not computable
    (POSIX class, escape-terminated body, reversed range or an
    oversized set)."""
    body = text[1:-1] if text.startswith("[") else text
    negated = body.startswith("!") or body.startswith("^")
    if negated:
        body = body[1:]
    items: set = set()
    last: Optional[str] = None
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            if i + 1 >= len(body):
                return None
            last = body[i + 1]
            items.add(last)
            i += 2
            continue
        if c == "-" and last is not None and i + 1 < len(body) and body[i + 1] != "]":
            hi = body[i + 1]
            if hi == "\\":
                if i + 2 >= len(body):
                    return None
                hi = body[i + 2]
                i += 1
            if ord(hi) < ord(last):
                return None  # reversed range: not computable
            for o in range(ord(last), ord(hi) + 1):
                items.add(chr(o))
            if len(items) > _MAX_CLASS_CHARS:
                return None
            last = None
            i += 2
            continue
        if c == "[" and i + 1 < len(body) and body[i + 1] == ":":
            return None  # POSIX class: keep it simple
        last = c
        items.add(c)
        i += 1
    if len(items) > _MAX_CLASS_CHARS:
        return None
    return _SimpleClass(negated, frozenset(items))


def _atom_covers(q_atom: Tuple[str, str], p_atom: Tuple[str, str]) -> bool:
    """Does atom q (from the covering rule) match everything atom p does?"""
    qk, qt = q_atom
    pk, pt = p_atom
    if qk == "star":
        return True  # a star run covers its whole segment part
    if qk == "literal":
        return pk == "literal" and qt == pt
    if qk == "question":
        return (pk == "literal" and len(pt) == 1) or pk == "question"
    if qk == "class":
        qc = _class_chars(qt)
        if qc is None or qc.negated:
            return False
        if pk == "literal":
            return pt in qc.items
        if pk == "question":
            return True  # exactly one character, in the class
        if pk == "class":
            pc = _class_chars(pt)
            if pc is None or pc.negated:
                return False
            return pc.items <= qc.items
    return False


_DOUBLESTAR = ("doublestar", "**")


def _norm_seg(seg: Optional[List[Tuple[str, str]]]) -> Optional[List[Tuple[str, str]]]:
    """Mark a segment that is exactly a '**' run as a doublestar."""
    if seg is None:
        return None
    if len(seg) == 1 and seg[0][0] == "star" and len(seg[0][1]) >= 2:
        return [_DOUBLESTAR]
    return seg


def _segments_cover(q_segs: List[Optional[List[Tuple[str, str]]]],
                    p_segs: List[Optional[List[Tuple[str, str]]]]) -> bool:
    """Aligned segment cover: every p-segment is covered by q's
    atoms, with q's '**' segments allowed to absorb p-segments
    (a trailing '/**' absorbs at least one segment; leading and
    middle '**' absorb zero or more — mirroring wildmatch)."""

    def cover_at(qi: int, pi: int) -> bool:
        if pi >= len(p_segs):
            # p is exhausted: q must be too (a remaining trailing
            # '**' would demand at least one more segment).
            return qi >= len(q_segs)
        if qi >= len(q_segs):
            return False  # q exhausted while p has segments left
        q_seg = q_segs[qi]
        p_seg = p_segs[pi]
        if q_seg == [_DOUBLESTAR]:
            for skip in range(0, len(p_segs) - pi + 1):
                if cover_at(qi + 1, pi + skip):
                    return True
            return False
        if p_seg == [_DOUBLESTAR]:
            # p matches at any depth here: only q's own '**' can
            # cover that (handled above) — a plain segment cannot.
            return False
        if q_seg is None or p_seg is None:
            return False
        if (
            len(p_seg) == 1
            and p_seg[0][0] == "literal"
            and any(a[0] in ("star", "question", "class") for a in q_seg)
        ):
            # p's match set at this position is exactly one fixed
            # string: q covers it iff q matches that string.
            q_text = "".join(text for _, text in q_seg)
            if _wildmatch(q_text, p_seg[0][1], pathname=False):
                return cover_at(qi + 1, pi + 1)
            return False
        if len(q_seg) != len(p_seg):
            return False
        if not all(_atom_covers(q, p) for q, p in zip(q_seg, p_seg)):
            return False
        return cover_at(qi + 1, pi + 1)

    return cover_at(0, 0)


def _rule_covers(candidate: _Rule, target: _Rule) -> bool:
    """Sound sufficient check: does ``candidate`` match every path
    ``target`` matches (dtype-compatibly)?

    Normalizes slash-free (NODIR) rules to a synthetic leading
    '**' segment (provably equivalent: they match the basename at
    any depth). MUSTBEDIR handling: a mustbedir candidate covers a
    mustbedir target; a dtype-agnostic candidate covers both; a
    mustbedir candidate never covers a plain target.
    """
    if candidate.mustbedir and not target.mustbedir:
        return False
    t_core = target.match_pat
    c_core = candidate.match_pat
    if not t_core or not c_core:
        return False
    t_segs = [_segment_atoms(p) for p in _split_unescaped(t_core)]
    c_segs = [_segment_atoms(p) for p in _split_unescaped(c_core)]
    if any(s is None for s in t_segs) or any(s is None for s in c_segs):
        return False
    if target.nodir:
        t_segs = [[_DOUBLESTAR]] + t_segs
    if candidate.nodir:
        c_segs = [[_DOUBLESTAR]] + c_segs
    t_norm = [_norm_seg(s) for s in t_segs]
    c_norm = [_norm_seg(s) for s in c_segs]
    return _segments_cover(c_norm, t_norm)


# ------------------------------------------------------------------ #
# The tool
# ------------------------------------------------------------------ #


def _rule_ref(rule: _Rule) -> Dict[str, Any]:
    return {
        "index": rule.index,
        "line": rule.line,
        "rule": rule.source,
        "negated": rule.negated,
        "dir_only": rule.mustbedir,
    }


def _preview(value: Any) -> str:
    """Bounded echo of a wrong-typed argument."""
    try:
        text = repr(value)
    except Exception:
        text = "<unrepresentable>"
    if len(text) > 60:
        text = text[:57] + "..."
    return f"{type(value).__name__} {text}"


class GitignoreTool(Tool):
    """Gitignore rule semantics: match, analyze, lint and explain.

    Attributes:
        max_rules_chars (int): Upper bound on the rules text
            (default 65,536; overridable per instance).
        max_rule_lines (int): Upper bound on rule text lines
            (default 4,096).
        max_path_chars (int): Upper bound on the match path
            (default 4,096).
        max_path_segments (int): Upper bound on path components
            (default 64).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "gitignore_tool"
    description: str = (
        "Gitignore rule semantics on the pure Python stdlib — no "
        "subprocess, no filesystem access, no network; the "
        "matching algorithm is a faithful translation of git's "
        "wildmatch/dir.c pipeline (pinned against the real git "
        "binary in tests). Match a path against rules "
        "(mode='match': {matched, rule_index, rule_line, "
        "rule_text, negated, effective, matched_on, "
        "matched_directory, matching_rules, explanation} — "
        "leading-directory walk: an ignored directory kills its "
        "subtree so later negations are dead; otherwise LAST "
        "matching rule wins), audit a rule set "
        "(mode='analyze': rule_count, dead_rules with blocked_by "
        "proofs per last-match-wins, contradictions, duplicates, "
        "trailing-space traps, missing-final-newline, any-depth "
        "patterns, escaping errors), lint rules (mode='lint': "
        "findings for invalid globs, never-matching patterns, "
        "reversed ranges, redundant ** outside the three special "
        "positions, duplicate rules/negations, the /**/ "
        "zero-or-more-directories note, Windows \\-separator "
        "mistakes) and dissect one rule (mode='explain': "
        "segments, anchored, dir_only, 3 verified example matches "
        "and 2 verified misses). Case-sensitive "
        "(core.ignoreCase=false documented). PathLintTool (#4036) "
        "lints path strings; this tool implements ignore-rule "
        "semantics."
    )

    MODES: ClassVar[tuple] = ("match", "analyze", "lint", "explain")

    _SEVERITY: ClassVar[Dict[str, str]] = {
        "invalid_glob": "error",
        "never_matches": "error",
        "reversed_range": "warning",
        "redundant_doublestar": "warning",
        "duplicate_rule": "warning",
        "duplicate_negation": "warning",
        "doublestar_midsegment": "info",
        "windows_separator": "warning",
    }
    _CODE_ORDER: ClassVar[Tuple[str, ...]] = tuple(_SEVERITY)

    max_rules_chars: int = Field(default=_MAX_RULES_CHARS, gt=0)
    max_rule_lines: int = Field(default=_MAX_RULE_LINES, gt=0)
    max_path_chars: int = Field(default=_MAX_PATH_CHARS, gt=0)
    max_path_segments: int = Field(default=_MAX_PATH_SEGMENTS, gt=0)

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        rules: Any = None,
        path: Any = None,
        is_dir: Any = None,
        rule: Any = None,
    ) -> Dict[str, Any]:
        """Run one gitignore semantics operation.

        Args:
            mode (str): One of ``match`` / ``analyze`` / ``lint`` /
                ``explain``.
            rules (str): The rules text (gitignore syntax) for
                ``match`` / ``analyze`` / ``lint``.
            path (str): The relative path for ``match`` (one
                trailing ``/`` asserts a directory, like the
                check-ignore CLI).
            is_dir (bool): Optional explicit directory assertion
                for ``match`` (overrides the trailing-slash rule).
            rule (str): The single rule line for ``explain``.

        Returns:
            Dict[str, Any]: The operation result.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} "
                f"(got {_preview(mode)})"
            )
        if mode == "match":
            parsed = self._validated_rules(rules)
            norm_path, path_is_dir = self._validated_path(path, is_dir)
            return self._run_match(parsed, norm_path, path_is_dir)
        if mode == "analyze":
            parsed = self._validated_rules(rules)
            return self._run_analyze(parsed, rules)
        if mode == "lint":
            parsed = self._validated_rules(rules)
            return self._run_lint(parsed)
        checked_rule = self._validated_rule(rule)
        return self._run_explain(checked_rule)

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"gitignore_tool: {message}")

    def _validated_rules(self, rules: Any) -> List[_Rule]:
        if not isinstance(rules, str):
            self._invalid(f"rules must be a string (got {_preview(rules)})")
        if len(rules) > self.max_rules_chars:
            self._invalid(
                f"rules exceeds max_rules_chars={self.max_rules_chars} "
                f"({len(rules)} characters)"
            )
        line_count = rules.count("\n") + (
            0 if rules.endswith("\n") or not rules else 1
        )
        if line_count > self.max_rule_lines:
            self._invalid(
                f"rules exceeds max_rule_lines={self.max_rule_lines} "
                f"({line_count} lines)"
            )
        if "\x00" in rules:
            self._invalid("rules must not contain NUL characters")
        return _parse_rules(rules)

    def _validated_path(self, path: Any, is_dir: Any) -> Tuple[str, bool]:
        if not isinstance(path, str) or path == "":
            self._invalid(
                f"path must be a non-empty string (got {_preview(path)})"
            )
        if len(path) > self.max_path_chars:
            self._invalid(
                f"path exceeds max_path_chars={self.max_path_chars} "
                f"({len(path)} characters)"
            )
        if "\x00" in path:
            self._invalid("path must not contain NUL characters")
        if "\\" in path:
            self._invalid(
                "path must use '/' separators only (gitignore paths are "
                "slash-separated; a backslash is an escape, not a "
                f"separator) — got {_preview(path)}"
            )
        norm = path
        path_is_dir = False
        if norm.endswith("/"):
            norm = norm[:-1]
            path_is_dir = True
        if is_dir is not None:
            if not isinstance(is_dir, bool):
                self._invalid(
                    f"is_dir must be a boolean (got {_preview(is_dir)})"
                )
            path_is_dir = is_dir
        if norm.startswith("/"):
            self._invalid("path must be relative to the .gitignore directory")
        if norm == "":
            self._invalid("path must name at least one component")
        components = norm.split("/")
        if len(components) > self.max_path_segments:
            self._invalid(
                f"path exceeds max_path_segments={self.max_path_segments} "
                f"({len(components)} components)"
            )
        for comp in components:
            if comp == "":
                self._invalid("path has an empty component (double slash)")
            if comp in (".", ".."):
                self._invalid(
                    f"path must not contain '{comp}' components "
                    f"(got {_preview(path)})"
                )
        return norm, path_is_dir

    @staticmethod
    def _validated_rule(rule: Any) -> str:
        if not isinstance(rule, str):
            GitignoreTool._invalid(f"rule must be a string (got {_preview(rule)})")
        if not rule or rule.endswith("\n"):
            GitignoreTool._invalid("rule must be a single non-empty line")
        if "\n" in rule:
            GitignoreTool._invalid(
                "rule must not contain newlines (one rule at a time)"
            )
        if len(rule) > _MAX_RULE_CHARS:
            GitignoreTool._invalid(
                f"rule exceeds {_MAX_RULE_CHARS} characters ({len(rule)})"
            )
        if "\x00" in rule:
            GitignoreTool._invalid("rule must not contain NUL characters")
        raw = rule[:-1] if rule.endswith("\r") else rule
        if raw == "" or raw.startswith("#"):
            GitignoreTool._invalid(
                "rule must be a pattern line, not a comment or blank line"
            )
        return raw

    # ------------------------------------------------------------------ #
    # match mode
    # ------------------------------------------------------------------ #

    def _run_match(
        self, rules: List[_Rule], path: str, is_dir: bool
    ) -> Dict[str, Any]:
        verdict = _check_ignore(rules, path, is_dir)
        matching_final = [r for r in rules if _rule_matches(r, path, is_dir)]
        if verdict is None:
            result = {
                "matched": False,
                "rule_index": None,
                "rule_line": None,
                "rule_text": None,
                "negated": False,
                "effective": False,
                "matched_on": None,
                "matched_directory": None,
                "matching_rules": [
                    _rule_ref(r) for r in matching_final[:_MATCH_LIST_LIMIT]
                ],
                "explanation": (
                    "no rule matches the path at any level (neither any "
                    "leading directory nor the path itself); the path is "
                    "not ignored"
                ),
            }
        else:
            rule = verdict.rule
            earlier = [
                _rule_ref(r)
                for r in matching_final
                if r.index < rule.index
            ][:_MATCH_LIST_LIMIT]
            if verdict.via == "directory":
                dead_negations = [
                    _rule_ref(r)
                    for r in matching_final
                    if r.negated and r.index > rule.index
                ][:_MATCH_LIST_LIMIT]
                explanation = (
                    f"ancestor directory '{verdict.directory}' is ignored "
                    f"by the rule at line {rule.line} (index {rule.index}); "
                    "git never descends into an ignored directory, so the "
                    "path is ignored regardless of any later rule"
                )
                if dead_negations:
                    shown = ", ".join(
                        f"line {d['line']} ({d['rule']})" for d in dead_negations
                    )
                    explanation += (
                        "; negation rules that match this path but can "
                        f"never be consulted: {shown}"
                    )
                effective = True
                negated = False
            else:
                if rule.negated:
                    explanation = (
                        f"the LAST matching rule is the negation at line "
                        f"{rule.line} (index {rule.index}); it re-includes "
                        "the path, overriding earlier matching rules"
                    )
                    effective = False
                else:
                    explanation = (
                        f"the LAST matching rule (line {rule.line}, index "
                        f"{rule.index}) ignores the path; later rules win "
                        "over earlier ones (gitignore(5): the last matching "
                        "pattern decides the outcome)"
                    )
                    effective = True
                negated = rule.negated
                if earlier:
                    shown = ", ".join(
                        f"line {e['line']} ({e['rule']})" for e in earlier
                    )
                    explanation += f"; overridden earlier rules: {shown}"
            result = {
                "matched": True,
                "rule_index": rule.index,
                "rule_line": rule.line,
                "rule_text": rule.source,
                "negated": negated,
                "effective": effective,
                "matched_on": verdict.via,
                "matched_directory": verdict.directory,
                "matching_rules": [
                    _rule_ref(r) for r in matching_final[:_MATCH_LIST_LIMIT]
                ],
                "explanation": explanation,
            }
        return {
            "mode": "match",
            "path": path,
            "is_dir": is_dir,
            "rule_count": len(rules),
            **result,
            "notes": (
                "pure in-memory semantics (git wildmatch/dir.c translation); "
                "core.ignoreCase=false (case-sensitive); is_dir mirrors the "
                "dtype resolution of git check-ignore"
            ),
        }

    # ------------------------------------------------------------------ #
    # analyze mode
    # ------------------------------------------------------------------ #

    def _run_analyze(self, rules: List[_Rule], rules_text: str) -> Dict[str, Any]:
        dead_rules: List[Dict[str, Any]] = []
        contradictions: List[Dict[str, Any]] = []
        duplicates: List[Dict[str, Any]] = []
        trailing_space_traps: List[Dict[str, Any]] = []
        any_depth: List[Dict[str, Any]] = []
        escaping_errors: List[Dict[str, Any]] = []

        # duplicates / contradictions by identical parsed shape
        groups: Dict[Tuple[bool, bool, str], List[_Rule]] = {}
        for r in rules:
            groups.setdefault((r.negated, r.mustbedir, r.core), []).append(r)
        for key in sorted(groups, key=lambda k: groups[k][0].index):
            group = groups[key]
            negated = key[0]
            # identical pattern, opposite polarity: they fight
            # (report each unordered pair exactly once, from the
            # negated side)
            mirror = groups.get((not negated, key[1], key[2]))
            if mirror and negated:
                contradictions.append(
                    {
                        "negated": _rule_ref(group[0]),
                        "plain": _rule_ref(mirror[0]),
                        "winner": (
                            "the later of the two lines wins under "
                            "last-match-wins for any path they both match"
                        ),
                    }
                )
            if len(group) < 2:
                continue
            duplicates.append(
                {
                    "indexes": [r.index for r in group],
                    "lines": [r.line for r in group],
                    "rule": group[0].source,
                    "negated": negated,
                    "note": (
                        "earlier copies can never be the last matching rule "
                        "(last match wins); only the final copy is effective"
                    ),
                }
            )
            for r in group[:-1]:
                dead_rules.append(
                    {
                        "index": r.index,
                        "line": r.line,
                        "rule": r.source,
                        "blocked_by": _rule_ref(group[-1]),
                        "reason": (
                            "duplicate negation: an identical later rule "
                            "always shadows it (last match wins)"
                            if negated
                            else "duplicate rule: an identical later rule "
                            "always shadows it (last match wins)"
                        ),
                    }
                )
            # identical pattern, opposite polarity: they fight
            mirror = groups.get((not key[0], key[1], key[2]))
            if mirror and negated:
                # report each unordered pair exactly once
                contradictions.append(
                    {
                        "negated": _rule_ref(group[0]),
                        "plain": _rule_ref(mirror[0]),
                        "winner": (
                            "the later of the two lines wins under "
                            "last-match-wins for any path they both match"
                        ),
                    }
                )

        # negation killed by a later covering rule (sound lattice)
        for i, target in enumerate(rules):
            if not target.negated or not target.match_pat:
                continue
            for later in rules[i + 1 :]:
                if not later.match_pat:
                    continue
                if _rule_covers(later, target):
                    dead_rules.append(
                        {
                            "index": target.index,
                            "line": target.line,
                            "rule": target.source,
                            "blocked_by": _rule_ref(later),
                            "reason": (
                                "later rule provably matches every path "
                                "this negation matches (structural cover), "
                                "so the negation can never be the last match"
                            ),
                        }
                    )
                    break

        # negation dead inside a provably ignored directory
        for target in rules:
            if not target.negated or target.nodir or not target.match_pat:
                continue
            parts = _split_unescaped(target.match_pat)
            for k in range(1, len(parts)):
                prefix_atoms = [_segment_atoms(p) for p in parts[:k]]
                if any(
                    seg is None or any(a[0] != "literal" for a in seg)
                    for seg in prefix_atoms
                ):
                    break  # literal-prefix chain ended: not provable deeper
                directory = "/".join(
                    "".join(a[1] for a in seg) for seg in prefix_atoms
                )
                verdict = _check_ignore(rules, directory, True)
                if verdict is not None and not verdict.rule.negated:
                    dead_rules.append(
                        {
                            "index": target.index,
                            "line": target.line,
                            "rule": target.source,
                            "blocked_by": _rule_ref(verdict.rule),
                            "reason": (
                                "every path this negation matches lies "
                                f"inside the ignored directory '{directory}' "
                                "(git never descends into ignored "
                                "directories, so the negation is never "
                                "consulted)"
                            ),
                        }
                    )
                    break

        # dedup by index (keep the first report) and order by index
        seen_indexes: set = set()
        unique_dead: List[Dict[str, Any]] = []
        for d in sorted(dead_rules, key=lambda d: d["index"]):
            if d["index"] in seen_indexes:
                continue
            seen_indexes.add(d["index"])
            unique_dead.append(d)

        # trailing-space traps and escaping errors from raw lines
        for r in rules:
            if r.space_trimmed:
                trailing_space_traps.append(
                    {
                        "line": r.line,
                        "index": r.index,
                        "raw_line": r.raw_line,
                        "effective_rule": r.source,
                        "note": (
                            "git drops unescaped trailing spaces, so the "
                            "rule is weaker than written; write '\\ ' to "
                            "match a literal trailing space"
                        ),
                    }
                )
            if not r.match_pat:
                continue
            facts = _scan_rule(r.match_pat)
            if facts["dangling_backslash"]:
                escaping_errors.append(
                    {
                        "line": r.line,
                        "index": r.index,
                        "rule": r.source,
                        "problem": (
                            "dangling trailing backslash: it escapes the "
                            "line end, so the pattern can never match (and "
                            "stops trailing-space trimming of the line)"
                        ),
                    }
                )
            if facts["escaped_space_end"]:
                escaping_errors.append(
                    {
                        "line": r.line,
                        "index": r.index,
                        "rule": r.source,
                        "problem": (
                            "'\\ ' at the end of the rule matches a literal "
                            "trailing space in the filename — usually not "
                            "what was meant"
                        ),
                    }
                )
            for _, esc in facts["escapes"][:_DETAIL_LIMIT]:
                if esc not in _SPECIAL_ESCAPE:
                    escaping_errors.append(
                        {
                            "line": r.line,
                            "index": r.index,
                            "rule": r.source,
                            "problem": (
                                f"backslash before '{esc}' escapes an "
                                "ordinary character; in gitignore '\\' is "
                                "an escape, not a Windows path separator — "
                                "if a separator was meant, use '/'"
                            ),
                        }
                    )
                    break

        # any-depth (unanchored slash-free) info patterns
        for r in rules:
            if (
                r.nodir
                and r.match_pat
                and not any(c in r.match_pat for c in "*?[")
            ):
                any_depth.append(
                    {
                        "index": r.index,
                        "line": r.line,
                        "rule": r.source,
                        "note": (
                            "slash-free patterns match at ANY depth "
                            "(basename match); anchor with a leading '/' "
                            "(or a middle slash) if only the top level was "
                            "meant"
                        ),
                    }
                )

        return {
            "mode": "analyze",
            "rule_count": len(rules),
            "dead_rules": unique_dead,
            "contradictions": contradictions[: _DETAIL_LIMIT * 4],
            "duplicates": duplicates[: _DETAIL_LIMIT * 4],
            "trailing_space_traps": trailing_space_traps,
            "missing_final_newline": {
                "present": bool(rules_text) and not rules_text.endswith("\n"),
                "effect": (
                    "git still honors the final line (its reader appends a "
                    "virtual newline), but POSIX text-file convention — and "
                    "several third-party parsers — expect a trailing "
                    "newline; append one"
                ),
            },
            "any_depth_patterns": any_depth,
            "escaping_errors": escaping_errors,
            "notes": (
                "reachability computed honestly per last-match-wins and the "
                "ignored-directory walk; only provable deaths are reported"
            ),
        }

    # ------------------------------------------------------------------ #
    # lint mode
    # ------------------------------------------------------------------ #

    def _run_lint(self, rules: List[_Rule]) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []
        for r in rules:
            findings.extend(self._lint_rule(r))
        seen: Dict[Tuple[bool, bool, str], _Rule] = {}
        for r in rules:
            key = (r.negated, r.mustbedir, r.core)
            if key in seen:
                code = "duplicate_negation" if r.negated else "duplicate_rule"
                first = seen[key]
                findings.append(
                    {
                        "line": r.line,
                        "code": code,
                        "severity": self._SEVERITY[code],
                        "message": (
                            f"rule duplicates line {first.line} "
                            f"('{first.source}'); the earlier copy can never "
                            "be the last matching rule (last match wins)"
                        ),
                    }
                )
            else:
                seen[key] = r
        findings.sort(
            key=lambda f: (f["line"], self._CODE_ORDER.index(f["code"]))
        )
        summary: Dict[str, Any] = {"total": len(findings)}
        for sev in ("error", "warning", "info"):
            summary[sev] = sum(1 for f in findings if f["severity"] == sev)
        return {
            "mode": "lint",
            "findings": findings,
            "summary": summary,
            "rule_count": len(rules),
            "notes": (
                "findings ordered by (line, code order); error-severity "
                "findings mark patterns that can never match anything in "
                "git's matcher"
            ),
        }

    def _lint_rule(self, r: _Rule) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []

        def add(code: str, message: str) -> None:
            out.append(
                {
                    "line": r.line,
                    "code": code,
                    "severity": self._SEVERITY[code],
                    "message": message,
                }
            )

        core = r.match_pat
        if core == "":
            add(
                "never_matches",
                "empty pattern (the line carried only spaces or a bare "
                "'!'): matches nothing",
            )
            return out
        facts = _scan_rule(core)
        if facts["dangling_backslash"]:
            add(
                "never_matches",
                "pattern ends with a dangling backslash: it escapes the "
                "line end and the pattern can never match",
            )
        for cf in facts["classes"]:
            if cf.unterminated:
                excerpt = core[cf.start : cf.start + 24]
                add(
                    "invalid_glob",
                    f"unterminated character class '{excerpt}': git's "
                    "matcher aborts on it, so the pattern never matches",
                )
            elif cf.bad_posix:
                excerpt = core[cf.start : cf.start + 24]
                add(
                    "invalid_glob",
                    f"malformed POSIX class '{excerpt}': the unknown class "
                    "name makes the whole pattern unmatchable",
                )
            for rng in cf.reversed_ranges[:_DETAIL_LIMIT]:
                add(
                    "reversed_range",
                    f"reversed character range [{rng}]: the endpoints are "
                    "ordered high-low (byte values), so the range matches "
                    "nothing",
                )
        if facts["empty_segment"]:
            add(
                "never_matches",
                "empty path segment (double '/'): real paths never contain "
                "an empty component, so the pattern matches nothing",
            )
        for run in facts["star_runs"]:
            if not run["special"]:
                excerpt = core[run["start"] : run["end"]]
                add(
                    "redundant_doublestar",
                    f"'{excerpt}' uses '**' outside the special positions "
                    "(leading '**/', trailing '/**', middle '/**/'): git "
                    "treats it as a single '*' that does not cross '/'",
                )
        if facts["mid_doublestar_slash"]:
            add(
                "doublestar_midsegment",
                "'/**/' matches ZERO or more directories: a/**/b also "
                "matches a/b itself",
            )
        for _, esc in facts["escapes"][:_DETAIL_LIMIT]:
            if esc not in _SPECIAL_ESCAPE:
                glued = core.replace("\\", "")[:24]
                add(
                    "windows_separator",
                    f"backslash before '{esc}': in gitignore '\\' escapes a "
                    "character, so the rule matches names with the parts "
                    f"glued together ('{glued}'); use '/' as the path "
                    "separator",
                )
                break
        return out

    # ------------------------------------------------------------------ #
    # explain mode
    # ------------------------------------------------------------------ #

    def _run_explain(self, raw_rule: str) -> Dict[str, Any]:
        source = _trim_trailing_spaces(raw_rule)
        rule = _Rule(0, 1, raw_rule, source)
        segments = self._explain_segments(rule)
        matches, misses = self._explain_examples(rule)
        notes: List[str] = []
        if rule.negated:
            notes.append(
                "the leading '!' negates the rule: it RE-INCLUDES paths an "
                "earlier rule ignored (write '\\!' for a literal '!')"
            )
        if rule.core.startswith("/"):
            notes.append(
                "the leading '/' anchors the rule to the .gitignore's own "
                "directory (here: the repository root)"
            )
        elif not rule.nodir:
            notes.append(
                "the pattern contains a '/', so it is anchored to the "
                ".gitignore's directory even without a leading '/'"
            )
        else:
            notes.append(
                "the pattern is slash-free, so it matches its basename at "
                "ANY depth"
            )
        if rule.mustbedir:
            notes.append(
                "the trailing '/' restricts the rule to directories; it "
                "never matches files"
            )
        return {
            "mode": "explain",
            "rule_text": raw_rule,
            "negated": rule.negated,
            "anchored": not rule.nodir,
            "dir_only": rule.mustbedir,
            "segments": segments,
            "example_matches": matches,
            "example_misses": misses,
            "notes": notes,
        }

    def _explain_segments(self, rule: _Rule) -> List[Dict[str, Any]]:
        segments: List[Dict[str, Any]] = []
        if rule.negated:
            segments.append(
                {
                    "kind": "negation",
                    "text": "!",
                    "matches": "negates the rule (re-includes)",
                }
            )
        core = rule.match_pat
        parts = _split_unescaped(core)
        for pos, part in enumerate(parts):
            if part == "" and pos == 0:
                segments.append(
                    {
                        "kind": "literal",
                        "text": "/",
                        "matches": "the leading '/' anchors to the root",
                    }
                )
                continue
            atoms = _segment_atoms(part)
            if atoms is None:
                segments.append(
                    {
                        "kind": "literal",
                        "text": part,
                        "matches": "raw text (dead escape: never matches)",
                    }
                )
                continue
            for kind, text in atoms:
                if kind == "star":
                    pure = part == text
                    if len(text) == 1:
                        star_kind = "wildcard"
                        desc = "any run of characters (not crossing '/')"
                    else:
                        special = (
                            (pos == 0 and core.startswith("**"))
                            or (pos == len(parts) - 1 and core.endswith("**"))
                            or (pure and 0 < pos < len(parts) - 1)
                        )
                        star_kind = "doublestar" if special else "wildcard"
                        if special:
                            desc = (
                                "'**' in a special position: crosses '/' "
                                "(zero or more path segments)"
                            )
                        else:
                            desc = (
                                "'**' outside a special position: acts as a "
                                "single '*' (does not cross '/')"
                            )
                    segments.append(
                        {"kind": star_kind, "text": text, "matches": desc}
                    )
                elif kind == "question":
                    segments.append(
                        {
                            "kind": "wildcard",
                            "text": "?",
                            "matches": "any one character except '/'",
                        }
                    )
                elif kind == "class":
                    body = text[1:-1]
                    neg = body.startswith("!") or body.startswith("^")
                    if neg:
                        body = body[1:]
                    posix_name = None
                    if (
                        len(body) >= 4
                        and body.startswith("[:")
                        and body.endswith(":]")
                    ):
                        candidate_name = body[2:-2]
                        if candidate_name in _POSIX_CLASSES:
                            posix_name = candidate_name
                    if posix_name is not None:
                        desc = (
                            f"one character of the POSIX {posix_name} class"
                            + (" (negated)" if neg else "")
                            + "; never '/'"
                        )
                    else:
                        cf = _class_chars("[" + body + "]")
                        if cf is not None and not neg and len(cf.items) <= _DETAIL_LIMIT:
                            members = "".join(sorted(cf.items))
                            desc = f"one character in the set '{members}'"
                        elif cf is not None and neg and len(cf.items) <= _DETAIL_LIMIT:
                            members = "".join(sorted(cf.items))
                            desc = (
                                f"one character NOT in the set '{members}' "
                                "(and never '/')"
                            )
                        else:
                            desc = (
                                "one character NOT in the set"
                                if neg
                                else "one character in the set"
                            )
                    segments.append(
                        {"kind": "class", "text": "[" + text[1:-1] + "]", "matches": desc}
                    )
                else:
                    segments.append(
                        {
                            "kind": "literal",
                            "text": text,
                            "matches": f"the literal text '{text}'",
                        }
                    )
            if pos < len(parts) - 1:
                segments.append(
                    {
                        "kind": "literal",
                        "text": "/",
                        "matches": "path separator (anchors the pattern)",
                    }
                )
        return segments

    # ------------------------------------------------------------------ #
    # explain example generation (verified against the matcher)
    # ------------------------------------------------------------------ #

    _FILLERS = ("d", "e", "f")

    def _build_example(self, rule: _Rule, depth: int) -> str:
        """Build a concrete path that matches ``rule`` by replacing
        wildcards with deterministic filler (depth controls the
        filler and the '**' breadth)."""
        filler = self._FILLERS[depth % len(self._FILLERS)]
        parts = _split_unescaped(rule.match_pat)
        out_parts: List[str] = []
        for idx, part in enumerate(parts):
            if part == "" and idx == 0:
                continue  # leading '/' anchor
            built: List[str] = []
            i = 0
            n = len(part)
            while i < n:
                c = part[i]
                if c == "\\" and i + 1 < n:
                    built.append(part[i + 1])
                    i += 2
                    continue
                if c == "*":
                    j = i
                    while j < n and part[j] == "*":
                        j += 1
                    run_len = j - i
                    pure = part == part[i:j]
                    if run_len >= 2 and (
                        (idx == 0 and rule.match_pat.startswith("**"))
                        or (idx == len(parts) - 1 and rule.match_pat.endswith("**"))
                        or (pure and 0 < idx < len(parts) - 1)
                    ):
                        built.append(filler * (depth + 1))
                    else:
                        built.append(filler)
                    i = j
                    continue
                if c == "?":
                    built.append(filler)
                    i += 1
                    continue
                if c == "[":
                    extent = _class_extent(part, i)
                    if extent is None:
                        built.append(c)
                        i += 1
                        continue
                    body = part[i + 1 : extent - 1]
                    neg = False
                    if body.startswith("!") or body.startswith("^"):
                        neg = True
                        body = body[1:]
                    posix_name = None
                    if (
                        len(body) >= 4
                        and body.startswith("[:")
                        and body.endswith(":]")
                    ):
                        candidate_name = body[2:-2]
                        if candidate_name in _POSIX_CLASSES:
                            posix_name = candidate_name
                    if posix_name is not None:
                        pool = "aA0z9 _-" if not neg else "aA0z9"
                        want = not neg
                        choice = next(
                            (
                                ch
                                for ch in pool
                                if _posix_class_member(
                                    posix_name, ord(ch.encode("latin-1"))
                                )
                                == want
                            ),
                            "z",
                        )
                        built.append(choice)
                    else:
                        cf = _class_chars(("!" if neg else "") + body)
                        if cf is not None and cf.items:
                            if neg:
                                outside = next(
                                    (
                                        ch
                                        for ch in "defghijklmnopqrstuvwxyz"
                                        if ch not in cf.items
                                    ),
                                    "z",
                                )
                                built.append(outside)
                            else:
                                built.append(min(cf.items))
                        else:
                            built.append(filler)
                    i = extent
                    continue
                built.append(c)
                i += 1
            out_parts.append("".join(built))
        text = "/".join(out_parts)
        if rule.mustbedir:
            text += "/"
        return text

    def _explain_examples(self, rule: _Rule) -> Tuple[List[str], List[str]]:
        """Three deterministic matches and two misses, each verified
        against the real matcher (matches must match; misses must
        not)."""
        base = self._build_example(rule, 0)
        second = self._build_example(rule, 1)
        candidates = [base, second, self._build_example(rule, 2)]
        if rule.nodir:
            # A slash-free rule matches at any depth: offer depth
            # variants too (anchored literals have a fixed shape,
            # so nothing to vary there).
            body = base[:-1] if base.endswith("/") else base
            slash = "/" if rule.mustbedir else ""
            candidates += ["a/" + body + slash, "a/b/" + body + slash]
        matches: List[str] = []
        for m in candidates:
            is_dir = m.endswith("/")
            norm = m[:-1] if is_dir else m
            if (
                norm
                and norm not in [x.rstrip("/") for x in matches]
                and _rule_matches(rule, norm, is_dir)
            ):
                matches.append(m)
        if not matches:
            matches = [base]  # generation guarantees at least this one

        base_body = base[:-1] if base.endswith("/") else base
        # Deterministic miss candidates, in fixed priority order;
        # only non-matching ones are kept (verified below).
        miss_candidates: List[str] = []
        if len(base_body) > 1:
            miss_candidates.append("z" + base_body[1:])  # first char changed
        miss_candidates.append(base_body + "zz")          # trailing junk
        swapped = base_body.swapcase()
        if swapped != base_body:
            miss_candidates.append(swapped)               # case mismatch
        if rule.mustbedir:
            miss_candidates.append(base_body)  # the same name as a FILE
        elif rule.nodir:
            miss_candidates.append("dir/" + base_body + "/inner")
        else:
            miss_candidates.append("prefix/" + base_body)
        misses: List[str] = []
        for m in miss_candidates:
            if m.endswith("/"):
                is_dir, norm = True, m[:-1]
            else:
                is_dir, norm = False, m
            if norm and not _rule_matches(rule, norm, is_dir):
                misses.append(m)
        return matches[:3], misses[:2]

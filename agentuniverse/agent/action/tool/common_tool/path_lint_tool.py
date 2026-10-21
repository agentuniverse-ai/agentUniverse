#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: path_lint_tool.py

r"""Filesystem path portability and safety linting, pure Python
stdlib — no filesystem access, no network, no subprocess.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) at the **path-string layer**: not the file on disk
and not the dependency manifest, but the *path text itself*.
Agents that review generated code, sanitize user-supplied paths,
debug "works on Linux, breaks on Windows" reports or migrate
repositories across platforms need to ask path-shaped questions —
"is this path portable across Windows and POSIX?", "does it
carry hidden control characters or Unicode confusables that a
human reviewer cannot see?", "can these two different-looking
path strings reference the same file?" and "would this exact
string survive a Windows filesystem?" Existence is **NOT**
checked — the tool never touches the filesystem; it is pure text
analysis of the path string.

Three modes:

* ``lint`` — one path string into an ordered findings list. Each
  finding is ``{line, code, message, severity}`` where ``line``
  is **always 1** (the single-text contract: the input is one
  string, not a document, so every finding lives on the one and
  only line). Severity is one of ``error`` / ``warning`` /
  ``info``. Checks run in a fixed documented order and each code
  emits at most one finding (details of every affected segment
  are aggregated into that finding's message, bounded), so the
  output is fully deterministic and its size is bounded no
  matter how pathological the input.
* ``compare`` — two path strings into a same-file analysis:
  the POSIX-normalized and Windows-normalized form of each
  (``posixpath.normpath`` / ``ntpath.normpath`` verbatim — the
  stdlib modules are the normative oracle), whether the two can
  alias (reference the same file) on either platform, and why.
  Windows comparison is case-insensitive
  (``ntpath.normcase`` — the documented filesystem truth for
  NTFS/FAT) and folds ``/`` into ``\``; POSIX comparison is
  byte-exact and case-sensitive. A path pair whose Windows
  forms differ *only by letter case* gets the rename-collision
  hint: on Windows such a "rename" collides with the source,
  on POSIX it is a distinct file.
* ``validate`` — one path string plus a ``platform`` option
  (``posix`` / ``windows`` / ``auto`` / ``both``; ``auto`` infers
  Windows from the path shape — a backslash separator or a
  drive-letter prefix — and POSIX otherwise) into per-platform
  verdicts: each verdict is ``valid`` (no error-severity finding
  attributed to that platform) plus the error / warning / info
  code lists and the attributed findings themselves, using the
  same codes as ``lint``.

The lint checks, in execution order (each attributed to the
platforms where it bites — the attribution drives ``validate``):

* ``null_byte`` (error, both) — U+0000 terminates Win32 paths
  and is invalid in POSIX filenames.
* ``control_char`` (error, both) — Unicode ``Cc`` characters
  (C0 0x01-0x1F, DEL 0x7F, C1 U+0080-U+009F) and lone
  surrogates (``Cs`` — unencodable as UTF-8, so the filesystem
  bytes can never exist).
* ``confusable_char`` (warning, both) — separator homoglyphs
  that render like ``/`` or ``\`` but are ordinary characters:
  FULLWIDTH SOLIDUS U+FF0F, FULLWIDTH REVERSE SOLIDUS U+FF3C,
  FRACTION SLASH U+2044, DIVISION SLASH U+2215, REVERSE SOLIDUS
  OPERATOR U+29F5, SMALL REVERSE SOLIDUS U+FE68. A reviewer
  cannot tell them from real separators; the filesystem can.
* ``non_nfc`` (warning, both) — the path is not in Unicode
  Normalization Form C, so canonically equivalent spellings
  compare unequal byte-wise (and NFD-based filesystems such as
  HFS+ normalize the other way).
* ``mixed_separators`` (warning, both) — both ``/`` and ``\``
  occur: each platform reads the other's separator as a literal
  filename character, so the path means different trees on
  different systems.
* ``unc_prefix`` (error or warning, windows) — UNC and Win32
  namespace prefix validation: ``\\?\`` requires an absolute
  target (``\\?\C:\...`` or ``\\?\UNC\server\share\...``), does
  not translate forward slashes, and disables the other checks'
  reliance on translation; a UNC path needs both a server and a
  share (``\\server`` or bare ``\\`` is flagged).
* ``device_namespace`` (info, windows) — ``\\.\`` device paths
  name device objects, not files.
* ``drive_relative`` (warning, windows) — ``C:x`` (and bare
  ``C:``) resolve against the *current directory of drive C*, a
  per-drive working directory that differs from the process
  cwd: the classic Win32 footgun. ``C:\x`` / ``C:/x`` are
  absolute and clean.
* ``reserved_char`` (error, windows) — the Microsoft "Naming
  Files, Paths, and Namespaces" reserved set ``< > : " | ? *``
  outside its two legal structural slots (the drive colon; the
  ``\\?\`` prefix). A colon elsewhere also hints at an NTFS
  alternate data stream, which most tooling cannot round-trip.
* ``reserved_name`` (error, windows) — reserved device names
  CON, PRN, AUX, NUL, COM1-COM9 and LPT1-LPT9 (exactly 1-9:
  COM0 / LPT0 are *not* reserved), case-insensitive, with or
  without an extension (``CON``, ``con``, ``Con.txt`` and
  ``COM3.log.tar`` are all reserved), checked on **every**
  segment — a directory named ``NUL`` fails exactly like a
  file. Knowledge hand-embedded from the Microsoft naming docs,
  not discovered at runtime.
* ``trailing_dot_space`` (error, windows) — segments ending in
  ``.`` or space: Win32 strips them, so ``foo.`` and ``foo``
  collide and ``foo .txt`` silently becomes ``foo.txt``.
* ``dot_segment`` (info, both) — ``.`` segments are no-ops that
  normalization removes.
* ``dot_dot_segment`` (info, both) — benign ``..`` segments that
  stay inside the path (an absolute path's root-clamped ``..``
  is dropped by normalization on both platforms).
* ``parent_escape`` (warning, both) — in a *relative* path,
  ``..`` segments outnumber the preceding real segments
  (``../x``, ``a/../..``): after normalization the path escapes
  its base — the classic sanitized-path traversal leftover.
* ``empty_segment`` (info, both) — interior double separators
  (``a//b``) collapse under normalization, with UNC tolerance:
  a leading pair (exactly two separators — the UNC / POSIX-root
  indicator) and one trailing separator are legal and silent;
  extra leading (``///``), doubled interior and doubled
  trailing separators are reported.
* ``tilde_prefix`` (info, posix) — a leading ``~`` segment is
  expanded by POSIX shells (``~`` / ``~user``) but literal on
  Windows: the path means different things depending on who
  expands it.
* ``segment_length`` (warning, both) — a single component
  longer than 255 characters exceeds the NTFS / ext4 component
  limit.
* ``path_length`` (warning, windows) — the path text exceeds
  260 characters (``MAX_PATH``) and therefore needs the
  ``\\?\`` extended-length prefix or ``LongPathsEnabled``; with
  a ``\\?\`` prefix the budget is 32,767 instead.

Division of labor inside the family (see the Distinction
section of the PR): **FreezeDiffTool** (#4026) and
**RequirementsTool** (#4021) operate on *dependency text*
(pip-freeze snapshots and requirements.txt declarations);
**JsonPathTool** (#3477) / **XmlPathTool** (#3744) query JSON /
XML *documents*; **FileSystemTool** (#750) performs bounded
*filesystem access*. None of them lints the filesystem path
string itself — Windows reserved names, separator portability,
control characters, traversal escapes, encoding — which is
exactly this tool's layer, and it does it without touching the
filesystem the way FileSystemTool must.

Out of scope: symlink resolution, 8.3 short-name aliasing,
``subst`` drives, hard links and case-sensitivity-per-directory
(every one needs filesystem access — this tool is pure text);
existence, permissions and free-space checks; shell quoting;
URL paths.

Determinism: fixed check order, at most one finding per code,
aggregated and bounded message detail, sorted code lists in
every verdict — the same input always yields byte-identical
output on every platform (``ntpath.normcase`` is deliberately
used so the Windows verdict is the same on a POSIX host and
vice versa).

Input validation is strict and happens before any work: wrong
parameter types raise ``ValueError`` (the echoed value is
truncated to a bounded preview — a wrong-typed argument can be
arbitrarily large and is never echoed whole); the path inputs
are capped at ``max_path_chars`` characters (default 4,096 — a
real overridable field on the tool instance; a path at the cap
is linted for length, a path beyond it is rejected, since a
4,097-character "path" is input abuse, not a lint finding);
``platform`` must be one of the four documented values.
"""

import ntpath
import posixpath
import re
import unicodedata
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict, Field

from agentuniverse.agent.action.tool.tool import Tool

# ------------------------------------------------------------------ #
# Limits (reject pathological inputs before any work)
# ------------------------------------------------------------------ #

_MAX_PATH_CHARS = 4_096
# Microsoft MAX_PATH and the extended-length budget.
_WIN_MAX_PATH = 260
_WIN_EXT_MAX_PATH = 32_767
# NTFS / ext4 per-component ceiling.
_MAX_SEGMENT_CHARS = 255
# How many affected segment indexes a single aggregated finding
# lists before switching to "+k more" (bounded output).
_DETAIL_LIMIT = 8

# ------------------------------------------------------------------ #
# Hand-embedded knowledge from the Microsoft naming docs
# ("Naming Files, Paths, and Namespaces"): reserved device
# names are CON PRN AUX NUL COM1-COM9 LPT1-LPT9, case-insensitive,
# with or without an extension. COM0 / LPT0 are NOT in the list.
# ------------------------------------------------------------------ #

_RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)
# Reserved characters (the drive colon and the \\?\ prefix are
# the two legal structural slots, handled by the parser).
_RESERVED_CHARS = "<>:\"|?*"

# Separator homoglyphs: render like / or \ but are ordinary
# filename characters on every filesystem.
_CONFUSABLES: Dict[str, str] = {
    "\uFF0F": "FULLWIDTH SOLIDUS (looks like /)",
    "\uFF3C": "FULLWIDTH REVERSE SOLIDUS (looks like \\)",
    "\u2044": "FRACTION SLASH (looks like /)",
    "\u2215": "DIVISION SLASH (looks like /)",
    "\u29F5": "REVERSE SOLIDUS OPERATOR (looks like \\)",
    "\uFE68": "SMALL REVERSE SOLIDUS (looks like \\)",
}

_SEPARATORS = "/\\"
_DRIVE_RE = re.compile(r"^([A-Za-z]):(.*)$", re.DOTALL)
_EXTENDED_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_EXT_PREFIX = "\\\\?\\"
_EXT_PREFIX_FWD = "//?/"
_UNC_EXT_MARKER = "UNC"
_DEVICE_PREFIX = "\\\\.\\"
_DEVICE_PREFIX_FWD = "//./"
_SEPARATOR_RUN_RE = re.compile(r"[/\\]{2,}")

# Check order == findings order. Deterministic by construction.
_SEVERITY: Dict[str, str] = {
    "null_byte": "error",
    "control_char": "error",
    "confusable_char": "warning",
    "non_nfc": "warning",
    "mixed_separators": "warning",
    "unc_prefix": "error",
    "device_namespace": "info",
    "drive_relative": "warning",
    "reserved_char": "error",
    "reserved_name": "error",
    "trailing_dot_space": "error",
    "dot_segment": "info",
    "dot_dot_segment": "info",
    "parent_escape": "warning",
    "empty_segment": "info",
    "tilde_prefix": "info",
    "segment_length": "warning",
    "path_length": "warning",
}
_CHECK_ORDER: Tuple[str, ...] = tuple(_SEVERITY)
_PLATFORMS: Dict[str, Tuple[str, ...]] = {
    "null_byte": ("posix", "windows"),
    "control_char": ("posix", "windows"),
    "confusable_char": ("posix", "windows"),
    "non_nfc": ("posix", "windows"),
    "mixed_separators": ("posix", "windows"),
    "unc_prefix": ("windows",),
    "device_namespace": ("windows",),
    "drive_relative": ("windows",),
    "reserved_char": ("windows",),
    "reserved_name": ("windows",),
    "trailing_dot_space": ("windows",),
    "dot_segment": ("posix", "windows"),
    "dot_dot_segment": ("posix", "windows"),
    "parent_escape": ("posix", "windows"),
    "empty_segment": ("posix", "windows"),
    "tilde_prefix": ("posix",),
    "segment_length": ("posix", "windows"),
    "path_length": ("windows",),
}


def _preview(value: Any, limit: int = 120) -> str:
    """A bounded ``repr`` for error messages — a wrong-typed
    parameter can be arbitrarily large, and echoing it whole would
    turn a one-line ``ValueError`` into megabytes."""
    text = repr(value)
    if len(text) > limit:
        text = f"{text[:limit]}... (truncated {type(value).__name__})"
    return text


def _listing(indexes: List[int]) -> str:
    """Render segment indexes with the bounded '+k more' tail."""
    head = ", ".join(str(i) for i in indexes[:_DETAIL_LIMIT])
    if len(indexes) <= _DETAIL_LIMIT:
        return f"segment(s) {head}"
    return f"segment(s) {head} and {len(indexes) - _DETAIL_LIMIT} more"


class _Structure:
    r"""The structural parse of one path string.

    Attributes:
        kind (str): one of ``drive_absolute`` / ``drive_relative``
            / ``extended_drive`` / ``extended_unc`` / ``device`` /
            ``unc`` / ``posix_root`` / ``relative`` /
            ``extended_invalid``.
        drive (Optional[str]): the drive letter when present.
        extended (bool): True when a ``\\?\``-shaped prefix
            (either slash) was consumed.
        prefix_fwd (bool): True when the namespace prefix was
            spelled with forward slashes (invalid for Win32).
        lead (int): count of leading separator characters.
        body (str): the path with prefixes and drive letter
            removed (the prefixes carry characters — ``?`` and
            the drive colon — that are legal only in their slot,
            so they must not reach the content scans).
        backslash_lead (bool): True when the leading separator
            run uses a backslash (UNC on Windows).
    """

    def __init__(self, path: str) -> None:
        self.kind = "relative"
        self.drive: Optional[str] = None
        self.extended = False
        self.prefix_fwd = False
        rest = path
        # Win32 namespace prefixes must be matched before the
        # drive letter and before any reserved-character scan.
        lowered = rest.lower()
        if lowered.startswith(_EXT_PREFIX):
            self.extended = True
            rest = rest[len(_EXT_PREFIX):]
            self.kind = "extended_invalid"
            if _EXTENDED_DRIVE_RE.match(rest):
                self.kind = "extended_drive"
            elif rest[:4].upper().startswith(_UNC_EXT_MARKER + "\\"):
                self.kind = "extended_unc"
        elif lowered.startswith(_EXT_PREFIX_FWD):
            self.extended = True
            self.prefix_fwd = True
            rest = rest[len(_EXT_PREFIX_FWD):]
            self.kind = "extended_invalid"
            if _EXTENDED_DRIVE_RE.match(rest):
                self.kind = "extended_drive"
        elif lowered.startswith(_DEVICE_PREFIX):
            rest = rest[len(_DEVICE_PREFIX):]
            self.kind = "device"
        elif lowered.startswith(_DEVICE_PREFIX_FWD):
            rest = rest[len(_DEVICE_PREFIX_FWD):]
            self.kind = "device"
            self.prefix_fwd = True
        # Drive letter (\\.\ device paths and \\?\UNC\ forms have none).
        if self.kind not in ("device", "extended_unc"):
            match = _DRIVE_RE.match(rest)
            if match:
                self.drive = match.group(1)
                rest = match.group(2)
                if self.kind == "relative":
                    self.kind = (
                        "drive_absolute"
                        if rest[:1] and rest[0] in _SEPARATORS
                        else "drive_relative"
                    )
        # Leading separator run (on what remains).
        self.lead = 0
        for ch in rest:
            if ch in _SEPARATORS:
                self.lead += 1
            else:
                break
        self.backslash_lead = rest[:1] == "\\"
        if self.lead and self.kind in ("relative", "drive_relative"):
            # A separator after the drive colon makes it absolute;
            # bare separators make a root/UNC form.
            if self.kind == "drive_relative" and rest[:1] and rest[0] in _SEPARATORS:
                self.kind = "drive_absolute"
            elif self.kind == "relative":
                self.kind = (
                    "unc" if self.lead >= 2 and self.backslash_lead else "posix_root"
                )
        elif self.lead >= 2 and self.kind == "posix_root":
            self.kind = "unc" if self.backslash_lead else "posix_root"
        self.body = rest


def _segment_list(structure: _Structure) -> List[str]:
    """The content segments (empty runs collapsed) of the body."""
    body = structure.body
    if structure.kind == "extended_drive":
        # Strip the separator after the drive colon so segment
        # indexes refer to user-visible components only.
        if body[:1] in _SEPARATORS:
            body = body[1:]
    elif structure.kind == "extended_unc":
        body = body[4:]  # the consumed UNC marker
    return [part for part in re.split(r"[/\\]+", body) if part]


def _lint_path(path: str) -> List[Dict[str, Any]]:
    """Run the fixed check sequence — the deterministic engine of
    all three modes. Returns public findings
    (``{line, code, message, severity}``) plus a private
    ``platforms`` key that ``validate`` consumes (stripped by the
    callers before the payload is returned)."""
    findings: List[Dict[str, Any]] = []
    structure = _Structure(path)

    def add(code: str, message: str) -> None:
        findings.append(
            {
                "line": 1,  # the single-text contract
                "code": code,
                "message": message,
                "severity": _SEVERITY[code],
                "platforms": list(_PLATFORMS[code]),
            }
        )

    # 1. null bytes ------------------------------------------------ #
    if "\x00" in path:
        add(
            "null_byte",
            f"path contains {path.count(chr(0))} null byte(s) (U+0000): "
            "a null byte terminates Win32 paths and is invalid in "
            "POSIX filenames",
        )

    # 2. control characters --------------------------------------- #
    controls: List[str] = []
    for ch in path:
        if ch == "\x00":
            continue
        category = unicodedata.category(ch)
        if category == "Cc":
            controls.append(f"U+{ord(ch):04X}")
        elif category == "Cs":
            controls.append(f"U+{ord(ch):04X} (lone surrogate)")
    if controls:
        head = ", ".join(controls[:_DETAIL_LIMIT])
        more = (
            f" and {len(controls) - _DETAIL_LIMIT} more"
            if len(controls) > _DETAIL_LIMIT
            else ""
        )
        add(
            "control_char",
            f"path contains control characters: {head}{more} — "
            "control characters (Unicode Cc) cannot appear in "
            "filenames, and lone surrogates cannot be encoded as "
            "UTF-8 at all",
        )

    # 3. separator homoglyphs -------------------------------------- #
    seen: List[str] = []
    for ch, label in _CONFUSABLES.items():
        if ch in path:
            seen.append(f"{label} U+{ord(ch):04X}")
    if seen:
        add(
            "confusable_char",
            "path contains separator lookalikes that are ordinary "
            f"characters: {'; '.join(seen)} — they render like real "
            "separators but never split the path",
        )

    # 4. normalization form ---------------------------------------- #
    if unicodedata.normalize("NFC", path) != path:
        add(
            "non_nfc",
            "path is not in Unicode Normalization Form C — "
            "canonically equivalent spellings (e.g. e + combining "
            "acute vs the precomposed e-acute) compare unequal "
            "byte-wise; normalize with NFC for stable comparison",
        )

    # 5. mixed separators ------------------------------------------ #
    if "/" in path and "\\" in path:
        add(
            "mixed_separators",
            "path mixes '/' and '\\' separators — POSIX treats '\\' "
            "as a literal filename character and Windows accepts "
            "both, so the string resolves to different trees on "
            "different platforms",
        )

    # 6. UNC / namespace prefixes ---------------------------------- #
    if structure.kind == "extended_invalid":
        detail = (
            "the \\\\?\\ prefix must be followed by a drive-absolute "
            "target (\\\\?\\C:\\...) or UNC\\server\\share; forward "
            "slashes and relative components are not translated"
        )
        if structure.prefix_fwd:
            detail = (
                "the extended-length prefix must use backslashes "
                "(\\\\?\\); '//?/' is not recognized by Win32"
            )
        add("unc_prefix", f"invalid extended-length prefix: {detail}")
    elif structure.prefix_fwd or (
        structure.extended
        and structure.kind in ("extended_drive", "extended_unc")
        and "/" in structure.body
    ):
        add(
            "unc_prefix",
            "a Win32 namespace prefix path must use backslashes "
            "only — the \\\\?\\ and \\\\.\\ prefixes disable "
            "translation, so forward slashes are not separators "
            "there and the path fails on Windows",
        )
    elif structure.kind == "unc":
        segments = _segment_list(structure)
        if len(segments) < 2:
            add(
                "unc_prefix",
                "UNC path is missing its share: a UNC path needs "
                "both a server and a share (\\\\server\\share\\...)",
            )

    # 7. device namespace ------------------------------------------ #
    if structure.kind == "device":
        add(
            "device_namespace",
            "the \\\\.\\ prefix addresses the Win32 device namespace "
            "(\\\\.\\PhysicalDisk0, \\\\.\\COM1) — device objects, "
            "not files; not a portable filesystem path",
        )

    # 8. drive-relative form --------------------------------------- #
    if structure.kind == "drive_relative":
        add(
            "drive_relative",
            "drive-relative path (C:x, or bare C:) — resolves "
            "against the current directory of drive C, a hidden "
            "per-drive working directory that differs from the "
            "process cwd; use C:\\x for an absolute path",
        )

    # Segment-level checks (skip content scans inside prefixes).
    segments = _segment_list(structure)

    # 9. reserved characters --------------------------------------- #
    hits: Dict[str, List[int]] = {}
    for index, segment in enumerate(segments, start=1):
        for ch in _RESERVED_CHARS:
            if ch in segment:
                hits.setdefault(ch, []).append(index)
    if hits:
        parts = []
        for ch in _RESERVED_CHARS:
            if ch in hits:
                spots = hits[ch]
                head = ", ".join(str(i) for i in spots[:_DETAIL_LIMIT])
                tail = (
                    f" (+{len(spots) - _DETAIL_LIMIT} more)"
                    if len(spots) > _DETAIL_LIMIT
                    else ""
                )
                extra = (
                    " (a colon here suggests an NTFS alternate data "
                    "stream, which most tooling cannot round-trip)"
                    if ch == ":"
                    else ""
                )
                parts.append(f"'{ch}' in segment(s) {head}{tail}{extra}")
        add(
            "reserved_char",
            "Windows reserved characters present: "
            + "; ".join(parts)
            + " — the reserved set < > : \" | ? * cannot appear in "
            "a path component (Microsoft Naming Files, Paths, and "
            "Namespaces)",
        )

    # 10. reserved device names ------------------------------------ #
    reserved_hits: List[int] = []
    for index, segment in enumerate(segments, start=1):
        if segment in (".", ".."):
            continue
        # Win32 strips trailing dots and spaces from every segment
        # before the name is interpreted, so the reserved-name
        # comparison must see the stripped stem ("PRN .dat" is
        # PRN.dat is reserved).
        stem = segment.split(".", 1)[0].rstrip(" .").upper()
        if stem in _RESERVED_NAMES:
            reserved_hits.append(index)
    if reserved_hits:
        add(
            "reserved_name",
            f"Windows reserved device name in {_listing(reserved_hits)}: "
            "CON PRN AUX NUL COM1-COM9 LPT1-LPT9 are reserved "
            "case-insensitively, with or without an extension "
            "(CON.txt is as reserved as CON); COM0/LPT0 are not "
            "reserved",
        )

    # 11. trailing dots / spaces ----------------------------------- #
    trailing: List[int] = []
    for index, segment in enumerate(segments, start=1):
        if segment in (".", ".."):
            continue  # '.' and '..' are legal special segments
        if segment.endswith(".") or segment.endswith(" "):
            trailing.append(index)
    if trailing:
        add(
            "trailing_dot_space",
            f"segment(s) ending in '.' or space in {_listing(trailing)}: "
            "Win32 strips trailing dots and spaces, so 'foo.' "
            "collides with 'foo' and 'foo .txt' silently becomes "
            "'foo.txt'",
        )

    # 12-13. dot segments / parent escapes ------------------------- #
    dot_indexes: List[int] = []
    dotdot_indexes: List[int] = []
    for index, segment in enumerate(segments, start=1):
        if segment == ".":
            dot_indexes.append(index)
        elif segment == "..":
            dotdot_indexes.append(index)
    if dot_indexes:
        add(
            "dot_segment",
            f"'.' no-op segment(s) at {_listing(dot_indexes)} — "
            "removed by normalization on both platforms",
        )
    absolute = structure.kind in (
        "drive_absolute",
        "extended_drive",
        "extended_unc",
        "unc",
        "posix_root",
        "device",
    )
    escapes = 0
    depth = 0
    for segment in segments:
        if segment == "..":
            if absolute or depth > 0:
                depth = max(0, depth - 1)
            else:
                depth -= 1
                if depth < 0:
                    escapes += 1
        elif segment not in (".", ""):
            depth += 1
    if escapes:
        add(
            "parent_escape",
            f"{escapes} '..' segment(s) escape the relative base — "
            "after normalization the path references locations "
            "above its starting directory (the classic "
            "sanitized-path traversal leftover)",
        )
    elif dotdot_indexes:
        note = (
            " (beyond the root they are simply dropped)"
            if absolute
            else ""
        )
        add(
            "dot_dot_segment",
            f"'..' segment(s) at {_listing(dotdot_indexes)} stay "
            "inside the path and are resolved by normalization"
            f"{note}",
        )

    # 14. empty segments (with UNC tolerance) ---------------------- #
    empties: List[str] = []
    body = structure.body
    if structure.lead > 2:
        empties.append(f"{structure.lead - 2} extra leading separator(s)")
    for match in _SEPARATOR_RUN_RE.finditer(body):
        run = match.group(0)
        start, end = match.span()
        if start == 0:
            # The leading run is fully handled by the lead>2 check
            # above (a tolerated pair reports nothing).
            continue
        if end == len(body):
            # One trailing separator is legal and silent; a run of
            # two or more reports the extras.
            if len(run) < 2:
                continue
            empties.append(
                f"{len(run) - 1} trailing separator(s) at the end"
            )
        else:
            empties.append(f"empty segment(s) at offset {start}")
    if empties:
        add(
            "empty_segment",
            f"{'; '.join(empties[:_DETAIL_LIMIT])} — empty segments "
            "collapse under normalization; the leading pair of a "
            "UNC / POSIX-root path and one trailing separator are "
            "legal and tolerated",
        )

    # 15. tilde prefix --------------------------------------------- #
    if segments and segments[0].startswith("~"):
        add(
            "tilde_prefix",
            "the leading segment starts with '~' — POSIX shells "
            "expand ~ and ~user to a home directory while Windows "
            "keeps the tilde literal, so the path depends on who "
            "expands it",
        )

    # 16. over-long segments --------------------------------------- #
    long_segments = [
        index
        for index, segment in enumerate(segments, start=1)
        if len(segment) > _MAX_SEGMENT_CHARS
    ]
    if long_segments:
        worst = max(len(s) for s in segments)
        add(
            "segment_length",
            f"component(s) at {_listing(long_segments)} exceed "
            f"{_MAX_SEGMENT_CHARS} characters (longest "
            f"{worst}) — the per-component limit of NTFS and ext4",
        )

    # 17. total length --------------------------------------------- #
    budget = _WIN_EXT_MAX_PATH if structure.extended else _WIN_MAX_PATH
    if len(path) > budget:
        detail = (
            "Windows MAX_PATH (260) — the path needs the \\\\?\\ "
            "extended-length prefix or LongPathsEnabled"
            if not structure.extended
            else "the extended-length budget (32,767)"
        )
        add(
            "path_length",
            f"path is {len(path)} characters, beyond {detail}",
        )

    return findings


def _public(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Strip the private platform attribution for output."""
    return {
        "line": finding["line"],
        "code": finding["code"],
        "message": finding["message"],
        "severity": finding["severity"],
    }


def _summary(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        counts[finding["severity"]] += 1
    return {
        "total": len(findings),
        "error": counts["error"],
        "warning": counts["warning"],
        "info": counts["info"],
    }


def _normalize_windows(path: str) -> str:
    return ntpath.normpath(path)


def _fold_windows(path: str) -> str:
    return ntpath.normcase(ntpath.normpath(path))


def _normalize_posix(path: str) -> str:
    return posixpath.normpath(path)


def _compare_paths(path_a: str, path_b: str) -> Dict[str, Any]:
    """The same-file analysis of the compare mode."""
    posix_a = _normalize_posix(path_a)
    posix_b = _normalize_posix(path_b)
    windows_a = _normalize_windows(path_a)
    windows_b = _normalize_windows(path_b)
    fold_a = _fold_windows(path_a)
    fold_b = _fold_windows(path_b)
    posix_equal = posix_a == posix_b
    windows_equal = fold_a == fold_b
    case_only = (
        not posix_equal and windows_a != windows_b and windows_equal
    )
    reasons: List[str] = []
    reasons.append(
        "posix: normalized forms are identical (same file on a "
        "case-sensitive POSIX filesystem)"
        if posix_equal
        else "posix: normalized forms differ (different files on "
        "a case-sensitive POSIX filesystem)"
    )
    reasons.append(
        "windows: normalized forms are identical after case "
        "folding (same file on a case-insensitive Windows "
        "filesystem)"
        if windows_equal
        else "windows: normalized forms differ even after case "
        "folding (different files on Windows)"
    )
    if case_only:
        reasons.append(
            "rename collision: the two paths differ only by letter "
            "case — renaming one to the other collides on Windows "
            "(case-insensitive) while creating a second file on "
            "POSIX"
        )
    if not posix_equal and windows_equal:
        reasons.append(
            "the pair can alias on Windows but not on POSIX"
        )
    elif posix_equal and not windows_equal:
        reasons.append(
            "the pair can alias on POSIX but not on Windows"
        )
    reasons.append(
        "text-level analysis only: relative paths are assumed to "
        "share one current directory, and symlink resolution, 8.3 "
        "short names, subst drives and hard links are not checked "
        "(no filesystem access)"
    )
    return {
        "posix_normalized": {
            "a": posix_a,
            "b": posix_b,
            "equal": posix_equal,
        },
        "windows_normalized": {
            "a": windows_a,
            "b": windows_b,
            "equal": windows_equal,
        },
        "case_only_difference": case_only,
        "alias_possible": posix_equal or windows_equal,
        "reasons": reasons,
    }


def _validate_path_string(value: Any, name: str, cap: int) -> str:
    """Strict single-string validation (type and cap)."""
    if value is None or isinstance(value, bool) or not isinstance(value, str):
        raise ValueError(
            f"path_lint_tool: {name} must be a string "
            f"(got {_preview(value)})"
        )
    if len(value) > cap:
        raise ValueError(
            f"path_lint_tool: {name} is {len(value)} characters, "
            f"beyond the {cap}-character cap (raise max_path_chars "
            f"on the tool instance to lint deliberately longer "
            f"strings)"
        )
    return value


# ------------------------------------------------------------------ #
# The tool
# ------------------------------------------------------------------ #

class PathLintTool(Tool):
    """Filesystem path portability and safety linting tool.

    Attributes:
        max_path_chars (int): Upper bound on any path string
            (default 4,096; overridable per instance).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "path_lint_tool"
    description: str = (
        "Filesystem path portability and safety linting, pure "
        "Python stdlib — no filesystem access (existence is NOT "
        "checked), no network, no subprocess. Lint one path "
        "(mode='lint': ordered findings [{line (always 1), code, "
        "message, severity}] — null bytes and control characters, "
        "separator homoglyphs and non-NFC Unicode, mixed / and \\ "
        "separators, UNC and \\\\?\\ prefix validation, the "
        "drive-relative C:x quirk, Windows reserved characters "
        "<>:\"|?* and reserved device names CON PRN AUX NUL "
        "COM1-9 LPT1-9 (case-insensitive, with or without "
        "extension), trailing dots/spaces, '.'/'..' semantics "
        "with parent-escape detection, empty segments with UNC "
        "tolerance, tilde prefixes, the 260-character MAX_PATH "
        "and 255-character component limits), analyze whether "
        "two paths can alias (mode='compare': posixpath/ntpath "
        "normalization of both, Windows case-insensitivity "
        "documented via ntpath.normcase, case-only rename "
        "collision hint, alias_possible with reasons) and give "
        "per-platform verdicts (mode='validate': posix / windows "
        "/ auto / both with the lint failure codes attributed "
        "per platform). FreezeDiffTool (#4026) and "
        "RequirementsTool (#4021) handle dependency text; this "
        "tool is the path-string layer."
    )

    MODES: ClassVar[tuple] = ("lint", "compare", "validate")
    PLATFORMS: ClassVar[tuple] = ("posix", "windows", "auto", "both")

    max_path_chars: int = Field(default=_MAX_PATH_CHARS, gt=0)

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        path: Any = None,
        path_a: Any = None,
        path_b: Any = None,
        platform: Any = None,
    ) -> Dict[str, Any]:
        """Run one path linting operation.

        Args:
            mode (str): One of ``lint`` / ``compare`` /
                ``validate``.
            path (str): The path string for ``lint`` and
                ``validate`` (required there; ignored by
                ``compare``).
            path_a (str): The first path for ``compare``
                (required there).
            path_b (str): The second path for ``compare``
                (required there).
            platform (str): The platform option for ``validate``
                — ``posix`` / ``windows`` / ``auto`` (infer from
                the path shape) / ``both`` (default ``auto``).

        Returns:
            Dict[str, Any]: The operation result — a structured
                payload per mode, with path-level problems carried
                inside the findings instead of raising.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} "
                f"(got {_preview(mode)})"
            )
        if mode == "lint":
            checked = _validate_path_string(path, "path", self.max_path_chars)
            return self._run_lint(checked)
        if mode == "compare":
            first = _validate_path_string(path_a, "path_a", self.max_path_chars)
            second = _validate_path_string(path_b, "path_b", self.max_path_chars)
            return self._run_compare(first, second)
        checked = _validate_path_string(path, "path", self.max_path_chars)
        if platform is None:
            platform = "auto"
        if platform not in self.PLATFORMS:
            self._invalid(
                f"platform must be one of: {', '.join(self.PLATFORMS)} "
                f"(got {_preview(platform)})"
            )
        return self._run_validate(checked, platform)

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"path_lint_tool: {message}")

    def _run_lint(self, path: str) -> Dict[str, Any]:
        findings = [_public(f) for f in _lint_path(path)]
        return {
            "mode": "lint",
            "findings": findings,
            "summary": _summary(findings),
            "checked_length": len(path),
            "notes": (
                "pure text analysis — file existence is NOT "
                "checked; line is always 1 (single-text contract)"
            ),
        }

    def _run_compare(self, path_a: str, path_b: str) -> Dict[str, Any]:
        result = _compare_paths(path_a, path_b)
        return {
            "mode": "compare",
            **result,
        }

    def _run_validate(self, path: str, platform: str) -> Dict[str, Any]:
        raw_findings = _lint_path(path)
        inferred = None
        if platform == "auto":
            inferred = self._infer_platform(path)
            targets = (inferred,)
        elif platform == "both":
            targets = ("posix", "windows")
        else:
            targets = (platform,)
        verdicts: Dict[str, Any] = {}
        for target in targets:
            attributed = [
                f for f in raw_findings if target in f["platforms"]
            ]
            codes = [f["code"] for f in attributed]
            verdicts[target] = {
                "valid": not any(
                    f["severity"] == "error" for f in attributed
                ),
                "error_codes": [
                    f["code"] for f in attributed
                    if f["severity"] == "error"
                ],
                "warning_codes": [
                    f["code"] for f in attributed
                    if f["severity"] == "warning"
                ],
                "info_codes": [
                    f["code"] for f in attributed
                    if f["severity"] == "info"
                ],
                "codes": codes,
                "findings": [_public(f) for f in attributed],
            }
        payload: Dict[str, Any] = {
            "mode": "validate",
            "platforms": verdicts,
        }
        if inferred is not None:
            payload["inferred_platform"] = inferred
            payload["inference_rule"] = (
                "auto: a backslash separator or a drive-letter "
                "prefix implies windows, everything else posix"
            )
        payload["checked_length"] = len(path)
        return payload

    @staticmethod
    def _infer_platform(path: str) -> str:
        """Infer the platform from the path shape."""
        if "\\" in path:
            return "windows"
        if _DRIVE_RE.match(path):
            # A drive-letter prefix (C:\x, C:/x, C:x, bare C:) is
            # a Windows concept in every form.
            return "windows"
        return "posix"

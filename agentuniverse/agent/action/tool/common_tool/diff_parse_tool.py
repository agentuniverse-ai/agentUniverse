#!/usr/bin/env python3
"""Unified-diff parsing, validation, reverse generation, and statistics.

The tool accepts a unified diff (plain ``diff -u`` output, ``git diff`` output,
or difflib-style output) and offers four deterministic, stdlib-only modes:

- ``validate``    -- grammar and arithmetic audit of the diff text itself
- ``apply_check`` -- verify the diff applies to a single original text
- ``reverse``     -- produce a diff that transforms the new text back to the old
- ``stats``       -- per-file change statistics and churn hotspots

Policies (documented, deterministic):

- Strict two-way unified diffs only. Combined ``@@@`` merge diffs are rejected
  as malformed body lines.
- ``apply_check`` requires exact context and removed-line matches at the
  positions implied by the hunk headers; there is no fuzz-factor search
  (unlike ``patch(1)`` which retries at nearby offsets). File-level sections
  are additionally held to their ``/dev/null`` claims: a ``--- /dev/null``
  (or ``new file mode``) diff cannot apply to non-empty text (patch(1)
  refuses with "Patch creates file that already exists!"), and a
  ``+++ /dev/null`` (or ``deleted file mode``) diff must consume the
  original entirely.
- A context line whose content is empty is the prefix character ``' '`` plus
  empty text, i.e. a single space on the line. A completely empty body line
  is a grammar violation (``E_EMPTY_BODY_LINE``).
- ``\\ No newline at end of file`` must immediately follow a ``' '``, ``'+'``
  or ``'-'`` body line and may not follow another marker. It may follow a
  context line (meaning both sides lack a final newline) or the ``-``/``+``
  line of either side. Because a line without a trailing newline is by
  definition the last line of its file, the marker may only annotate the
  final ``' '``/``'-'`` line of the old side and the final ``' '``/``'+'``
  line of the new side across the whole file section; a marker on any
  earlier line (with same-side lines following in the same or a later hunk)
  is rejected as semantically impossible (``patch(1)`` calls this a
  malformed patch).
- Hunk headers must be arithmetically consistent: the new-side position of
  hunk N must equal its old-side position plus the net line change
  accumulated by earlier hunks of the same file (``E_HUNK_OFFSET``). Real
  ``diff -u``/``git diff``/``difflib`` output always satisfies this, and
  ``patch(1)`` rejects diffs that do not.
- Newline transport: when every physical line of the diff text ends with CRLF
  the CRs are treated as the diff's own line endings and stripped. When only
  some lines end with CR, the CRs are kept as line content and a
  ``W_MIXED_NEWLINE`` warning is emitted. CR characters surviving inside body
  lines are content (the diffed file itself had CRLF endings) and are compared
  exactly against the original text; ``W_CRLF_CONTENT`` marks them.
- An empty old range is written ``-0,0`` for new files or ``-N,0`` for pure
  insertions after line N; a start of 0 with a nonzero count is a grammar
  error. Counts of 1 may be omitted per POSIX.
- Git header parsing follows real ``git diff`` behavior: ``old mode`` /
  ``new mode`` prelude lines alone form a valid hunk-less section (a pure
  permission-bit change produces exactly that), quoted paths use C escapes
  where consecutive octal escapes are raw bytes decoded as UTF-8 (git's
  ``core.quotePath`` octal form), and the ambiguous unquoted
  ``diff --git a/<path with spaces> b/<path>`` form is split at the first
  ``' b/'`` separator exactly like GNU patch does.
- ``reverse`` is a textual transform: it swaps the ``---``/``+++`` paths,
  flips every hunk header range, and swaps ``+``/``-`` markers in place.
  Git-specific prelude lines (index, modes, rename/copy metadata) are dropped
  because they cannot be truthfully inverted; binary and hunk-less sections
  are reported in ``skipped``.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")
_MARKER = "\\ No newline at end of file"
_ESCAPES = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "f": "\f",
    "b": "\b",
    "v": "\v",
    "a": "\a",
    '"': '"',
    "\\": "\\",
}

_GIT_EXTRAS: ClassVar[tuple[str, ...]] = (
    "index",
    "old mode",
    "new mode",
    "new file mode",
    "deleted file mode",
    "similarity index",
    "dissimilarity index",
    "rename from",
    "rename to",
    "copy from",
    "copy to",
)

_MODES: ClassVar[tuple[str, ...]] = ("validate", "apply_check", "reverse", "stats")


class BodyLine:
    """One hunk body line: origin ' ', '+', '-' with optional no-newline mark."""

    __slots__ = ("content", "line_no", "no_newline", "origin")

    def __init__(self, origin: str, content: str, line_no: int) -> None:
        self.origin = origin
        self.content = content
        self.line_no = line_no
        self.no_newline = False


class Hunk:
    """One @@ hunk with parsed header numbers and consumed body lines."""

    __slots__ = (
        "line_no",
        "lines",
        "new_count",
        "new_start",
        "new_used",
        "old_count",
        "old_start",
        "old_used",
        "section",
    )

    def __init__(self, line_no: int, old_start: int, old_count: int, new_start: int, new_count: int, section: str) -> None:
        self.line_no = line_no
        self.old_start = old_start
        self.old_count = old_count
        self.new_start = new_start
        self.new_count = new_count
        self.section = section
        self.lines: list[BodyLine] = []
        self.old_used = 0
        self.new_used = 0

    def _consume(self, line: BodyLine) -> None:
        self.lines.append(line)
        if line.origin in (" ", "-"):
            self.old_used += 1
        if line.origin in (" ", "+"):
            self.new_used += 1

    def old_side_no_newline(self) -> bool:
        return any(item.no_newline and item.origin in (" ", "-") for item in self.lines)

    def new_side_no_newline(self) -> bool:
        return any(item.no_newline and item.origin in (" ", "+") for item in self.lines)


class FileSection:
    """One file's portion of the diff: headers, git extras, and hunks."""

    __slots__ = (
        "binary",
        "extras",
        "git_paths",
        "hunks",
        "line_no",
        "new_path",
        "new_ts",
        "old_path",
        "old_ts",
    )

    def __init__(self, line_no: int) -> None:
        self.line_no = line_no
        self.git_paths: tuple[str, str] | None = None
        self.extras: list[tuple[str, str]] = []
        self.old_path: str | None = None
        self.new_path: str | None = None
        self.old_ts: str | None = None
        self.new_ts: str | None = None
        self.binary = False
        self.hunks: list[Hunk] = []

    def status(self) -> str:
        """Classify the section as added, deleted, renamed, binary, or modified."""
        kinds = {kind for kind, _ in self.extras}
        if self.binary:
            return "binary"
        if "rename from" in kinds or "rename to" in kinds:
            return "renamed"
        if self.old_path == "/dev/null" or "new file mode" in kinds:
            return "added"
        if self.new_path == "/dev/null" or "deleted file mode" in kinds:
            return "deleted"
        return "modified"

    def normalized_paths(self) -> tuple[str, str]:
        """Resolve effective paths (header, rename extras, or git header) and
        strip single git a/ b/ prefixes, keeping /dev/null intact."""
        extras = dict(self.extras)
        old = self.old_path
        new = self.new_path
        if old is None:
            old = extras.get("rename from") or extras.get("copy from")
            if old is None and self.git_paths is not None:
                old = self.git_paths[0]
        if new is None:
            new = extras.get("rename to") or extras.get("copy to")
            if new is None and self.git_paths is not None:
                new = self.git_paths[1]
        old = old or ""
        new = new or ""
        if old.startswith("a/") and len(old) > 2:
            old = old[2:]
        if new.startswith("b/") and len(new) > 2:
            new = new[2:]
        return old, new


class ParsedDiff:
    """Parse result shared by every mode."""

    __slots__ = ("cr_warned", "files", "final_newline", "findings", "newline_style", "truncated")

    def __init__(self) -> None:
        self.files: list[FileSection] = []
        self.findings: list[dict[str, Any]] = []
        self.newline_style = "lf"
        self.final_newline = True
        self.truncated = False
        self.cr_warned = False

    def errors(self) -> list[dict[str, Any]]:
        return [item for item in self.findings if item["severity"] == "error"]

    def warnings(self) -> list[dict[str, Any]]:
        return [item for item in self.findings if item["severity"] == "warning"]


class DiffParseTool(Tool):
    """Validate, apply-check, reverse, and summarize unified diffs (stdlib only)."""

    max_input_bytes: int = 2 * 1024 * 1024
    max_lines: int = 200_000
    max_files: int = 2_000
    max_hunks: int = 20_000
    max_line_bytes: int = 1_048_576
    warn_line_bytes: int = 65_536
    max_findings: int = 200

    def execute(
        self,
        mode: str,
        diff: str,
        original_text: str | None = None,
        new_text: str | None = None,
    ) -> dict[str, Any]:
        try:
            operation = self._mode(mode)
            text = self._diff_text(diff)
            parsed = self._parse(text)
            if operation == "validate":
                return self._validate_result(parsed)
            if operation == "apply_check":
                return self._apply_check(parsed, original_text)
            if operation == "reverse":
                return self._reverse_result(parsed, new_text)
            return self._stats_result(parsed)
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except RecursionError:  # pragma: no cover - defensive
            return self._error("validation_error", "diff structure is too deeply nested")
        except Exception as exc:  # pragma: no cover - defensive
            return self._error("operation_error", f"Diff parsing failed: {exc}")

    # ------------------------------------------------------------- input checks

    @staticmethod
    def _error(kind: str, message: str, **extra: Any) -> dict[str, Any]:
        result: dict[str, Any] = {"status": "error", "error_type": kind, "error": message}
        result.update(extra)
        return result

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in _MODES:
            raise ValueError("mode must be validate, apply_check, reverse, or stats")
        return mode

    def _diff_text(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("diff must be a string")
        if not value.strip():
            raise ValueError("diff must be a non-empty string")
        if self._byte_size(value) > self.max_input_bytes:
            raise ValueError(f"diff exceeds max_input_bytes ({self.max_input_bytes})")
        return value

    def _optional_text(self, name: str, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string when provided")
        if self._byte_size(value) > self.max_input_bytes:
            raise ValueError(f"{name} exceeds max_input_bytes ({self.max_input_bytes})")
        return value

    @staticmethod
    def _byte_size(value: str) -> int:
        return len(value.encode("utf-8", "replace"))

    # ----------------------------------------------------------------- parsing

    def _add_finding(
        self, parsed: ParsedDiff, line_no: int, code: str, message: str, severity: str = "error"
    ) -> None:
        if len(parsed.findings) < self.max_findings:
            parsed.findings.append(
                {"line": line_no, "code": code, "severity": severity, "message": message}
            )
        else:
            parsed.truncated = True

    def _split_lines(self, parsed: ParsedDiff, text: str) -> list[str]:
        """Split on LF, classify CRLF transport, and strip transport CRs."""
        raw = text.split("\n")
        parsed.final_newline = text.endswith("\n")
        if parsed.final_newline:
            raw.pop()
        if not raw:
            return raw
        with_cr = sum(1 for item in raw if item.endswith("\r"))
        if with_cr == len(raw):
            parsed.newline_style = "crlf"
            raw = [item[:-1] for item in raw]
        elif with_cr:
            parsed.newline_style = "mixed"
            self._add_finding(
                parsed,
                1,
                "W_MIXED_NEWLINE",
                "diff mixes LF and CRLF line endings; CR characters kept as content",
                "warning",
            )
        if len(raw) > self.max_lines:
            raise ValueError(f"diff exceeds max_lines ({self.max_lines})")
        for position, item in enumerate(raw, start=1):
            size = self._byte_size(item)
            if size > self.max_line_bytes:
                raise ValueError(f"line {position} exceeds max_line_bytes ({self.max_line_bytes})")
            if size > self.warn_line_bytes:
                self._add_finding(
                    parsed, position, "W_LONG_LINE", f"line {position} is unusually long", "warning"
                )
        if not parsed.final_newline:
            self._add_finding(
                parsed,
                len(raw),
                "W_NO_EOF_NEWLINE",
                "diff text is missing a newline at end of file",
                "warning",
            )
        return raw

    @staticmethod
    def _decode_quoted(path: str) -> tuple[str, bool]:
        """Decode a GNU-style quoted path; unknown escapes stay literal.

        Git's ``core.quotePath`` escapes non-ASCII filenames as sequences of
        one-byte octal escapes (the UTF-8 bytes), so escapes and literal
        characters are accumulated into a byte string first and decoded as
        UTF-8 afterwards; undecodable bytes become U+FFFD.
        """
        if not path.startswith('"'):
            return path, True
        out = bytearray()
        index = 1
        while index < len(path):
            char = path[index]
            if char == "\\" and index + 1 < len(path):
                nxt = path[index + 1]
                if nxt in _ESCAPES:
                    out.append(ord(_ESCAPES[nxt]))
                    index += 2
                    continue
                if nxt in "01234567":
                    digits = []
                    scan = index + 1
                    while scan < len(path) and len(digits) < 3 and path[scan] in "01234567":
                        digits.append(path[scan])
                        scan += 1
                    if digits:
                        out.append(int("".join(digits), 8) & 0xFF)
                        index = scan
                        continue
                out.extend(nxt.encode("utf-8"))
                index += 2
                continue
            if char == '"':
                return out.decode("utf-8", "replace"), True
            out.extend(char.encode("utf-8"))
            index += 1
        return out.decode("utf-8", "replace"), False

    def _parse_path(
        self, parsed: ParsedDiff, rest: str, line_no: int
    ) -> tuple[str, str | None]:
        """Parse 'path[\\ttimestamp]'; returns (path, timestamp or None)."""
        path_part, _sep, timestamp = rest.partition("\t")
        if not path_part:
            self._add_finding(parsed, line_no, "E_HEADER_PATH", "header path is empty")
            return "", timestamp or None
        decoded, closed = self._decode_quoted(path_part)
        if not closed:
            self._add_finding(
                parsed, line_no, "E_ESCAPE", "quoted path is missing its closing quote"
            )
        return decoded, timestamp or None

    def _parse(self, text: str) -> ParsedDiff:
        parsed = ParsedDiff()
        lines = self._split_lines(parsed, text)
        total = len(lines)
        index = 0
        while index < total:
            line = lines[index]
            if not line.strip():
                self._add_finding(
                    parsed,
                    index + 1,
                    "W_TRAILING_BLANK",
                    "blank line inside or after the diff was skipped",
                    "warning",
                )
                index += 1
                continue
            if line.startswith("diff --git "):
                section, index = self._parse_git_section(parsed, lines, index)
            elif line.startswith("--- "):
                section, index = self._parse_plain_section(parsed, lines, index)
            else:
                self._add_finding(
                    parsed,
                    index + 1,
                    "E_UNEXPECTED_LINE",
                    f"expected a file header but found: {line[:60]!r}",
                )
                index += 1
                continue
            if section is not None:
                parsed.files.append(section)
            if len(parsed.files) > self.max_files:
                raise ValueError(f"diff exceeds max_files ({self.max_files})")
        return parsed

    @staticmethod
    def _quoted_end(text: str, start: int) -> int | None:
        """Index of the closing quote of the token starting at ``start``, or None."""
        index = start + 1
        while index < len(text):
            if text[index] == "\\":
                index += 2
                continue
            if text[index] == '"':
                return index
            index += 1
        return None

    @classmethod
    def _split_git_pair(cls, rest: str) -> tuple[str, str] | None:
        """Split a ``diff --git`` tail into (left, right) tokens, quotes included.

        Git quotes a side only when it contains characters octal/escape-quoted
        by ``core.quotePath``, so mixed raw/quoted pairs occur, and raw paths
        may contain spaces which git writes unquoted. The boundary is located
        at the first ``' b/'`` separator when present (the same rule GNU
        patch uses to disambiguate), otherwise at the first space.
        """
        if rest.startswith('"'):
            return cls._split_quoted_git_pair(rest)
        boundary = rest.find(" b/")
        if boundary != -1:
            return rest[:boundary], rest[boundary + 1 :]
        if " " in rest:
            left, right = rest.split(" ", 1)
            if right:
                return left, right
        return None

    @classmethod
    def _split_quoted_git_pair(cls, rest: str) -> tuple[str, str] | None:
        """Split a git header tail whose left token starts with a quoted path."""
        end = cls._quoted_end(rest, 0)
        if end is None or rest[end + 1 : end + 2] != " ":
            return None
        right = rest[end + 2 :]
        if not right:
            return None
        if right.startswith('"') and cls._quoted_end(rest, end + 2) != len(rest) - 1:
            return None
        return rest[: end + 1], right

    def _git_paths(self, parsed: ParsedDiff, line: str, line_no: int) -> tuple[str, str]:
        rest = line[len("diff --git ") :]
        pair = self._split_git_pair(rest)
        if pair is None:
            self._add_finding(
                parsed, line_no, "E_UNEXPECTED_LINE", f"malformed git header: {line[:60]!r}"
            )
            return "", ""
        left, closed_l = self._decode_quoted(pair[0])
        right, closed_r = self._decode_quoted(pair[1])
        if not closed_l or not closed_r:
            self._add_finding(
                parsed, line_no, "E_ESCAPE", "quoted path in git header is missing its closing quote"
            )
        return left, right

    def _parse_git_section(
        self, parsed: ParsedDiff, lines: list[str], index: int
    ) -> tuple[FileSection | None, int]:
        section = FileSection(index + 1)
        section.git_paths = self._git_paths(parsed, lines[index], index + 1)
        index += 1
        total = len(lines)
        rename_like = False
        mode_like = False
        while index < total:
            line = lines[index]
            if line.startswith("Binary files ") and line.rstrip().endswith(" differ"):
                section.binary = True
                self._add_finding(
                    parsed,
                    index + 1,
                    "W_BINARY_SKIPPED",
                    f"binary change recognized: {line[:80]}",
                    "warning",
                )
                index += 1
                if index < total and lines[index].startswith("@@ "):
                    self._add_finding(
                        parsed,
                        index + 1,
                        "E_BINARY_WITH_HUNKS",
                        "hunks are not allowed after 'Binary files ... differ'",
                    )
                return section, index
            if line == "GIT binary patch":
                section.binary = True
                self._add_finding(
                    parsed,
                    index + 1,
                    "W_BINARY_SKIPPED",
                    "GIT binary patch payload is recognized and skipped",
                    "warning",
                )
                index += 1
                while index < total and not lines[index].startswith("diff --git "):
                    index += 1
                return section, index
            if line.startswith("--- "):
                return self._parse_plain_section(parsed, lines, index, section)
            if line.startswith("diff --git "):
                if not rename_like and not mode_like:
                    self._add_finding(
                        parsed,
                        section.line_no,
                        "E_HEADER_MISSING",
                        "git file header has no ---/+++ pair, no binary note, no rename/"
                        "copy lines, no mode change, and no hunks",
                    )
                return section, index
            matched = False
            for extra in _GIT_EXTRAS:
                if line.startswith(extra + " "):
                    value = line[len(extra) + 1 :].strip()
                    if value.startswith('"'):
                        value, closed = self._decode_quoted(value)
                        if not closed:
                            self._add_finding(
                                parsed,
                                index + 1,
                                "E_ESCAPE",
                                "quoted rename/copy path is missing its closing quote",
                            )
                    section.extras.append((extra, value))
                    if extra in ("rename from", "rename to", "copy from", "copy to"):
                        rename_like = True
                    if extra in ("old mode", "new mode"):
                        mode_like = True
                    matched = True
                    break
            if not matched:
                self._add_finding(
                    parsed,
                    index + 1,
                    "E_UNEXPECTED_LINE",
                    f"unexpected line inside git file header: {line[:60]!r}",
                )
                return section, index + 1
            index += 1
        if not rename_like and not mode_like and not section.binary:
            self._add_finding(
                parsed,
                section.line_no,
                "E_HEADER_MISSING",
                "git file header has no ---/+++ pair, no binary note, no rename/copy "
                "lines, no mode change, and no hunks",
            )
        return section, index

    def _parse_plain_section(
        self,
        parsed: ParsedDiff,
        lines: list[str],
        index: int,
        section: FileSection | None = None,
    ) -> tuple[FileSection | None, int]:
        if section is None:
            section = FileSection(index + 1)
        total = len(lines)
        section.old_path, section.old_ts = self._parse_path(parsed, lines[index][4:], index + 1)
        index += 1
        if index >= total or not lines[index].startswith("+++ "):
            self._add_finding(
                parsed,
                min(index + 1, total),
                "E_HEADER_ORDER",
                "every '---' header must be immediately followed by a '+++' header",
            )
            return section, min(index, total)
        section.new_path, section.new_ts = self._parse_path(parsed, lines[index][4:], index + 1)
        index += 1
        prev_hunk: Hunk | None = None
        net_lines = 0
        while index < total:
            line = lines[index]
            if line.startswith("@@"):
                hunk, index = self._parse_hunk(parsed, lines, index)
                if hunk is None:
                    continue
                section.hunks.append(hunk)
                if len(section.hunks) > self.max_hunks:
                    raise ValueError(f"diff exceeds max_hunks ({self.max_hunks})")
                if prev_hunk is not None:
                    overlap_limit = prev_hunk.old_start + max(prev_hunk.old_count - 1, 0)
                    if hunk.old_start < prev_hunk.old_start or (
                        prev_hunk.old_count > 0 and hunk.old_start <= overlap_limit
                    ):
                        self._add_finding(
                            parsed,
                            hunk.line_no,
                            "E_HUNK_ORDER",
                            f"hunk old start {hunk.old_start} goes backwards or overlaps the "
                            f"previous hunk (which covers through old line {overlap_limit})",
                        )
                pos_old = hunk.old_start - 1 if hunk.old_count > 0 else hunk.old_start
                pos_new = hunk.new_start - 1 if hunk.new_count > 0 else hunk.new_start
                if pos_new - pos_old != net_lines:
                    expected = pos_old + net_lines + (1 if hunk.new_count > 0 else 0)
                    self._add_finding(
                        parsed,
                        hunk.line_no,
                        "E_HUNK_OFFSET",
                        f"hunk new start {hunk.new_start} is inconsistent with the hunk "
                        f"arithmetic: {net_lines} net line change(s) from earlier hunks "
                        f"place it at {expected}",
                    )
                net_lines += hunk.new_count - hunk.old_count
                prev_hunk = hunk
                continue
            if line.startswith("diff --git ") or line.startswith("--- "):
                break
            if not line.strip():
                self._add_finding(
                    parsed,
                    index + 1,
                    "W_TRAILING_BLANK",
                    "blank line inside or after the diff was skipped",
                    "warning",
                )
                index += 1
                continue
            self._add_finding(
                parsed,
                index + 1,
                "E_BODY_LINE",
                f"expected a hunk header but found: {line[:60]!r}",
            )
            index += 1
        if not section.hunks:
            self._add_finding(
                parsed,
                section.line_no,
                "E_SECTION_EMPTY",
                "file header has no hunks; identical files produce no diff at all",
            )
        self._check_marker_placements(parsed, section)
        return section, index

    def _check_marker_placements(self, parsed: ParsedDiff, section: FileSection) -> None:
        """Enforce that no-newline markers annotate only each side's last line.

        A file line without a trailing newline is necessarily the file's last
        line, so a marker on an old-side line with old-side lines following
        (in the same or a later hunk) is semantically impossible, and
        likewise for the new side. patch(1) rejects such diffs as malformed.
        """
        last_of = {"old": (-1, -1), "new": (-1, -1)}
        for hunk_index, hunk in enumerate(section.hunks):
            for line_index, item in enumerate(hunk.lines):
                if item.origin in (" ", "-"):
                    last_of["old"] = (hunk_index, line_index)
                if item.origin in (" ", "+"):
                    last_of["new"] = (hunk_index, line_index)
        for hunk_index, hunk in enumerate(section.hunks):
            for line_index, item in enumerate(hunk.lines):
                if not item.no_newline:
                    continue
                sides = ("old", "new") if item.origin == " " else (("old",) if item.origin == "-" else ("new",))
                for side in sides:
                    if last_of[side] != (hunk_index, line_index):
                        self._add_finding(
                            parsed,
                            item.line_no,
                            "E_NO_NEWLINE_MARKER",
                            f"'\\ No newline at end of file' cannot mark this {side}-side "
                            f"line: the {side} side continues afterwards, but a line "
                            f"without a trailing newline must be the last line of the file",
                        )

    def _parse_hunk(
        self, parsed: ParsedDiff, lines: list[str], index: int
    ) -> tuple[Hunk | None, int]:
        match = _HUNK_RE.match(lines[index])
        if match is None:
            self._add_finding(
                parsed,
                index + 1,
                "E_HUNK_GRAMMAR",
                f"malformed hunk header: {lines[index][:60]!r}",
            )
            return None, index + 1
        old_start, old_count, new_start, new_count, tail = match.groups()
        hunk = Hunk(
            index + 1,
            int(old_start),
            1 if old_count is None else int(old_count),
            int(new_start),
            1 if new_count is None else int(new_count),
            tail,
        )
        for label, start, count in (
            ("old", hunk.old_start, hunk.old_count),
            ("new", hunk.new_start, hunk.new_count),
        ):
            if start == 0 and count != 0:
                self._add_finding(
                    parsed,
                    hunk.line_no,
                    "E_HUNK_GRAMMAR",
                    f"{label} start 0 is only legal with a zero count (e.g. -0,0 for new files)",
                )
        index += 1
        total = len(lines)
        prev_origin: str | None = None
        prev_marker = False
        while hunk.old_used < hunk.old_count or hunk.new_used < hunk.new_count:
            if index >= total:
                self._count_finding(parsed, hunk)
                return hunk, index
            line = lines[index]
            if line.startswith("\\ No newline"):
                if prev_marker:
                    self._add_finding(
                        parsed,
                        index + 1,
                        "E_NO_NEWLINE_MARKER",
                        "duplicate '\\ No newline' marker for the same body line",
                    )
                elif prev_origin not in (" ", "+", "-"):
                    self._add_finding(
                        parsed,
                        index + 1,
                        "E_NO_NEWLINE_MARKER",
                        "'\\ No newline' must directly follow a ' ', '+' or '-' body line",
                    )
                elif hunk.lines:
                    hunk.lines[-1].no_newline = True
                prev_marker = True
                index += 1
                continue
            origin = line[:1]
            prev_marker = False
            if "\r" in line[1:] and parsed.newline_style != "crlf" and not parsed.cr_warned:
                parsed.cr_warned = True
                self._add_finding(
                    parsed,
                    index + 1,
                    "W_CRLF_CONTENT",
                    "body lines carry CR characters (the diffed file likely has CRLF "
                    "endings); they are compared exactly against the original text",
                    "warning",
                )
            if origin == " ":
                if hunk.old_used >= hunk.old_count or hunk.new_used >= hunk.new_count:
                    self._count_finding(parsed, hunk)
                    return hunk, index
                hunk._consume(BodyLine(" ", line[1:], index + 1))
                prev_origin = " "
            elif origin == "-":
                if hunk.old_used >= hunk.old_count:
                    self._count_finding(parsed, hunk)
                    return hunk, index
                hunk._consume(BodyLine("-", line[1:], index + 1))
                prev_origin = "-"
            elif origin == "+":
                if hunk.new_used >= hunk.new_count:
                    self._count_finding(parsed, hunk)
                    return hunk, index
                hunk._consume(BodyLine("+", line[1:], index + 1))
                prev_origin = "+"
            elif line == "":
                self._add_finding(
                    parsed,
                    index + 1,
                    "E_EMPTY_BODY_LINE",
                    "empty line inside a hunk; an empty context line is a single space",
                )
                hunk._consume(BodyLine(" ", "", index + 1))
                prev_origin = " "
            else:
                if line.startswith(("@@", "diff --git ", "--- ", "+++ ")):
                    self._count_finding(parsed, hunk)
                    return hunk, index
                self._add_finding(
                    parsed,
                    index + 1,
                    "E_BODY_LINE",
                    f"hunk body line must start with ' ', '+' or '-': {line[:60]!r}",
                )
                hunk._consume(BodyLine(" ", line, index + 1))
                prev_origin = " "
            index += 1
        marker_seen = False
        while index < total and lines[index].startswith("\\ No newline"):
            if not marker_seen and hunk.lines:
                hunk.lines[-1].no_newline = True
                marker_seen = True
            else:
                self._add_finding(
                    parsed,
                    index + 1,
                    "E_NO_NEWLINE_MARKER",
                    "duplicate '\\ No newline' marker for the same body line",
                )
            index += 1
        if index < total and lines[index][:1] in (" ", "+", "-") and not lines[index].startswith(
            ("--- ", "+++ ")
        ):
            self._add_finding(
                parsed,
                index + 1,
                "E_EXTRA_BODY_LINE",
                f"body line after hunk counts were already satisfied: {lines[index][:60]!r}",
            )
            index += 1
        return hunk, index

    def _count_finding(self, parsed: ParsedDiff, hunk: Hunk) -> None:
        """Report which side of the hunk arithmetic failed, expected vs actual."""
        if hunk.old_used != hunk.old_count:
            self._add_finding(
                parsed,
                hunk.line_no,
                "E_HUNK_COUNT_OLD",
                f"old side expects {hunk.old_count} line(s) from ' ' and '-' but found "
                f"{hunk.old_used}",
            )
        if hunk.new_used != hunk.new_count:
            self._add_finding(
                parsed,
                hunk.line_no,
                "E_HUNK_COUNT_NEW",
                f"new side expects {hunk.new_count} line(s) from ' ' and '+' but found "
                f"{hunk.new_used}",
            )

    # ------------------------------------------------------------------- modes

    @staticmethod
    def _file_summary(parsed: ParsedDiff) -> dict[str, int]:
        counts = {"added": 0, "deleted": 0, "modified": 0, "renamed": 0, "binary": 0}
        for section in parsed.files:
            key = section.status()
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _validate_result(self, parsed: ParsedDiff) -> dict[str, Any]:
        hunks = sum(len(section.hunks) for section in parsed.files)
        return {
            "status": "success",
            "mode": "validate",
            "valid": not parsed.errors(),
            "files": len(parsed.files),
            "hunks": hunks,
            "findings": parsed.findings,
            "errors": len(parsed.errors()),
            "warnings": len(parsed.warnings()),
            "findings_truncated": parsed.truncated,
            "newline_style": parsed.newline_style,
            "final_newline": parsed.final_newline,
            "summary": self._file_summary(parsed),
        }

    # apply ------------------------------------------------------------

    @staticmethod
    def _split_original(text: str) -> tuple[list[str], bool]:
        if text == "":
            return [], True
        parts = text.split("\n")
        final_newline = text.endswith("\n")
        if final_newline:
            parts.pop()
        return parts, final_newline

    def _simulate(
        self, section: FileSection, original: str, crlf_transport: bool = False
    ) -> tuple[bool, list[dict[str, Any]], str | None, str | None]:
        """Apply every hunk exactly; return (ok, per_hunk, result_text, reason).

        When the diff text itself used uniform CRLF line endings, a single
        trailing CR cannot be attributed to content or transport, so one CR is
        tolerated and re-added at the comparison boundary (patch(1) behaves the
        same way when stripping CRs).

        File-level sections are stricter than patch(1)'s line editing: a
        ``--- /dev/null`` (or ``new file mode``) section asserts the old file
        is empty, so it cannot apply to non-empty text (patch(1) asks "Patch
        creates file that already exists!"); a ``+++ /dev/null`` (or
        ``deleted file mode``) section asserts the result is empty, so
        applying it must consume the original entirely.
        """
        lines, final_newline = self._split_original(original)
        status = section.status()
        if status == "added" and original != "":
            return (
                False,
                [],
                None,
                "old_side_empty_mismatch: the diff creates the file (old side is /dev/null) "
                "but original_text is not empty",
            )
        cr_original = any(item.endswith("\r") for item in lines)

        def normalize_cr(value: str) -> str:
            return value[:-1] if value.endswith("\r") else value

        def content_matches(content: str, line: str) -> bool:
            if content == line:
                return True
            return crlf_transport and normalize_cr(content) == normalize_cr(line)

        def emit(content: str) -> str:
            if crlf_transport and cr_original and not content.endswith("\r"):
                return content + "\r"
            return content

        per_hunk: list[dict[str, Any]] = []
        cursor = 0
        output: list[str] = []
        old_no_newline = False
        new_no_newline = False
        last_line_consumed = False
        for hunk in section.hunks:
            old_no_newline = old_no_newline or hunk.old_side_no_newline()
            new_no_newline = new_no_newline or hunk.new_side_no_newline()
            # Unified diff hunk headers carry original-file coordinates: the
            # old_start of a later hunk already accounts for earlier hunks, so
            # no cumulative offset may be applied when locating it.
            pos = hunk.old_start - 1 if hunk.old_count > 0 else hunk.old_start
            pos = max(pos, cursor)
            entry: dict[str, Any] = {
                "index": len(per_hunk) + 1,
                "applies": True,
                "old_start": hunk.old_start,
                "new_start": hunk.new_start,
                "context_matches": True,
                "first_mismatch_line": None,
            }
            mismatch: int | None = None
            walk = pos
            for item in hunk.lines:
                if item.origin == "+":
                    continue
                if walk >= len(lines) or not content_matches(item.content, lines[walk]):
                    mismatch = min(walk + 1, len(lines) + 1)
                    break
                walk += 1
            if mismatch is not None:
                entry["applies"] = False
                entry["context_matches"] = False
                entry["first_mismatch_line"] = mismatch
                per_hunk.append(entry)
                return False, per_hunk, None, "context_mismatch"
            if hunk.old_used > 0 and pos < len(lines) and pos + hunk.old_used >= len(lines):
                last_line_consumed = True
            output.extend(lines[cursor:pos])
            for item in hunk.lines:
                if item.origin != "-":
                    output.append(emit(item.content))
            cursor = pos + hunk.old_used
            per_hunk.append(entry)
        if lines:
            if old_no_newline and final_newline:
                return (
                    False,
                    per_hunk,
                    None,
                    "newline_marker_mismatch: diff says the old side lacks a final newline "
                    "but the original text has one",
                )
            if last_line_consumed and not final_newline and not old_no_newline:
                return (
                    False,
                    per_hunk,
                    None,
                    "newline_marker_mismatch: the diff rewrites the last line as newline-"
                    "terminated but the original text lacks a final newline",
                )
        output.extend(lines[cursor:])
        if status == "deleted" and output:
            return (
                False,
                per_hunk,
                None,
                f"new_side_empty_mismatch: the diff deletes the file (new side is /dev/null) "
                f"but applying it leaves {len(output)} line(s) unconsumed",
            )
        if new_no_newline:
            final_result = False
        elif last_line_consumed:
            final_result = True
        else:
            final_result = final_newline
        result = "\n".join(output)
        if output and final_result:
            result += "\n"
        return True, per_hunk, result, None

    def _apply_check(self, parsed: ParsedDiff, original_text: Any) -> dict[str, Any]:
        original = self._optional_text("original_text", original_text)
        if original is None:
            raise ValueError("apply_check requires original_text")
        base = {
            "status": "success",
            "mode": "apply_check",
            "findings": parsed.findings[: self.max_findings],
        }
        if parsed.errors():
            return {
                **base,
                "applies": False,
                "reject_reason": "invalid_diff",
                "per_hunk": [],
            }
        if len(parsed.files) > 1:
            paths = []
            for section in parsed.files:
                old_norm, new_norm = section.normalized_paths()
                paths.append(new_norm or old_norm or section.old_path or "")
            return self._error(
                "multi_file_diff",
                "apply_check accepts single-file diffs only; this diff touches "
                f"{len(parsed.files)} files",
                files=paths[:20],
                files_total=len(paths),
            )
        section = parsed.files[0]
        if section.binary:
            return {**base, "applies": False, "reject_reason": "binary_section", "per_hunk": []}
        if not section.hunks:
            return {**base, "applies": True, "reject_reason": None, "per_hunk": []}
        applies, per_hunk, _result, reason = self._simulate(
            section, original, crlf_transport=parsed.newline_style == "crlf"
        )
        return {
            **base,
            "applies": applies,
            "reject_reason": reason,
            "per_hunk": per_hunk,
        }

    # reverse ----------------------------------------------------------

    @staticmethod
    def _range_token(start: int, count: int, sign: str) -> str:
        if count == 1:
            return f"{sign}{start}"
        return f"{sign}{start},{count}"

    def _reverse_text(self, parsed: ParsedDiff) -> tuple[str, list[dict[str, Any]]]:
        newline = "\r\n" if parsed.newline_style == "crlf" else "\n"
        skipped: list[dict[str, Any]] = []
        chunks: list[str] = []
        for section in parsed.files:
            old_norm, new_norm = section.normalized_paths()
            label = new_norm or old_norm
            if section.binary:
                skipped.append({"file": label, "reason": "binary_section"})
                continue
            if not section.hunks:
                skipped.append({"file": label, "reason": "no_hunks (rename or mode only)"})
                continue
            chunks.append(
                f"--- {section.new_path}"
                + (f"\t{section.new_ts}" if section.new_ts is not None else "")
                + newline
            )
            chunks.append(
                f"+++ {section.old_path}"
                + (f"\t{section.old_ts}" if section.old_ts is not None else "")
                + newline
            )
            for hunk in section.hunks:
                old_token = self._range_token(hunk.new_start, hunk.new_count, "-")
                new_token = self._range_token(hunk.old_start, hunk.old_count, "+")
                chunks.append(f"@@ {old_token} {new_token} @@{hunk.section}{newline}")
                for item in hunk.lines:
                    swapped = {"+": "-", "-": "+", " ": " "}[item.origin]
                    chunks.append(f"{swapped}{item.content}{newline}")
                    if item.no_newline:
                        chunks.append(f"{_MARKER}{newline}")
        if not chunks:
            reasons = "; ".join(f"{item['file']}: {item['reason']}" for item in skipped)
            raise ValueError(f"nothing to reverse: {reasons}")
        text = "".join(chunks)
        if not parsed.final_newline and text.endswith(newline):
            text = text[: -len(newline)]
        return text, skipped

    def _reverse_result(self, parsed: ParsedDiff, new_text: Any) -> dict[str, Any]:
        fresh = self._optional_text("new_text", new_text)
        if parsed.errors():
            return {
                "status": "success",
                "mode": "reverse",
                "diff": None,
                "valid": False,
                "round_trip": None,
                "skipped": [],
                "findings": parsed.findings[: self.max_findings],
            }
        text, skipped = self._reverse_text(parsed)
        reparsed = self._parse(text)
        valid = not reparsed.errors()
        result: dict[str, Any] = {
            "status": "success",
            "mode": "reverse",
            "diff": text,
            "valid": valid,
            "round_trip": None,
            "skipped": skipped,
            "git_headers_dropped": sum(len(section.extras) for section in parsed.files),
            "findings": reparsed.findings[: self.max_findings],
        }
        if fresh is None or not valid or len(parsed.files) > 1:
            return result
        applies, _per_hunk, produced, _reason = self._simulate(
            reparsed.files[0], fresh, crlf_transport=reparsed.newline_style == "crlf"
        )
        if not applies or produced is None:
            result["round_trip"] = False
            return result
        applies_forward, _entries, regenerated, _why = self._simulate(
            parsed.files[0], produced, crlf_transport=parsed.newline_style == "crlf"
        )
        result["round_trip"] = bool(applies_forward and regenerated == fresh)
        return result

    # stats ------------------------------------------------------------

    def _stats_result(self, parsed: ParsedDiff) -> dict[str, Any]:
        files: list[dict[str, Any]] = []
        hotspots: list[dict[str, Any]] = []
        totals = {"files": 0, "hunks": 0, "add_lines": 0, "del_lines": 0, "net": 0}
        for section in parsed.files:
            adds = sum(1 for hunk in section.hunks for item in hunk.lines if item.origin == "+")
            dels = sum(1 for hunk in section.hunks for item in hunk.lines if item.origin == "-")
            old_norm, new_norm = section.normalized_paths()
            files.append(
                {
                    "path_old": old_norm,
                    "path_new": new_norm,
                    "status": section.status(),
                    "hunks": len(section.hunks),
                    "add_lines": adds,
                    "del_lines": dels,
                    "net": adds - dels,
                }
            )
            totals["files"] += 1
            totals["hunks"] += len(section.hunks)
            totals["add_lines"] += adds
            totals["del_lines"] += dels
            totals["net"] += adds - dels
            label = new_norm or old_norm or section.old_path or ""
            for hunk_index, hunk in enumerate(section.hunks):
                changed = sum(1 for item in hunk.lines if item.origin in ("+", "-"))
                hotspots.append(
                    {
                        "file": label,
                        "hunk_index": hunk_index + 1,
                        "old_range": (
                            [hunk.old_start, hunk.old_start + hunk.old_count - 1]
                            if hunk.old_count
                            else [hunk.old_start + 1, hunk.old_start]
                        ),
                        "new_range": (
                            [hunk.new_start, hunk.new_start + hunk.new_count - 1]
                            if hunk.new_count
                            else [hunk.new_start + 1, hunk.new_start]
                        ),
                        "changed_lines": changed,
                    }
                )
        hotspots.sort(key=lambda item: (-item["changed_lines"], item["file"], item["hunk_index"]))
        return {
            "status": "success",
            "mode": "stats",
            "files": files,
            "totals": totals,
            "hotspots": hotspots[:3],
            "findings": parsed.findings[: self.max_findings],
        }

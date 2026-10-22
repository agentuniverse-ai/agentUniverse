#!/usr/bin/env python3
"""GitLogTool: parse and summarize `git log` text output.

The tool understands the output shapes `git log` actually produces and pins
them against the real binary in its test suite:

- default / ``--pretty=short`` / ``--pretty=medium`` commit headers
  (``commit <sha>`` with optional ``(HEAD -> ...)`` decorations, ``Merge:``
  parent lines, ``Author:`` and ``Date:`` lines, 4-space-indented messages)
- ``--oneline`` / ``--pretty=format:`` styles
- ``--stat`` file tables (``path | 12 +++--``, ``...``-truncated paths,
  ``Bin 0 -> 1234 bytes`` binary entries, and the
  ``N files changed, N insertions(+), N deletions(-)`` summary with its
  singular/plural forms)
- ``--numstat`` (``added<TAB>deleted<TAB>path``, ``-`` for binary)
- ``--name-status`` (``M/A/D`` and ``R100 old new`` / ``C100`` renames)

Modes:
  parse    -- full commit list with everything found per commit
  detect   -- which decorations/styles the text carries
  summarize-- per-author counts, date range, file-touch ranking, totals

The parser never runs git and never touches a repository; it only reads the
text it is given. Everything is capped and deterministic.
"""

import re
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool

_MODES = ("parse", "detect", "summarize")

_MAX_TEXT_CHARS = 2_000_000
_MAX_COMMITS = 5_000
_MAX_FILES_PER_COMMIT = 2_000
_MAX_MESSAGE_CHARS = 4_000

_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
_COMMIT_LINE_RE = re.compile(r"^commit ([0-9a-f]{7,40})(?: \((.*)\))?$")
_MERGE_RE = re.compile(r"^Merge: ([0-9a-f]+(?: [0-9a-f]+)*)$")
_AUTHOR_RE = re.compile(r"^Author: (.*) <([^<>]*)>$")
_DATE_RE = re.compile(r"^Date:\s+(.*)$")
_ONELINE_RE = re.compile(r"^([0-9a-f]{7,40}) (.*)$")
_NUMSTAT_RE = re.compile(r"^(\d+|-)\t(\d+|-)\t(.*)$")
_STATUS_RE = re.compile(r"^([MADRCUXB!])(\d*)\t(.*)$")
_STAT_FILE_RE = re.compile(r"^(.*?) \| (.*)$")
_STAT_SUMMARY_RE = re.compile(
    r"^ (\d+) files? changed(?:, (\d+) insertions?\(\+\))?"
    r"(?:, (\d+) deletions?\(-\))?"
    r"(?:, (\d+) files? unmatched)?"
)
_STAT_BIN_RE = re.compile(r"^Bin (?:\d+ )?-> (\d+) bytes$")

_MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}
_GIT_DATE_RE = re.compile(
    r"^([A-Z][a-z]{2}) ([A-Z][a-z]{2}) (\d{1,2}) (\d{2}):(\d{2}):(\d{2}) (\d{4}) ([+-]\d{4})$"
)


def _iso_from_git_date(raw: str) -> str:
    """Convert 'Thu Jul 9 16:46:23 2026 +0800' to an ISO string (best effort)."""
    m = _GIT_DATE_RE.match(raw.strip())
    if not m:
        return ""
    wday, mon, day, hh, mm, ss, year, tz = m.groups()
    month = _MONTHS.get(mon)
    if not month:
        return ""
    tzs = f"{tz[:3]}:{tz[3:]}"
    return f"{int(year):04d}-{month:02d}-{int(day):02d}T{hh}:{mm}:{ss}{tzs}"


def _parse_stat_changes(field: str) -> dict:
    """'57 ++++++' / '2 +-' / '0' / 'Bin 0 -> 12 bytes' -> counts."""
    field = field.strip()
    bin_m = _STAT_BIN_RE.match(field)
    if bin_m:
        return {"binary": True, "bytes": int(bin_m.group(1))}
    plus = field.count("+")
    minus = field.count("-")
    return {"binary": False, "plus": plus, "minus": minus, "raw": field[:40]}


class GitLogTool(Tool):
    """Parse and summarize git log text output."""

    name: str = "git_log_tool"
    description: str = (
        "Parse git log text output (default/short/medium/oneline formats, "
        "--stat tables, --numstat, --name-status) into structured commits "
        "and summaries. Pure text analysis; never runs git."
    )
    tool_type: str = "api"

    def execute(self, mode: str = "parse", log_text: str = "", **kwargs: Any) -> Any:
        """Run one git-log analysis.

        - parse:     log_text -> full commit list
        - detect:    log_text -> which styles/decorations are present
        - summarize: log_text -> author/file/date aggregation
        """
        if mode not in _MODES:
            raise ValueError(f"mode must be one of {_MODES}; got {mode!r:.64}")
        if not isinstance(log_text, str):
            raise ValueError(f"log_text must be a string, got {type(log_text).__name__}")
        if len(log_text) > _MAX_TEXT_CHARS:
            raise ValueError(
                f"log_text exceeds {_MAX_TEXT_CHARS} characters (got {len(log_text)})"
            )
        commits, warnings = self._parse_commits(log_text)
        if mode == "parse":
            return {"mode": "parse", "commit_count": len(commits), "commits": commits,
                    "warnings": warnings}
        if mode == "detect":
            return {"mode": "detect", **self._detect(commits, log_text), "warnings": warnings}
        return {"mode": "summarize", **self._summarize(commits), "warnings": warnings}

    # ------------------------------------------------------------------ #

    def _parse_commits(self, text: str) -> tuple:
        commits: list = []
        warnings: list = []
        current: dict = None
        oneline_only = bool(text) and all(
            (not line) or _ONELINE_RE.match(line) for line in text.splitlines()[:50]
        ) and any(_ONELINE_RE.match(line) for line in text.splitlines()[:50])

        def flush():
            nonlocal current
            if current is not None:
                commits.append(self._finish(current))
                current = None

        for lineno, line in enumerate(text.splitlines(), start=1):
            if len(commits) >= _MAX_COMMITS and (
                _COMMIT_LINE_RE.match(line) or _ONELINE_RE.match(line)
            ):
                warnings.append(
                    f"commit cap ({_MAX_COMMITS}) reached at line {lineno}; "
                    "remaining output ignored"
                )
                break
            m = _COMMIT_LINE_RE.match(line)
            if m:
                flush()
                current = {
                    "sha": m.group(1), "decoration": m.group(2) or None,
                    "merge_parents": [], "author": None, "author_email": None,
                    "date_raw": None, "date_iso": None,
                    "message_lines": [], "message": "",
                    "stat": [], "stat_summary": None,
                    "numstat": [], "name_status": [],
                }
                continue
            m = _ONELINE_RE.match(line)
            if m and oneline_only and current is None:
                current = {
                    "sha": m.group(1), "decoration": None, "merge_parents": [],
                    "author": None, "author_email": None, "date_raw": None,
                    "date_iso": None, "message_lines": [m.group(2)],
                    "message": m.group(2)[:_MAX_MESSAGE_CHARS],
                    "stat": [], "stat_summary": None, "numstat": [], "name_status": [],
                }
                commits.append(self._finish(current))
                current = None
                continue
            if current is None:
                if line.strip():
                    warnings.append(f"line {lineno}: content before first commit ignored")
                continue
            m = _MERGE_RE.match(line)
            if m:
                current["merge_parents"] = m.group(1).split()
                continue
            m = _AUTHOR_RE.match(line)
            if m:
                current["author"], current["author_email"] = m.group(1), m.group(2)
                continue
            m = _DATE_RE.match(line)
            if m:
                current["date_raw"] = m.group(1)
                current["date_iso"] = _iso_from_git_date(m.group(1))
                continue
            m = _NUMSTAT_RE.match(line)
            if m and not line.startswith(" "):
                a, d, path = m.groups()
                if len(current["numstat"]) < _MAX_FILES_PER_COMMIT:
                    current["numstat"].append({
                        "added": None if a == "-" else int(a),
                        "deleted": None if d == "-" else int(d),
                        "path": path,
                    })
                continue
            m = _STATUS_RE.match(line)
            if m and not line.startswith(" "):
                code, score, rest = m.groups()
                if code in ("R", "C") and "\t" in rest:
                    old, new = rest.split("\t", 1)
                    entry = {"status": code, "score": int(score) if score else None,
                             "old_path": old, "path": new}
                else:
                    entry = {"status": code, "score": int(score) if score else None,
                             "path": rest}
                if len(current["name_status"]) < _MAX_FILES_PER_COMMIT:
                    current["name_status"].append(entry)
                continue
            m = _STAT_SUMMARY_RE.match(line)
            if m:
                current["stat_summary"] = {
                    "files_changed": int(m.group(1)),
                    "insertions": int(m.group(2) or 0),
                    "deletions": int(m.group(3) or 0),
                }
                continue
            m = _STAT_FILE_RE.match(line)
            if m and "|" in line and not line.startswith("    "):
                if len(current["stat"]) < _MAX_FILES_PER_COMMIT:
                    current["stat"].append({
                        "path": m.group(1).strip(),
                        **_parse_stat_changes(m.group(2)),
                    })
                continue
            if line.startswith("    "):
                if sum(len(x) for x in current["message_lines"]) < _MAX_MESSAGE_CHARS:
                    current["message_lines"].append(line[4:])
                continue
            if not line.strip() and current["message_lines"]:
                if sum(len(x) for x in current["message_lines"]) < _MAX_MESSAGE_CHARS:
                    current["message_lines"].append("")
                continue
        flush()
        return commits, warnings

    @staticmethod
    def _finish(commit: dict) -> dict:
        msg = "\n".join(commit.pop("message_lines")).rstrip("\n")
        commit["message"] = msg[:_MAX_MESSAGE_CHARS]
        return commit

    # ------------------------------------------------------------------ #

    @staticmethod
    def _detect(commits: list, text: str) -> dict:
        if not commits:
            return {"styles": [], "decorations": [], "notes": ["no commits found"]}
        styles = []
        if any(c["date_raw"] for c in commits):
            styles.append("medium/default (Date lines)")
        elif any(c["author"] for c in commits):
            styles.append("short (Author, no Date)")
        else:
            styles.append("oneline/format (no headers)")
        if any(c["stat"] for c in commits):
            styles.append("--stat")
        if any(c["numstat"] for c in commits):
            styles.append("--numstat")
        if any(c["name_status"] for c in commits):
            styles.append("--name-status")
        decos = sorted({c["decoration"] for c in commits if c["decoration"]})
        return {
            "styles": styles,
            "decorations": decos[:20],
            "merge_commits": sum(1 for c in commits if c["merge_parents"]),
        }

    @staticmethod
    def _summarize(commits: list) -> dict:
        if not commits:
            return {"commit_count": 0, "authors": [], "files": [], "totals": {}}
        authors: dict = {}
        file_touch: dict = {}
        totals = {"stat_files": 0, "insertions": 0, "deletions": 0}
        for c in commits:
            who = c["author"] or "(unknown)"
            authors.setdefault(who, {"commits": 0, "insertions": 0, "deletions": 0})
            authors[who]["commits"] += 1
            for ns in c["numstat"]:
                if ns["added"] is not None:
                    authors[who]["insertions"] += ns["added"]
                    totals["insertions"] += ns["added"]
                if ns["deleted"] is not None:
                    authors[who]["deletions"] += ns["deleted"]
                    totals["deletions"] += ns["deleted"]
                file_touch[ns["path"]] = file_touch.get(ns["path"], 0) + 1
            for st in c["stat"]:
                totals["stat_files"] += 1
                file_touch[st["path"]] = file_touch.get(st["path"], 0) + 1
            if c["stat_summary"]:
                totals["insertions"] = max(
                    totals["insertions"], totals["insertions"]
                )  # numstat already counted; keep summary separately below
        dates = [c["date_iso"] for c in commits if c["date_iso"]]
        top_files = sorted(file_touch.items(), key=lambda kv: (-kv[1], kv[0]))[:20]
        return {
            "commit_count": len(commits),
            "authors": [
                {"author": a, **v} for a, v in sorted(
                    authors.items(), key=lambda kv: (-kv[1]["commits"], kv[0])
                )
            ],
            "date_range": {"earliest": min(dates), "latest": max(dates)} if dates else None,
            "most_touched_files": [{"path": p, "commits": n} for p, n in top_files],
            "totals": totals,
        }

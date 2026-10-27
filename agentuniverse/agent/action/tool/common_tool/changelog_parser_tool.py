#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: changelog_parser_tool.py

"""Keep-a-Changelog style markdown changelog parser (pure stdlib).

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency parser that turns a
``CHANGELOG.md`` document into structured release objects. The sibling
``SemverTool`` performs version *arithmetic*; this tool handles the
*document* around the versions and supports three modes:

* ``parse`` — the full releases list. Version headings are ``##``
  (ATX) lines in any of the forms ``## [1.2.3] - 2024-01-15``
  (Keep-a-Changelog link-reference style), ``## 1.2.3 - 2024-01-15``
  (bare) or ``## v1.2.3 - 2024-01-15`` (``v`` prefix); the optional
  ``v`` prefix is stripped and the special section ``## [Unreleased]``
  (any case) is normalized to ``Unreleased``. Versions follow SemVer
  2.0.0 (``X.Y.Z`` core with optional prerelease/build and no leading
  zeros). The release date is the first ISO ``YYYY-MM-DD`` group in
  the heading remainder and must be a real calendar date. Sections are
  the ``###`` headings under a release — the six Keep-a-Changelog
  names (Added / Changed / Deprecated / Removed / Fixed / Security)
  carry no extra semantics and any other name is preserved verbatim;
  names are kept exactly as written, in document order, and repeated
  headings merge. Entries are the bullet lines (``-``, ``*`` or
  ``+``) under a section, flattened in document order with an
  ``indent`` level of ``leading whitespace length // 2`` (nested
  bullets are not tree-ified). A release is ``yanked`` when the
  heading remainder contains the marker ``YANKED`` (case-insensitive)
  or when the matching link-reference definition title does.
  Link-reference definitions (``[1.2.3]: https://…`` with an optional
  ``(title)``) are parsed anywhere in the document and attached to
  the release with the same normalized version as its ``url``;
  unmatched keys are ignored and the first definition of a duplicate
  key wins. The first release listed in the document is flagged
  ``latest: true`` — the document's listing order is authoritative
  even when dates or version numbers disagree with it, and the flag
  lands on ``Unreleased`` when that section is listed first.
* ``latest`` — just the newest semver release (the first one listed,
  per the same document-order rule) with its sections; ``Unreleased``
  is skipped.
* ``between`` — the releases whose versions compare strictly greater
  than ``from_version`` and less than or equal to ``to_version``
  (SemVer 2.0.0 precedence: numeric core, prerelease < release,
  numeric prerelease identifiers compare numerically, build metadata
  ignored), returned in document order; ``Unreleased`` is excluded.

Ignored content: the preamble (anything before the first version
heading), ``#`` / ``###``-and-deeper headings outside a release, prose
lines, horizontal rules, and bullets that appear before the first
section of a release. Fenced code blocks are not treated specially (a
``##`` inside a fence is parsed as a heading). A ``##`` heading that
is not a release heading terminates the release currently being
parsed, so nothing after it is attributed to that release.

Input validation is strict and happens before any parsing: wrong
``mode``, missing / mistyped / empty / oversized ``text`` (over
100,000 characters), a missing or invalid SemVer ``from_version`` /
``to_version``, or a ``to_version`` that is not strictly greater than
``from_version`` raise a ``ValueError``, mirroring the other common
tools. Content-level failures are returned as structured ``error``
payloads instead: a document with no release headings at all
(``no_releases``), the ``latest`` mode on a document whose only
release is ``Unreleased`` (``no_semver_releases``), and a release
heading whose date is not a valid calendar date such as ``2024-02-30``
(``invalid_date``).
"""

import datetime
import re
from functools import total_ordering
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Strict SemVer 2.0.0 grammar with an optional lowercase "v" prefix.
_SEMVER_RE = re.compile(
    r"^v?(\d+)\.(\d+)\.(\d+)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_NUMERIC_RE = re.compile(r"\A\d+\Z")

# ATX headings: exactly two / three hashes followed by whitespace.
_H2_RE = re.compile(r"^##(?!#)[ \t]+(?P<title>\S.*?)[ \t]*$")
_H3_RE = re.compile(r"^###[ \t]+(?P<title>\S.*?)[ \t]*$")

# "## [1.2.3] - 2024-01-15" — bracketed version token plus remainder.
_BRACKET_TITLE_RE = re.compile(r"^\[(?P<inner>[^\]]+)\](?P<rest>.*)$")
# "## 1.2.3 - 2024-01-15" / "## v1.2.3" — bare version token; the
# remainder must start with whitespace or be empty (a token like
# "1.2.3.4" must not half-match as "1.2.3").
_BARE_TITLE_RE = re.compile(
    r"^v?(?P<ver>\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]*)?)(?P<rest>.*)$"
)
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
# Markdown link reference definition: "[1.2.3]: https://… (Title)".
_LINK_DEF_RE = re.compile(
    r"^\[(?P<key>[^\]]+)\]:[ \t]*(?P<url>\S+)"
    r"(?:[ \t]+\((?P<title>[^)]*)\))?[ \t]*$"
)
# Bullet item: optional leading whitespace, one of -/*/+ and text.
_BULLET_RE = re.compile(r"^(?P<ws>[ \t]*)[-*+](?:[ \t]+(?P<text>.*))?$")
# Horizontal rule / thematic break (three or more of the same marker
# character, optionally separated by spaces — CommonMark allows
# "* * *" and "- - -" just as much as "***" and "---").
_HR_RE = re.compile(r"[ \t]*([-=*_])(?:[ \t]*\1){2,}[ \t]*$")


@total_ordering
class _SemVer:
    """A strictly validated semantic version (SemVer 2.0.0).

    Build metadata is parsed and preserved in ``canonical`` but, per
    the specification, ignored by every comparison.
    """

    __slots__ = ("major", "minor", "patch", "prerelease", "build", "canonical")

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: tuple,
        build: str,
        canonical: str,
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build
        self.canonical = canonical

    @classmethod
    def parse(cls, value: Any) -> Any:
        """Parse ``value`` into a ``_SemVer``, or return ``None``.

        Accepts a string with optional surrounding whitespace and an
        optional lowercase ``v`` prefix; rejects anything that is not
        strict SemVer 2.0.0, including leading zeros in the numeric
        core or in numeric prerelease identifiers.
        """
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            return None
        match = _SEMVER_RE.match(value.strip())
        if match is None:
            return None
        major_s, minor_s, patch_s, prerelease, build = match.groups()
        # Numeric core identifiers must not carry leading zeros.
        if any(len(part) > 1 and part[0] == "0" for part in (major_s, minor_s, patch_s)):
            return None
        prerelease_ids = tuple(prerelease.split(".")) if prerelease else ()
        for identifier in prerelease_ids:
            if (
                _NUMERIC_RE.match(identifier)
                and len(identifier) > 1
                and identifier[0] == "0"
            ):
                return None
        canonical = f"{major_s}.{minor_s}.{patch_s}"
        if prerelease:
            canonical += f"-{prerelease}"
        if build:
            canonical += f"+{build}"
        return cls(
            int(major_s), int(minor_s), int(patch_s), prerelease_ids, build or "", canonical
        )

    def _core(self) -> tuple:
        return (self.major, self.minor, self.patch)

    def __eq__(self, other: Any) -> Any:
        if not isinstance(other, _SemVer):
            return NotImplemented
        return self._core() == other._core() and self.prerelease == other.prerelease

    def __lt__(self, other: Any) -> Any:
        if not isinstance(other, _SemVer):
            return NotImplemented
        if self._core() != other._core():
            return self._core() < other._core()
        if self.prerelease == other.prerelease:
            return False
        if not self.prerelease:
            # A release outranks any of its prereleases.
            return False
        if not other.prerelease:
            return True
        for left, right in zip(self.prerelease, other.prerelease):
            if left == right:
                continue
            left_num = bool(_NUMERIC_RE.match(left))
            right_num = bool(_NUMERIC_RE.match(right))
            if left_num and right_num:
                return int(left) < int(right)
            if left_num:
                return True  # Numeric identifiers sort below alphanumeric ones.
            if right_num:
                return False
            return left < right
        # All shared identifiers equal: the shorter list is lower.
        return len(self.prerelease) < len(other.prerelease)

    def __hash__(self) -> int:
        return hash((self._core(), self.prerelease))


class _InvalidChangelogDate(Exception):
    """Internal signal: a release heading carries a malformed date."""

    def __init__(self, version: str, date_text: str) -> None:
        super().__init__(version, date_text)
        self.version = version
        self.date_text = date_text


class ChangelogParserTool(Tool):
    """Markdown changelog parser built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input
            length; longer documents are rejected before any parsing.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "changelog_parser_tool"
    description: str = (
        "Changelog parser tool — pure Python stdlib, no network "
        "required. Parses Keep-a-Changelog style markdown documents "
        "into structured releases (mode='parse': version headings "
        "'## [1.2.3]' / '## 1.2.3' / '## v1.2.3' plus [Unreleased], "
        "ISO dates, Added/Changed/Deprecated/Removed/Fixed/Security "
        "and free-form ### sections, flattened bullet entries with "
        "indent levels, yanked markers and link-reference URLs, "
        "latest flag on the first release listed), returns the newest "
        "semver release with its entries (mode='latest'), or the "
        "releases strictly after from_version up to and including "
        "to_version (mode='between')."
    )

    MODES: ClassVar[tuple] = ("parse", "latest", "between")
    UNRELEASED: ClassVar[str] = "Unreleased"

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        text: Any = None,
        from_version: Any = None,
        to_version: Any = None,
    ) -> dict[str, Any]:
        """Run one changelog parsing operation.

        Args:
            mode (str): One of ``parse`` / ``latest`` / ``between``.
            text (str): The markdown changelog document. Required for
                every mode.
            from_version (str): ``between`` mode only — a SemVer string
                    (optional leading ``v``); only releases comparing
                    strictly greater than it are returned.
            to_version (str): ``between`` mode only — a SemVer string
                (optional leading ``v``); releases up to and including
                it are returned. Must be strictly greater than
                ``from_version``.

        Returns:
            Dict[str, Any]: The parsed releases (always a ``releases``
            list for ``parse`` / ``between`` plus the call context, or
            a single ``release`` object for ``latest``) or a
            structured ``error`` payload for content-level failures
            (no release headings, no semver release for ``latest``,
            invalid calendar date in a heading).

        Raises:
            ValueError: If any parameter is malformed (before any
                parsing happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "between":
            clean_from = self._validate_version_arg(from_version, "from_version")
            clean_to = self._validate_version_arg(to_version, "to_version")
            if _SemVer.parse(clean_to) <= _SemVer.parse(clean_from):
                self._invalid(
                    "to_version must be strictly greater than from_version "
                    f"(got from_version={clean_from!r}, to_version={clean_to!r})"
                )
        try:
            releases = self._parse_document(clean_text)
        except _InvalidChangelogDate as exc:
            return self._error_result(
                {"mode": mode},
                error_type="invalid_date",
                message=(
                    f"release heading for {exc.version!r} carries date "
                    f"{exc.date_text!r} which is not a valid ISO calendar "
                    "date (YYYY-MM-DD)"
                ),
            )
        if not releases:
            return self._error_result(
                {"mode": mode},
                error_type="no_releases",
                message=(
                    "no release headings found in the document — expected "
                    "'## [1.2.3]', '## 1.2.3' or '## v1.2.3' headings "
                    "(optionally with an ISO date) or '## [Unreleased]'"
                ),
            )
        if mode == "parse":
            return {
                "mode": "parse",
                "release_count": len(releases),
                "releases": releases,
            }
        if mode == "latest":
            for release in releases:
                if release["version"] != self.UNRELEASED:
                    return {"mode": "latest", "release": release}
            return self._error_result(
                {"mode": "latest"},
                error_type="no_semver_releases",
                message=(
                    "the document contains no semver release — only "
                    f"{self.UNRELEASED!r}; the latest mode requires at "
                    "least one '## <version>' release heading"
                ),
            )
        # mode == "between": (from_version, to_version] in document order.
        from_semver = _SemVer.parse(clean_from)
        to_semver = _SemVer.parse(clean_to)
        selected = [
            release
            for release in releases
            if (semver := _SemVer.parse(release["version"])) is not None
            and from_semver < semver <= to_semver
        ]
        return {
            "mode": "between",
            "from_version": clean_from,
            "to_version": clean_to,
            "release_count": len(selected),
            "releases": selected,
        }

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any parsing)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"changelog_parser_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` (the changelog document)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_version_arg(cls, value: Any, label: str) -> str:
        """Validate a ``between``-mode boundary as strict SemVer."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(
                f"{label} must be a semantic version string for the between "
                f"mode (got {value!r})"
            )
        parsed = _SemVer.parse(value)
        if parsed is None:
            cls._invalid(
                f"{label} must be a valid semantic version (X.Y.Z with "
                "optional prerelease/build and optional leading 'v') "
                f"(got {value!r})"
            )
        return parsed.canonical

    # ------------------------------------------------------------------ #
    # Document parsing
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_version_heading(cls, title: str) -> Any:
        """Classify an ``##`` heading title.

        Returns a ``(version, date, yanked)`` tuple for a release
        heading, or ``None`` for any other ``##`` heading. Raises
        ``_InvalidChangelogDate`` when the heading names a release
        whose date is not a real calendar date.
        """
        version_token = None
        rest = ""
        bracket = _BRACKET_TITLE_RE.match(title)
        if bracket is not None:
            version_token = bracket.group("inner").strip()
            rest = bracket.group("rest")
        else:
            bare = _BARE_TITLE_RE.match(title)
            if bare is not None:
                trailing = bare.group("rest")
                if trailing == "" or trailing[0] in " \t":
                    version_token = bare.group("ver")
                    rest = trailing
        if version_token is None:
            return None
        if version_token.lower() == cls.UNRELEASED.lower():
            version = cls.UNRELEASED
        else:
            semver = _SemVer.parse(version_token)
            if semver is None:
                return None
            version = semver.canonical
        yanked = "yanked" in rest.lower()
        date = None
        date_match = _DATE_RE.search(rest)
        if date_match is not None:
            date = date_match.group(1)
            try:
                datetime.date.fromisoformat(date)
            except ValueError:
                raise _InvalidChangelogDate(version, date) from None
        return version, date, yanked

    @classmethod
    def _normalize_link_key(cls, key: str) -> Any:
        """Normalize a link-reference key to a release version."""
        key = key.strip()
        if key.lower() == cls.UNRELEASED.lower():
            return cls.UNRELEASED
        semver = _SemVer.parse(key)
        return semver.canonical if semver is not None else None

    @classmethod
    def _parse_document(cls, text: str) -> list:
        """Parse the document into a list of release dictionaries.

        Every release dictionary has exactly the keys ``version``,
        ``date``, ``yanked``, ``url``, ``latest`` and ``sections``
        (a mapping of section name to a list of
        ``{"text": str, "indent": int}`` entries, in document order).
        """
        releases: list = []
        link_refs: dict = {}
        current: Any = None
        sections: Any = None
        current_section: Any = None

        for line in text.splitlines():
            h2 = _H2_RE.match(line)
            if h2 is not None:
                parsed = cls._parse_version_heading(h2.group("title"))
                if parsed is None:
                    # Non-release "##" heading: end the current release.
                    current = None
                    sections = None
                    current_section = None
                    continue
                version, date, yanked = parsed
                current = {
                    "version": version,
                    "date": date,
                    "yanked": yanked,
                    "url": None,
                    "latest": False,
                    "sections": {},
                }
                releases.append(current)
                sections = current["sections"]
                current_section = None
                continue

            link = _LINK_DEF_RE.match(line)
            if link is not None:
                key = cls._normalize_link_key(link.group("key"))
                if key is not None and key not in link_refs:
                    title = link.group("title") or ""
                    link_refs[key] = {
                        "url": link.group("url"),
                        "yanked": "yanked" in title.lower(),
                    }
                continue

            if current is None:
                continue  # Preamble or content between releases.

            h3 = _H3_RE.match(line)
            if h3 is not None:
                name = h3.group("title").strip()
                sections.setdefault(name, [])
                current_section = sections[name]
                continue

            if _HR_RE.match(line) is not None:
                continue

            bullet = _BULLET_RE.match(line)
            if bullet is not None:
                if current_section is None:
                    continue  # Bullets before the first section are ignored.
                body = bullet.group("text")
                current_section.append(
                    {
                        "text": body.rstrip(" \t") if body is not None else "",
                        "indent": len(bullet.group("ws")) // 2,
                    }
                )
                continue
            # Any other line (prose, deeper headings) is ignored.

        for release in releases:
            ref = link_refs.get(release["version"])
            if ref is not None:
                release["url"] = ref["url"]
                release["yanked"] = release["yanked"] or ref["yanked"]
        if releases:
            releases[0]["latest"] = True
        return releases

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict, error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }

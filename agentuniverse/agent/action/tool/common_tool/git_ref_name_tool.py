#!/usr/bin/env python3

"""Git reference-name validation and analysis (branches, tags, full refs).

Implements the git-check-ref-format(1) reference-name grammar exactly as
verified empirically against the real ``git check-ref-format`` binary:

- no ASCII control characters (bytes below 0x20, or 0x7f DEL), space,
  tilde ``~``, caret ``^``, colon ``:``, question mark ``?``, or open
  bracket ``[``;
- backslash ``\\`` is forbidden; asterisk ``*`` is forbidden unless the
  refspec-pattern option is set, and then at most one asterisk is allowed;
- no slash-separated component may begin with a dot ``.`` or end with the
  exact lowercase sequence ``.lock`` (the check is case-sensitive, so
  ``.LOCK`` is accepted by git just as it is here);
- no two consecutive dots ``..`` and no ``@{`` sequence anywhere;
- a component ending with a dot is allowed mid-path (``a./b`` is valid),
  but the whole name cannot end with a dot;
- no leading or trailing slash and no empty component (``//``);
- the single character ``@`` is not a valid full refname, while ``foo@bar``
  and a lone ``@`` component such as ``x/@`` are valid;
- by default at least two slash-separated levels are required; the
  ``allow_onelevel`` option relaxes this;
- branch shorthand additionally rejects a leading dash, the exact name
  ``HEAD``, and empty names, and is validated as ``refs/heads/`` + name.
  The stateful ``@{-N}`` / ``@{upstream}`` shorthand forms that git can
  resolve from repository history are outside a stateless validator and
  are rejected through the ``@{`` grammar rule;
- normalization removes leading slashes and collapses runs of slashes,
  exactly like ``git check-ref-format --normalize``; it does not strip a
  trailing slash, so ``a//b/`` still fails after normalization.

The tool uses only the standard library, performs no network or
filesystem access, and every output is deterministic.
"""

import re
import unicodedata
from typing import Any, Callable, ClassVar

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool


class GitRefNameTool(Tool):
    """Validate, normalize, analyze, repair, and compare git reference names."""

    MODES: ClassVar[tuple[str, ...]] = ("validate", "normalize", "analyze", "suggest", "compare")
    REF_TYPES: ClassVar[tuple[str, ...]] = ("any", "branch", "tag")

    HEADS_PREFIX: ClassVar[str] = "refs/heads/"
    TAGS_PREFIX: ClassVar[str] = "refs/tags/"
    REMOTES_PREFIX: ClassVar[str] = "refs/remotes/"
    LOCK_SUFFIX: ClassVar[str] = ".lock"

    #: Forbidden in any refname. "*" is handled separately (refspec patterns).
    FORBIDDEN_CHARS: ClassVar[frozenset[str]] = frozenset(" ~^:?[\\")
    CONTROL_ESCAPE: ClassVar[dict[int, str]] = {0x00: "\\0", 0x09: "\\t", 0x0A: "\\n", 0x0D: "\\r"}

    TICKET_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\b[A-Z][A-Z0-9]{1,9}-\d+\b")
    VERSION_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^v?\d+(\.\d+)+(-[\w.]+)?$")
    DATE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\d{4}-\d{2}-\d{2}|\b\d{8}\b")
    SEMVER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)(\.(0|[1-9]\d*))?(-[\w.]+)?(\+[\w.]+)?$"
    )
    RELEASE_BRANCH_PREFIXES: ClassVar[tuple[str, ...]] = ("release/", "releases/", "hotfix/")

    max_name_chars: int = Field(default=1024, gt=0, le=4096, description="Maximum accepted refname length in characters")
    max_violations: int = Field(default=8, ge=1, le=32, description="Maximum reported violations per validation")
    max_suggestions: int = Field(default=4, ge=1, le=8, description="Maximum repair suggestions")

    # ------------------------------------------------------------------ #
    # public API                                                          #
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str = "validate",
        name: str = "",
        other_name: str | None = None,
        ref_type: str = "any",
        allow_onelevel: bool = False,
        refspec_pattern: bool = False,
    ) -> dict[str, Any]:
        """Validate, normalize, analyze, repair, or compare a git refname.

        Args:
            mode: One of ``validate``, ``normalize``, ``analyze``,
                ``suggest``, ``compare``.
            name: The reference name under inspection.
            other_name: Second reference name (required for ``compare``).
            ref_type: ``branch`` validates ``name`` as a branch shorthand
                (git ``--branch`` semantics), ``tag`` as a tag name under
                ``refs/tags/``, ``any`` validates the name as given.
            allow_onelevel: Accept single-level refnames (git
                ``--allow-onelevel``); ``any`` mode only.
            refspec_pattern: Allow one ``*`` glob (git
                ``--refspec-pattern``); ``any`` mode only.

        Returns:
            A deterministic result dictionary. Mode is echoed and invalid
            names are reported through ``violations``, never exceptions.

        Raises:
            ValueError: If mode, argument types, or option combinations
                are invalid.
        """
        if mode not in self.MODES:
            raise ValueError(f"mode must be one of {list(self.MODES)}")
        if ref_type not in self.REF_TYPES:
            raise ValueError(f"ref_type must be one of {list(self.REF_TYPES)}")
        if not isinstance(allow_onelevel, bool) or not isinstance(refspec_pattern, bool):
            raise ValueError("allow_onelevel and refspec_pattern must be booleans")
        if refspec_pattern and ref_type != "any":
            raise ValueError("refspec_pattern applies to ref_type 'any' only")
        if not isinstance(name, str):
            raise ValueError("name must be a string")
        if len(name) > self.max_name_chars:
            raise ValueError(f"name must be at most {self.max_name_chars} characters")
        if mode == "compare":
            if not isinstance(other_name, str):
                raise ValueError("compare mode requires other_name as a string")
            if len(other_name) > self.max_name_chars:
                raise ValueError(f"other_name must be at most {self.max_name_chars} characters")

        if mode == "validate":
            return self._result_validate(name, ref_type, allow_onelevel, refspec_pattern)
        if mode == "normalize":
            return self._result_normalize(name, allow_onelevel, refspec_pattern)
        if mode == "analyze":
            return self._result_analyze(name)
        if mode == "suggest":
            return self._result_suggest(name, ref_type, allow_onelevel, refspec_pattern)
        return self._result_compare(name, other_name or "")

    # ------------------------------------------------------------------ #
    # validate / grammar                                                  #
    # ------------------------------------------------------------------ #

    def _result_validate(
        self,
        name: str,
        ref_type: str,
        allow_onelevel: bool,
        refspec_pattern: bool,
    ) -> dict[str, Any]:
        if ref_type == "branch":
            violations = self._branch_violations(name)
        elif ref_type == "tag":
            violations = self._grammar_violations(self.TAGS_PREFIX + name, limit=self.max_violations)
        else:
            violations = self._grammar_violations(name, allow_onelevel, refspec_pattern, limit=self.max_violations)
        return {
            "mode": "validate",
            "name": name,
            "ref_type": ref_type,
            "options": {"allow_onelevel": allow_onelevel, "refspec_pattern": refspec_pattern},
            "valid": not violations,
            "violations": violations,
        }

    def _branch_violations(self, name: str) -> list[dict[str, Any]]:
        """Mirror ``git check-ref-format --branch`` (stateless subset)."""
        limit = self.max_violations
        violations: list[dict[str, Any]] = []
        if not name:
            violations.append({"rule": "empty_name", "position": 0, "char": ""})
        if name.startswith("-"):
            violations.append({"rule": "branch_leading_dash", "position": 0, "char": "-"})
        if name == "HEAD":
            violations.append({"rule": "branch_head_reserved", "position": 0, "char": ""})
        violations.extend(self._grammar_violations(self.HEADS_PREFIX + name, limit=limit))
        return violations[:limit]

    @classmethod
    def _grammar_violations(
        cls,
        name: str,
        allow_onelevel: bool = False,
        refspec_pattern: bool = False,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        """All rule breaches of the git-check-ref-format grammar, in order."""
        violations: list[dict[str, Any]] = []

        def add(rule: str, position: int, char: str = "") -> None:
            if len(violations) < limit:
                violations.append({"rule": rule, "position": position, "char": char})

        if not name:
            add("empty_name", 0)
            return violations
        if name == "@":
            add("single_at", 0, "@")

        star_used = False
        prev = ""
        component_start = 0
        for index, char in enumerate(name):
            code = ord(char)
            if code < 0x20 or code == 0x7F:
                add("control_char", index, cls._escape_char(char))
            elif char in cls.FORBIDDEN_CHARS:
                add("forbidden_char", index, char)
            elif char == "*":
                if refspec_pattern and not star_used:
                    star_used = True
                else:
                    add("forbidden_char", index, "*")
            if char == "." and prev == ".":
                add("double_dot", index, ".")
            if char == "{" and prev == "@":
                add("at_brace", index, "{")
            if char == "/":
                cls._check_component(name, component_start, index, add)
                component_start = index + 1
            prev = char
        cls._check_component(name, component_start, len(name), add)

        if name.endswith("."):
            add("trailing_dot", len(name) - 1, ".")
        if "/" not in name and not allow_onelevel:
            add("onelevel", 0)
        return violations

    @classmethod
    def _check_component(
        cls,
        name: str,
        start: int,
        end: int,
        add: Callable[[str, int, str], None],
    ) -> None:
        if start >= end:
            add("empty_component", start)
            return
        if name[start] == ".":
            add("component_leading_dot", start, ".")
        if name[start:end].endswith(cls.LOCK_SUFFIX):
            add("lock_suffix", end - len(cls.LOCK_SUFFIX), cls.LOCK_SUFFIX)

    @classmethod
    def _escape_char(cls, char: str) -> str:
        code = ord(char)
        if code in cls.CONTROL_ESCAPE:
            return cls.CONTROL_ESCAPE[code]
        return f"\\x{code:02x}"

    # ------------------------------------------------------------------ #
    # normalize                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_string(name: str) -> str:
        """git --normalize: strip leading slashes, collapse slash runs."""
        return re.sub(r"/{2,}", "/", name.lstrip("/"))

    def _result_normalize(self, name: str, allow_onelevel: bool, refspec_pattern: bool) -> dict[str, Any]:
        normalized = self._normalize_string(name)
        violations = self._grammar_violations(normalized, allow_onelevel, refspec_pattern, limit=self.max_violations)
        return {
            "mode": "normalize",
            "name": name,
            "normalized": normalized,
            "changed": normalized != name,
            "options": {"allow_onelevel": allow_onelevel, "refspec_pattern": refspec_pattern},
            "valid": not violations,
            "violations": violations,
        }

    # ------------------------------------------------------------------ #
    # analyze                                                             #
    # ------------------------------------------------------------------ #

    def _result_analyze(self, name: str) -> dict[str, Any]:
        violations = self._grammar_violations(name, allow_onelevel=True, limit=self.max_violations)
        parts = name.split("/") if name else []
        prefixed_kind = self._prefixed_kind(name)
        findings = self._style_findings(name)
        looks_like: list[str] = []
        last = parts[-1] if parts else ""
        if self.SEMVER_PATTERN.match(last):
            looks_like.append("semver")
        elif self.VERSION_PATTERN.match(last):
            looks_like.append("version-tag")
        if self.DATE_PATTERN.search(name):
            looks_like.append("date-based")
        if name.startswith(self.RELEASE_BRANCH_PREFIXES):
            looks_like.append("release-branch")
        return {
            "mode": "analyze",
            "name": name,
            "valid_under_onelevel": not violations,
            "violations": violations,
            "parts": parts,
            "prefixed_kind": prefixed_kind,
            "suggested_type": self._suggested_type(name, prefixed_kind, looks_like),
            "looks_like": looks_like,
            "ticket_refs": self.TICKET_PATTERN.findall(name)[:8],
            "style_findings": findings,
        }

    @classmethod
    def _prefixed_kind(cls, name: str) -> str:
        if name.startswith(cls.HEADS_PREFIX):
            return "branch"
        if name.startswith(cls.TAGS_PREFIX):
            return "tag"
        if name.startswith(cls.REMOTES_PREFIX):
            return "remote-tracking"
        if name == "HEAD" or name.startswith("refs/"):
            return "ref"
        return "shorthand"

    @classmethod
    def _suggested_type(cls, name: str, prefixed_kind: str, looks_like: list[str]) -> str:
        if prefixed_kind in ("branch", "tag", "remote-tracking"):
            return prefixed_kind
        if prefixed_kind == "ref":
            return "HEAD" if name == "HEAD" else "ref"
        if name.startswith(cls.RELEASE_BRANCH_PREFIXES):
            return "branch"
        if "semver" in looks_like or "version-tag" in looks_like or "date-based" in looks_like:
            return "tag"
        if "/" in name:
            return "branch"
        return "unknown"

    @classmethod
    def _style_findings(cls, name: str) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []

        def add(finding: str, detail: str) -> None:
            findings.append({"finding": finding, "detail": detail})

        letters = [c for c in name if c.isalpha()]
        if len(letters) >= 4 and sum(1 for c in letters if c.isupper()) / len(letters) > 0.7:
            add("uppercase_heavy", "most letters are uppercase")
        if any(unicodedata.category(c) == "So" for c in name):
            add("emoji_or_symbol", "contains emoji or other symbol characters")
        if len(name.encode("utf-8")) > 200:
            add("very_long", "name exceeds 200 UTF-8 bytes; some filesystems cap ref components near 255")
        if unicodedata.normalize("NFKC", name) != name:
            samples = sorted({c for c in name if unicodedata.normalize("NFKC", c) != c})[:4]
            add("unicode_confusables", "characters NFKC rewrites, e.g. " + ", ".join(f"U+{ord(c):04X}" for c in samples))
        if any(unicodedata.category(c) == "Cf" or c in "\u200b\u200c\u200d\ufeff" for c in name):
            add("invisible_chars", "contains zero-width or format characters")
        if name != name.strip(" \t"):
            add("edge_whitespace", "leading or trailing space or tab")
        if unicodedata.normalize("NFC", name) != name:
            add("nfc_differs", "name is not in Unicode NFC form; macOS filesystems may normalize it differently")
        if name.startswith(".") or name.endswith("."):
            add("edge_dots", "leading or trailing dot")
        return findings

    # ------------------------------------------------------------------ #
    # suggest                                                             #
    # ------------------------------------------------------------------ #

    def _result_suggest(
        self,
        name: str,
        ref_type: str,
        allow_onelevel: bool,
        refspec_pattern: bool,
    ) -> dict[str, Any]:
        current = self._result_validate(name, ref_type, allow_onelevel, refspec_pattern)
        suggestions: list[dict[str, Any]] = []
        seen: set[str] = set()

        def push(candidate: str, changes: list[str]) -> None:
            if not candidate or candidate == name or candidate in seen:
                return
            if len(suggestions) >= self.max_suggestions:
                return
            seen.add(candidate)
            check = self._result_validate(candidate, ref_type, allow_onelevel, refspec_pattern)
            suggestions.append(
                {
                    "name": candidate,
                    "changes": self._dedupe_strings(changes),
                    "valid_now": check["valid"],
                }
            )

        sanitized, changes = self._sanitize(name, ref_type)
        push(sanitized, changes)
        minimal, minimal_changes = self._minimal_fix(name, ref_type, allow_onelevel, refspec_pattern)
        push(minimal, minimal_changes)
        if ref_type == "any" and not allow_onelevel and name and "/" not in name:
            push("heads/" + name, ["prepended the 'heads/' category to satisfy the two-level rule"])
        if ref_type == "branch" and name == "HEAD":
            push("head", ["lowercased 'HEAD' which is reserved for the symbolic ref"])

        best = None
        for suggestion in suggestions:
            if suggestion["valid_now"]:
                best = suggestion["name"]
                break
        return {
            "mode": "suggest",
            "name": name,
            "ref_type": ref_type,
            "options": {"allow_onelevel": allow_onelevel, "refspec_pattern": refspec_pattern},
            "input_valid": current["valid"],
            "violations": current["violations"],
            "suggestions": suggestions,
            "best": best,
        }

    @staticmethod
    def _dedupe_strings(values: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                out.append(value)
        return out

    @classmethod
    def _sanitize(cls, name: str, ref_type: str) -> tuple[str, list[str]]:
        """Mechanical repair of every violation at once, deterministic."""
        changes: list[str] = []
        working = name

        if ref_type == "branch" and working.startswith("-"):
            working = working.lstrip("-")
            changes.append("stripped leading dash(es) not allowed in branch names")
        if working.startswith("/"):
            working = working.lstrip("/")
            changes.append("removed leading slash(es)")
        if "@{" in working:
            working = working.replace("@{", "@")
            changes.append("broke the '@{' sequence")
        if working == "@":
            working = "at"
            changes.append("expanded the bare '@' shorthand")

        cleaned: list[str] = []
        replaced: set[str] = set()
        for char in working:
            code = ord(char)
            if code < 0x20 or code == 0x7F:
                replaced.add(cls._escape_char(char))
                cleaned.append("-")
            elif char in cls.FORBIDDEN_CHARS or char == "*":
                replaced.add(char)
                cleaned.append("-")
            else:
                cleaned.append(char)
        if replaced:
            changes.append("replaced forbidden characters with '-': " + ", ".join(sorted(replaced)))
        working = "".join(cleaned)

        collapsed = re.sub(r"/{2,}", "/", working)
        if collapsed != working:
            changes.append("collapsed repeated slashes")
            working = collapsed

        components: list[str] = []
        stripped_dots = stripped_locks = collapsed_dots = False
        for component in working.split("/"):
            if component.startswith("."):
                component = component.lstrip(".")
                stripped_dots = True
            while ".." in component:
                component = component.replace("..", ".")
                collapsed_dots = True
            while component.endswith(cls.LOCK_SUFFIX):
                component = component[: -len(cls.LOCK_SUFFIX)]
                stripped_locks = True
            if component.endswith("."):
                component = component.rstrip(".")
                stripped_dots = True
            components.append(component)
        if stripped_dots:
            changes.append("stripped edge dots from components")
        if collapsed_dots:
            changes.append("collapsed consecutive dots")
        if stripped_locks:
            changes.append("stripped '.lock' suffixes from components")
        working = "/".join(c for c in components if c)

        if working.endswith("."):
            working = working.rstrip(".")
            changes.append("removed trailing dot(s)")
        if working.startswith(("-", "/")):
            working = working.lstrip("-/")
            changes.append("stripped leading dash or slash produced by repairs")
        return working, changes

    def _minimal_fix(
        self,
        name: str,
        ref_type: str,
        allow_onelevel: bool,
        refspec_pattern: bool,
    ) -> tuple[str, list[str]]:
        """Fix only the first reported violation, as small as possible."""
        violations = self._result_validate(name, ref_type, allow_onelevel, refspec_pattern)["violations"]
        if not violations:
            return name, []
        first = violations[0]
        rule = first["rule"]
        position = first["position"]
        working = name
        changes: list[str] = []

        if rule == "empty_name":
            return "", ["input name is empty"]
        if rule == "branch_leading_dash":
            working = working.lstrip("-")
            changes.append("stripped leading dash(es)")
        elif rule == "branch_head_reserved":
            working = "head"
            changes.append("lowercased reserved 'HEAD'")
        elif rule == "single_at":
            working = "at"
            changes.append("expanded the bare '@' shorthand")
        elif rule == "onelevel":
            working = "heads/" + working
            changes.append("prepended the 'heads/' category")
        elif rule == "trailing_dot":
            working = working.rstrip(".")
            changes.append("removed trailing dot(s)")
        elif rule == "empty_component" and working.startswith("/"):
            working = working.lstrip("/")
            changes.append("removed leading slash(es)")
        elif rule == "empty_component" and working.endswith("/"):
            working = working.rstrip("/")
            changes.append("removed trailing slash(es)")
        elif rule == "empty_component":
            collapsed = re.sub(r"/{2,}", "/", working)
            working = collapsed
            changes.append("collapsed repeated slashes")
        elif rule in ("forbidden_char", "control_char"):
            working = working[:position] + "-" + working[position + 1:]
            changes.append(f"replaced character at position {position} with '-'")
        elif rule == "double_dot":
            working = working[: position - 1] + working[position:]
            changes.append(f"removed one dot of '..' at position {position}")
        elif rule == "at_brace":
            working = working[:position] + working[position + 1:]
            changes.append(f"removed '{{' of '@{{' at position {position}")
        elif rule == "component_leading_dot":
            working = working[:position] + working[position + 1:]
            changes.append(f"removed leading dot of component at position {position}")
        elif rule == "lock_suffix":
            working = working[:position] + working[position + len(self.LOCK_SUFFIX):]
            changes.append("removed '.lock' suffix")
        if working.startswith(("-", "/")) and working != name:
            working = working.lstrip("-/")
            changes.append("stripped leading dash or slash produced by repairs")
        return working, changes

    # ------------------------------------------------------------------ #
    # compare                                                             #
    # ------------------------------------------------------------------ #

    def _result_compare(self, name: str, other_name: str) -> dict[str, Any]:
        name_branch = self._strip_prefix(name, self.HEADS_PREFIX)
        other_branch = self._strip_prefix(other_name, self.HEADS_PREFIX)
        name_tag = self._strip_prefix(name, self.TAGS_PREFIX)
        other_tag = self._strip_prefix(other_name, self.TAGS_PREFIX)

        same_branch = bool(name_branch) and name_branch == other_branch
        same_tag = bool(name_tag) and name_tag == other_tag
        differ_case = name != other_name and name.lower() == other_name.lower()
        differ_normalization = (
            name != other_name
            and unicodedata.normalize("NFC", name) == unicodedata.normalize("NFC", other_name)
        )
        differ_confusables = (
            name != other_name
            and unicodedata.normalize("NFKC", name) == unicodedata.normalize("NFKC", other_name)
            and not differ_normalization
        )

        notes: list[str] = []
        if same_branch or same_tag:
            notes.append("names resolve to the same git reference")
        if differ_case:
            notes.append("names differ only by letter case; they collide on case-insensitive filesystems (core.ignoreCase=true)")
        if differ_normalization:
            notes.append("names differ only by Unicode normalization form (e.g. NFC vs NFD); macOS filesystems normalize and collide")
        if differ_confusables:
            notes.append("names are Unicode confusables: identical after NFKC (e.g. fullwidth vs ASCII lookalikes)")

        return {
            "mode": "compare",
            "name": name,
            "other_name": other_name,
            "same_ref_if_branch": same_branch,
            "same_ref_if_tag": same_tag,
            "equivalent": same_branch or same_tag,
            "differ_only_by_case": differ_case,
            "differ_only_by_unicode_normalization": differ_normalization,
            "unicode_confusables": differ_confusables,
            "casefolded_forms": [name.lower(), other_name.lower()],
            "nfc_forms": [unicodedata.normalize("NFC", name), unicodedata.normalize("NFC", other_name)],
            "valid_under_onelevel": {
                "name": not self._grammar_violations(name, allow_onelevel=True),
                "other_name": not self._grammar_violations(other_name, allow_onelevel=True),
            },
            "notes": notes,
        }

    @classmethod
    def _strip_prefix(cls, name: str, prefix: str) -> str:
        return name[len(prefix):] if name.startswith(prefix) else name

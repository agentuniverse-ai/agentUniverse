#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: acronym_expander_tool.py

"""Acronym detection, glossary lookup and inline expansion tool.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency helper agents can
call when preparing or polishing text: find the acronyms used in a
document, explain what they mean, or expand the first mention of each
one inline for readers.

The tool is built purely on the standard library (only ``re`` for the
scanner) and supports three modes:

* ``detect`` — scan ``text`` and report every acronym with its
  occurrence count and the span of its first occurrence.
* ``expand`` — resolve a list of ``acronyms`` (plus an optional
  user ``glossary``) to their expansions; entries found in neither
  glossary are marked ``unknown``.
* ``replace`` — rewrite ``text`` so that the first occurrence of each
  known acronym is expanded inline using the pattern
  ``API (Application Programming Interface)``; later occurrences are
  left alone and the rewrite is idempotent.

Detection rules (documented behaviour)
--------------------------------------

An acronym is a *maximal* run of 1-6 ASCII uppercase letters followed
by an optional digit suffix, with a total length of 2 to 6
characters.  ``A9``, ``GPT4``, ``MP3``, ``LLM`` and ``RAG`` all
match; a single letter (``A``), a 7-letter shout (``ABCDEFGH``) and
an oversized digit suffix (``A1234567``) do not.

Boundary rules — a run is disqualified when the character immediately
before or after it is a letter (either case) or an underscore:

* ``USAir`` yields nothing: the ``USA`` run is followed by a
  lowercase letter, and the ``air`` tail also poisons the shorter
  backtracked candidates.
* ``theAPI`` and ``macOSAPI`` yield nothing: camelCase tails never
  produce partial matches because a preceding letter (of any case)
  disqualifies the run.  For symmetry a run that was truncated by
  the 6-letter cap (e.g. ``ABCDEF`` inside ``ABCDEFG``) is rejected
  as well.
* ``API_KEY`` yields nothing: underscore-joined identifiers are
  treated as code, not prose, so both ``API`` and ``KEY`` are
  suppressed (the underscore counts as a blocking boundary).
* Mixed-case short forms such as ``K8s``, ``OAuth``, ``SaaS``,
  ``BaaS``, ``PaaS`` and ``NoSQL`` are never auto-detected — the
  lowercase letters inside them break the uppercase run.  They *are*
  available to ``expand`` and ``replace`` lookups through the
  built-in glossary (canonical spellings are matched
  case-insensitively).

Caps-lock guard — a paragraph in which more than 60% of the letters
are uppercase is treated as shouting and skipped entirely by both
``detect`` and ``replace`` (the caps ratio is computed per line, a
paragraph being one line of the input; a line with no letters is
never guarded).  The number of skipped lines is reported in the
result payload.  Exactly 60% is *not* guarded (the comparison is
strict).

Glossary semantics (documented behaviour)
-----------------------------------------

Lookups consult the user ``glossary`` first (user definitions always
win over the built-in ones) and then a built-in tech glossary of ~60
common terms.  Lookup is case-insensitive on the upper-cased form,
so ``k8s`` and ``K8S`` both resolve to the canonical ``K8s`` entry.
Deliberate, documented decisions baked into the glossary:

* No plural stripping — ``RAGs`` does **not** resolve to ``RAG``;
  it is reported as ``unknown`` unless the user adds it to their own
  glossary.  Plural stripping is a guessing game (``OSs``, ``CDs``,
  ``Is``) and the tool refuses to guess.
* ``CD`` is flagged ``ambiguous``: it expands to *Continuous
  Delivery* by default but the payload also carries the
  alternatives *Continuous Deployment* and *Compact Disc* so an
  agent can disambiguate from context.
* ``GraphQL`` and ``IoT`` are deliberately **not** in the built-in
  glossary — the former is a product name rather than an acronym,
  and the latter only exists in a mixed-case spelling the detector
  cannot produce; both resolve to ``unknown`` unless the user
  supplies them.

Replace semantics (documented behaviour)
----------------------------------------

Only the *first* occurrence of each acronym is expanded; subsequent
occurrences are left alone.  The expansion is idempotent: an acronym
that is immediately followed by a whitespace-prefixed parenthetical
(an earlier pass output like ``API (Application Programming
Interface)``, or a human annotation like ``API (v2)``) is treated as
already expanded, and acronyms found *inside* such a parenthetical
are treated as already expanded too — so running ``replace`` over
its own output returns the exact same text (the second pass reports
zero replacements).  A side effect of this conservative rule: an
acronym whose first occurrence already carries any parenthetical is
never expanded elsewhere in the text.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing/empty ``text``, missing
or empty ``acronyms``, non-string acronym entries, a ``glossary``
that is not a ``dict`` of non-empty ``str`` → ``str``, conflicting
case-insensitive glossary duplicates, oversized inputs) raise a
``ValueError``, mirroring the other common tools.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A maximal run of 1-6 uppercase letters plus an optional digit
# suffix.  The lookbehind/lookahead block any adjacent letter or
# underscore, which implements the boundary rules described in the
# module docstring (maximal run, "USAir"/"theAPI"/"API_KEY" guards)
# and also rejects runs truncated by the 6-letter cap ("ABCDEFG").
_ACRONYM_RE = re.compile(r"(?<![A-Za-z_])[A-Z]{1,6}[0-9]*(?![A-Za-z0-9_])")

# Minimum / maximum length of an acronym token (letters + digits).
_MIN_TOKEN_LEN = 2
_MAX_TOKEN_LEN = 6

# A paragraph whose uppercase-letter ratio strictly exceeds this
# threshold is treated as caps-lock shouting and skipped.
_CAPS_LOCK_RATIO = 0.6

# Hard input limits (mirrored as pydantic attributes on the class).
_MAX_TEXT_CHARS = 100_000
_MAX_ACRONYMS = 1_000
_MAX_GLOSSARY_ENTRIES = 1_000

# Built-in tech glossary, keyed by the canonical spelling.  Lookup is
# done on the upper-cased key (see _BUILTIN_LOOKUP).  Entries may set
# "ambiguous" (bool) and "alternatives" (list[str]) — only "CD" does.
_BUILTIN_GLOSSARY: dict[str, dict[str, Any]] = {
    "AI": {"expansion": "Artificial Intelligence"},
    "API": {"expansion": "Application Programming Interface"},
    "ASCII": {"expansion": "American Standard Code for Information Interchange"},
    "BaaS": {"expansion": "Backend as a Service"},
    "BI": {"expansion": "Business Intelligence"},
    "CD": {
        "expansion": "Continuous Delivery",
        "ambiguous": True,
        "alternatives": ["Continuous Deployment", "Compact Disc"],
    },
    "CDN": {"expansion": "Content Delivery Network"},
    "CI": {"expansion": "Continuous Integration"},
    "CLI": {"expansion": "Command Line Interface"},
    "CMS": {"expansion": "Content Management System"},
    "CPU": {"expansion": "Central Processing Unit"},
    "CRUD": {"expansion": "Create, Read, Update, Delete"},
    "CSS": {"expansion": "Cascading Style Sheets"},
    "CSV": {"expansion": "Comma-Separated Values"},
    "DNS": {"expansion": "Domain Name System"},
    "DOM": {"expansion": "Document Object Model"},
    "ETL": {"expansion": "Extract, Transform, Load"},
    "FTP": {"expansion": "File Transfer Protocol"},
    "GPT": {"expansion": "Generative Pre-trained Transformer"},
    "GPU": {"expansion": "Graphics Processing Unit"},
    "GUI": {"expansion": "Graphical User Interface"},
    "HTML": {"expansion": "HyperText Markup Language"},
    "HTTP": {"expansion": "Hypertext Transfer Protocol"},
    "HTTPS": {"expansion": "Hypertext Transfer Protocol Secure"},
    "IDE": {"expansion": "Integrated Development Environment"},
    "IP": {"expansion": "Internet Protocol"},
    "JWT": {"expansion": "JSON Web Token"},
    "JSON": {"expansion": "JavaScript Object Notation"},
    "K8s": {"expansion": "Kubernetes"},
    "LLM": {"expansion": "Large Language Model"},
    "ML": {"expansion": "Machine Learning"},
    "MVP": {"expansion": "Minimum Viable Product"},
    "NLP": {"expansion": "Natural Language Processing"},
    "NoSQL": {"expansion": "Not Only SQL"},
    "OCR": {"expansion": "Optical Character Recognition"},
    "OS": {"expansion": "Operating System"},
    "OAuth": {"expansion": "Open Authorization"},
    "PaaS": {"expansion": "Platform as a Service"},
    "QA": {"expansion": "Quality Assurance"},
    "RAM": {"expansion": "Random Access Memory"},
    "REST": {"expansion": "Representational State Transfer"},
    "RPC": {"expansion": "Remote Procedure Call"},
    "RAG": {"expansion": "Retrieval-Augmented Generation"},
    "SDK": {"expansion": "Software Development Kit"},
    "SLA": {"expansion": "Service Level Agreement"},
    "SMTP": {"expansion": "Simple Mail Transfer Protocol"},
    "SQL": {"expansion": "Structured Query Language"},
    "SSD": {"expansion": "Solid State Drive"},
    "SSO": {"expansion": "Single Sign-On"},
    "SSL": {"expansion": "Secure Sockets Layer"},
    "SaaS": {"expansion": "Software as a Service"},
    "TCP": {"expansion": "Transmission Control Protocol"},
    "TDD": {"expansion": "Test-Driven Development"},
    "TLS": {"expansion": "Transport Layer Security"},
    "UI": {"expansion": "User Interface"},
    "URI": {"expansion": "Uniform Resource Identifier"},
    "URL": {"expansion": "Uniform Resource Locator"},
    "UX": {"expansion": "User Experience"},
    "UUID": {"expansion": "Universally Unique Identifier"},
    "VPN": {"expansion": "Virtual Private Network"},
    "XML": {"expansion": "eXtensible Markup Language"},
    "YAML": {"expansion": "YAML Ain't Markup Language"},
}

# Case-insensitive lookup view of the built-in glossary.  The 62
# canonical keys upper-case to 62 distinct keys (verified by the unit
# tests), so the mapping is lossless.
_BUILTIN_LOOKUP: dict[str, tuple[str, dict[str, Any]]] = {
    key.upper(): (key, entry) for key, entry in _BUILTIN_GLOSSARY.items()
}


class AcronymExpanderTool(Tool):
    """Acronym detection, glossary lookup and inline expansion tool.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input
            length; longer inputs are rejected before any work.
        max_acronyms (int): Upper bound on the number of ``acronyms``
            entries accepted by the ``expand`` mode.
        max_glossary_entries (int): Upper bound on the number of
            user-glossary entries.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "acronym_expander_tool"
    description: str = (
        "Acronym expander tool — pure Python stdlib, no network "
        "required. Detect acronyms in text with counts and first "
        "occurrence spans (mode='detect'), resolve acronym lists to "
        "expansions via a user glossary plus a built-in tech "
        "glossary with unknown marking (mode='expand'), and expand "
        "the first occurrence of each known acronym inline as "
        "'API (Application Programming Interface)' with an "
        "idempotent second-pass guard (mode='replace')."
    )

    MODES: ClassVar[tuple] = ("detect", "expand", "replace")

    max_text_chars: int = 100_000
    max_acronyms: int = 1_000
    max_glossary_entries: int = 1_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        acronyms: Any = None,
        glossary: Any = None,
    ) -> dict[str, Any]:
        """Run one acronym operation.

        Args:
            mode (str): One of ``detect`` / ``expand`` / ``replace``.
            text (str): The text to scan; required for the ``detect``
                and ``replace`` modes; not used by ``expand``.
            acronyms (list[str] | str): The acronyms to resolve;
                required for the ``expand`` mode; not used by
                ``detect`` or ``replace``.  A list of non-empty
                strings, or a single string that is split on commas
                and whitespace.
            glossary (dict[str, str] | None): Optional user glossary
                of acronym → expansion; user definitions win over
                the built-in glossary.  Used by ``expand`` and
                ``replace``.

        Returns:
            Dict[str, Any]: The operation result (a ``result`` key
                plus the call context) — see the mode docstrings for
                the exact payload shapes.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "detect":
            return self._run_detect(self._validate_text(text))
        if mode == "expand":
            return self._run_expand(self._validate_acronyms(acronyms), glossary)
        return self._run_replace(self._validate_text(text), glossary)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"acronym_expander_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (detect and replace modes)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > _MAX_TEXT_CHARS:
            cls._invalid(
                f"text exceeds the {_MAX_TEXT_CHARS:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_acronyms(cls, acronyms: Any) -> list[str]:
        """Validate the ``acronyms`` input (expand mode).

        Accepts a list/tuple of non-empty strings or a single string
        (split on commas and whitespace).  Returns the cleaned list.
        """
        if acronyms is None:
            cls._invalid(
                "acronyms are required for mode='expand' — pass a list of "
                "acronym strings or a single comma/space separated string "
                f"(got {acronyms!r})"
            )
        if isinstance(acronyms, str):
            if not acronyms.strip():
                cls._invalid(
                    "acronyms must contain at least one acronym (got "
                    f"{acronyms!r})"
                )
            items: list[Any] = re.split(r"[\s,]+", acronyms.strip())
        elif isinstance(acronyms, (list, tuple)):
            items = list(acronyms)
        else:
            cls._invalid(
                "acronyms must be a list of strings or a single string "
                f"(got {acronyms!r})"
            )
        cleaned: list[str] = []
        for item in items:
            if (
                item is None
                or isinstance(item, bool)
                or not isinstance(item, str)
                or not item.strip()
            ):
                cls._invalid(
                    f"acronyms must be non-empty strings (got {item!r})"
                )
            entry = item.strip()
            if len(entry) > 64:
                cls._invalid(
                    f"acronym exceeds the 64-character limit (got {entry[:64]!r}...)"
                )
            cleaned.append(entry)
        if not cleaned:
            cls._invalid("acronyms must contain at least one acronym (got [])")
        if len(cleaned) > _MAX_ACRONYMS:
            cls._invalid(
                f"acronyms exceed the {_MAX_ACRONYMS:,}-entry limit "
                f"(got {len(cleaned):,} entries)"
            )
        return cleaned

    @classmethod
    def _validate_glossary(cls, glossary: Any) -> dict[str, str]:
        """Validate the user ``glossary`` and normalize it.

        Returns an upper-cased ``{ACRONYM: expansion}`` dict (the
        canonical, case-insensitive lookup form).  Keys that differ
        only in case must map to the same expansion, otherwise the
        glossary is ambiguous and rejected.
        """
        if glossary is None:
            return {}
        if isinstance(glossary, bool) or not isinstance(glossary, dict):
            cls._invalid(
                "glossary must be a dict of acronym -> expansion strings "
                f"or None (got {glossary!r})"
            )
        normalized: dict[str, str] = {}
        for key, value in glossary.items():
            if (
                key is None
                or isinstance(key, bool)
                or not isinstance(key, str)
                or not key.strip()
            ):
                cls._invalid(
                    f"glossary keys must be non-empty strings (got {key!r})"
                )
            if (
                value is None
                or isinstance(value, bool)
                or not isinstance(value, str)
                or not value.strip()
            ):
                cls._invalid(
                    "glossary values must be non-empty expansion strings "
                    f"(got {value!r})"
                )
            clean_key = key.strip()
            clean_value = value.strip()
            if len(clean_key) > 64:
                cls._invalid(
                    f"glossary key exceeds the 64-character limit (got {clean_key[:64]!r}...)"
                )
            if len(clean_value) > 500:
                cls._invalid(
                    f"glossary value for {clean_key!r} exceeds the "
                    "500-character limit"
                )
            folded = clean_key.upper()
            if folded in normalized and normalized[folded] != clean_value:
                cls._invalid(
                    f"glossary contains conflicting entries for {folded!r} "
                    f"({normalized[folded]!r} vs {clean_value!r})"
                )
            normalized[folded] = clean_value
        if len(normalized) > _MAX_GLOSSARY_ENTRIES:
            cls._invalid(
                f"glossary exceeds the {_MAX_GLOSSARY_ENTRIES:,}-entry "
                f"limit (got {len(normalized):,} entries)"
            )
        return normalized

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _is_caps_lock(paragraph: str) -> bool:
        """Return True when a paragraph is shouting (>60% caps).

        The ratio is computed over Unicode letters only; a paragraph
        with no letters is never guarded.  The comparison is strict,
        so exactly 60% uppercase is NOT treated as caps lock.
        """
        letters = [char for char in paragraph if char.isalpha()]
        if not letters:
            return False
        caps = sum(1 for char in letters if char.isupper())
        return caps / len(letters) > _CAPS_LOCK_RATIO

    @staticmethod
    def _matches(paragraph: str) -> list[re.Match]:
        """Return the valid acronym matches of one paragraph, in order."""
        return [
            match
            for match in _ACRONYM_RE.finditer(paragraph)
            if _MIN_TOKEN_LEN <= len(match.group(0)) <= _MAX_TOKEN_LEN
        ]

    def _merged_glossary(self, user_glossary: dict[str, str]) -> dict[str, str]:
        """Merge the user glossary over the built-in one (user wins)."""
        merged = {
            key: entry["expansion"]
            for key, (_, entry) in _BUILTIN_LOOKUP.items()
        }
        merged.update(user_glossary)
        return merged

    # ------------------------------------------------------------------ #
    # detect mode
    # ------------------------------------------------------------------ #

    def _run_detect(self, text: str) -> dict[str, Any]:
        """Scan the text and report acronyms with counts and spans."""
        acronyms: list[dict[str, Any]] = []
        positions: dict[str, int] = {}
        skipped = 0
        offset = 0
        for paragraph in text.split("\n"):
            if self._is_caps_lock(paragraph):
                skipped += 1
            else:
                for match in self._matches(paragraph):
                    token = match.group(0)
                    if token not in positions:
                        positions[token] = len(acronyms)
                        acronyms.append(
                            {
                                "acronym": token,
                                "count": 0,
                                "first_span": {
                                    "start": offset + match.start(),
                                    "end": offset + match.end(),
                                },
                            }
                        )
                    acronyms[positions[token]]["count"] += 1
            offset += len(paragraph) + 1
        return {
            "mode": "detect",
            "result": [entry["acronym"] for entry in acronyms],
            "acronyms": acronyms,
            "acronym_count": len(acronyms),
            "caps_lock_paragraphs_skipped": skipped,
        }

    # ------------------------------------------------------------------ #
    # expand mode
    # ------------------------------------------------------------------ #

    def _run_expand(
        self, acronyms: list[str], glossary: Any
    ) -> dict[str, Any]:
        """Resolve each acronym against user + built-in glossaries."""
        user_glossary = self._validate_glossary(glossary)
        expansions: list[dict[str, Any]] = []
        unknown = 0
        for acronym in acronyms:
            folded = acronym.upper()
            if folded in user_glossary:
                expansions.append(
                    {
                        "acronym": acronym,
                        "expansion": user_glossary[folded],
                        "source": "user_glossary",
                    }
                )
                continue
            builtin = _BUILTIN_LOOKUP.get(folded)
            if builtin is None:
                expansions.append(
                    {"acronym": acronym, "expansion": None, "source": "unknown"}
                )
                unknown += 1
                continue
            canonical, entry = builtin
            payload: dict[str, Any] = {
                "acronym": acronym,
                "canonical": canonical,
                "expansion": entry["expansion"],
                "source": "builtin",
            }
            if entry.get("ambiguous"):
                payload["ambiguous"] = True
                payload["alternatives"] = list(entry.get("alternatives", []))
            expansions.append(payload)
        return {
            "mode": "expand",
            "result": expansions,
            "expansion_count": len(expansions),
            "unknown_count": unknown,
            "user_glossary_size": len(user_glossary),
        }

    # ------------------------------------------------------------------ #
    # replace mode
    # ------------------------------------------------------------------ #

    def _run_replace(self, text: str, glossary: Any) -> dict[str, Any]:
        """Expand the first occurrence of each known acronym inline.

        Replacements are applied per paragraph, left to right, and an
        acronym immediately followed by a parenthetical is treated as
        already expanded (idempotence guard) — see the module
        docstring for the full rules.
        """
        merged = self._merged_glossary(self._validate_glossary(glossary))
        paragraphs = text.split("\n")
        rebuilt: list[str] = []
        replacements: list[dict[str, Any]] = []
        done: set[str] = set()
        skipped = 0
        for paragraph_index, paragraph in enumerate(paragraphs):
            if self._is_caps_lock(paragraph):
                skipped += 1
                rebuilt.append(paragraph)
                continue
            segments: list[str] = []
            cursor = 0
            blocked_until = -1
            for match in self._matches(paragraph):
                token = match.group(0)
                if match.start() < blocked_until:
                    # Inside the parenthetical of an already expanded
                    # (or human-annotated) acronym — treated as done.
                    done.add(token)
                    continue
                if token in done:
                    continue
                expansion = merged.get(token)
                if expansion is None:
                    continue
                if paragraph.startswith(" (", match.end()):
                    # Idempotence guard: the acronym is already
                    # followed by a parenthetical annotation, so it
                    # counts as expanded and nothing inside the
                    # annotation is touched either.
                    close = paragraph.find(")", match.end() + 2)
                    if close != -1:
                        blocked_until = close + 1
                    done.add(token)
                    continue
                segments.append(paragraph[cursor : match.start()])
                segments.append(f"{token} ({expansion})")
                cursor = match.end()
                done.add(token)
                replacements.append(
                    {
                        "acronym": token,
                        "expansion": expansion,
                        "paragraph": paragraph_index,
                        "start": match.start(),
                    }
                )
            segments.append(paragraph[cursor:])
            rebuilt.append("".join(segments))
        return {
            "mode": "replace",
            "result": "\n".join(rebuilt),
            "replacements": replacements,
            "replacement_count": len(replacements),
            "caps_lock_paragraphs_skipped": skipped,
        }

#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: mermaid_flow_tool.py

"""Mermaid diagram source generation tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency diagram source
generator aimed at visualization agents. The tool never renders and
never shells out to the mermaid CLI — it only *generates* Mermaid
diagram source text from small structured specifications, plus a basic
syntax sanity lint, so agents can hand the output to any
Mermaid-compatible renderer (GitHub, Notion, mermaid.live, ...).

Supported modes:

* ``flowchart`` — build ``flowchart TD`` (or ``LR``) source from a list
  of ``nodes`` (``{id, label?, shape?}``) and ``edges``
  (``{from, to, label?, arrow?}``). Shapes: ``rect`` (default),
  ``round``, ``stadium``, ``diamond``, ``hexagon``, ``circle``,
  ``parallelogram``. Arrows: ``arrow`` ``-->`` (default), ``dotted``
  ``-.->``, ``thick`` ``==>``.
* ``sequence`` — build ``sequenceDiagram`` source from ``participants``
  (``{name, as?}``), ``messages`` (``{from, to, text, kind?}`` with
  ``solid`` ``->`` default / ``dashed`` ``-->``) and optional ``notes``
  (``{over: name | [a, b], text}``).
* ``lint`` — run a *basic sanity check* over a Mermaid source string:
  diagram declaration keyword present, unbalanced double quotes, the
  reserved ``end`` keyword used as a flowchart node id (a classic
  Mermaid pitfall), other Mermaid statement keywords used as node ids
  or actor names, and arrows without a source or target endpoint.
  This is deliberately NOT a full Mermaid parser — it is a cheap
  line-oriented heuristic pass that catches the most common breakages;
  a clean lint result does not guarantee the source renders.

Determinism and escaping conventions (documented contract):

* Node / participant identifiers are sanitized to ``[A-Za-z0-9_]``:
  every invalid character is mapped to ``_`` (one per character).
  Ids that collide with a Mermaid statement keyword are deterministically
  renamed with a trailing underscore: ``end`` -> ``end_`` everywhere, plus
  the flowchart keywords ``style``/``class``/``classDef``/``linkStyle``/
  ``subgraph``/``graph``/``flowchart`` in flowchart mode (exact-case
  match — capitalized variants such as ``Style`` are legal ids), and the
  sequence keywords (``note``, ``over``, ``actor``, ``participant``,
  ``autonumber``, ``loop``, ``alt``, ``opt``, ``par``, ``else``,
  ``option``, ``critical``, ``break``, ``box``, ``rect``, ``activate``,
  ``deactivate``, ``and``, ``end``) in sequence mode (case-insensitive
  match — ``Note`` breaks a sequence diagram just like ``note``). If two
  distinct original ids still collide after sanitization, later ones
  (in input order) get ``_2``, ``_3``, ... suffixes. The full
  ``id_mapping`` (original -> sanitized, changed entries only) is
  reported in the result
  whenever at least one id changed. Renamed sequence participants
  automatically keep their original spelling as the display alias.
* A pipe ``|`` in any label is replaced by the look-alike character
  ``❘`` (U+2758 LIGHT VERTICAL BAR) per Mermaid convention, because a
  literal pipe would terminate ``|label|`` edge label syntax.
* Node labels containing Mermaid-significant characters
  (``()[]{}<>"'#;&`\\``) are wrapped in double quotes, and a literal
  ``"`` inside a quoted label is replaced by the Mermaid entity
  ``#quot;``. Labels without those characters (including Unicode text)
  are emitted bare.
* Edge labels escape every character that terminates the ``|label|``
  syntax or the line: ``"`` -> ``#quot;``, ``[``/``]`` -> ``#91;``/
  ``#93;``, ``{``/``}`` -> ``#123;``/``#125;``, ``(``/``)`` ->
  ``#40;``/``#41;``, pipes as above (Mermaid rejects the raw forms).
* Sequence message text, note text and display aliases escape ``;`` as
  ``#59;`` — a literal semicolon is a statement separator in sequence
  diagrams and truncates the message; aliases also escape ``"`` as
  ``#quot;``. Other characters (including ``:`` and ``#``) are emitted
  as-is.
* Output order is exactly the input order: nodes, then edges;
  participants, then messages, then notes. Lines are joined with a
  single ``\n`` (no trailing newline).

Input validation is strict and happens before any generation:
malformed parameters (wrong types, empty node/participant lists,
unknown mode / shape / arrow / kind / direction, duplicate ids, labels
containing control characters, oversized inputs) raise a
``ValueError``, mirroring the other common tools. Edge and message
endpoints must reference *declared* node / participant ids; unknown
endpoints produce one error listing every one of them.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Characters that may appear in a sanitized Mermaid identifier.
_INVALID_ID_CHARS = re.compile(r"[^A-Za-z0-9_]")
# Mermaid-significant characters that force a node label to be quoted.
_NEEDS_QUOTES = re.compile(r"""[(){}<>"'\[\]#;&`\\]""")
# Control characters are rejected in every label / id / text field.
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
# The reserved flowchart keyword, as a standalone word.
_STANDALONE_END = re.compile(r"\bend\b")
# Balanced "..." spans are masked before scanning for the `end` keyword.
_QUOTED_SPANS = re.compile(r'"[^"]*"')
# Balanced |...| edge-label spans, masked for the same reason.
_PIPE_SPANS = re.compile(r"\|[^|]*\|")
# Diagram declaration on the first meaningful line (case-insensitive).
_DIAGRAM_DECL = re.compile(r"(?i)^(flowchart|graph|sequencediagram)\b")
_SUBGRAPH_OPEN = re.compile(r"(?i)^subgraph\b")
# Arrow tokens recognized by the dangling-endpoint lint check.
_ARROW_TOKENS = ("-.->", "-->", "==>", "->")
# Arrow tokens used to split a line into id slots for the reserved-id
# lint check (covers the common flowchart / sequence link forms).
_ID_SPLIT_ARROWS = re.compile(r"-->|-\.-|==>|---|--|->")
# Innermost bracket groups, removed repeatedly to mask node labels.
_BRACKET_GROUPS = (
    re.compile(r"\(([^()]*)\)"),
    re.compile(r"\[([^][]*)\]"),
    re.compile(r"\{([^{}]*)\}"),
)

# Mermaid statement keywords that break a flowchart when used as node
# ids (verified against the mermaid v11 parser: `style-->b` and even
# `a-->style` fail to parse; capitalized variants such as `Style` are
# legal, so the match is exact-case).
_RESERVED_FLOWCHART_IDS = frozenset((
    "end", "style", "class", "classDef", "linkStyle", "subgraph",
    "graph", "flowchart",
))
# Mermaid statement keywords that break a sequence diagram when used as
# actor names (verified against the mermaid v11 parser; the sequence
# grammar matches these keywords case-insensitively, so `Note->A: hi`
# fails just like `note->A: hi`).
_RESERVED_SEQUENCE_IDS = frozenset((
    "end", "note", "over", "actor", "participant", "autonumber", "loop",
    "alt", "opt", "par", "else", "option", "critical", "break", "box",
    "rect", "activate", "deactivate", "and",
))
# Edge-label characters escaped as Mermaid entities: a raw double quote
# or any bracket terminates the |label| construct (verified against the
# mermaid v11 parser).
_EDGE_LABEL_ENTITIES = (
    ("[", "#91;"),
    ("]", "#93;"),
    ("{", "#123;"),
    ("}", "#125;"),
    ("(", "#40;"),
    (")", "#41;"),
    ('"', "#quot;"),
)


class MermaidFlowTool(Tool):
    """Mermaid diagram source generator built purely on the stdlib.

    The tool generates Mermaid ``flowchart`` / ``sequenceDiagram``
    source from structured specifications and lints Mermaid source
    strings; it never renders anything and has no dependency on the
    mermaid CLI.

    Class attributes:
        MAX_NODES (int): Upper bound on the ``nodes`` list length.
        MAX_EDGES (int): Upper bound on the ``edges`` list length.
        MAX_PARTICIPANTS (int): Upper bound on ``participants``.
        MAX_MESSAGES (int): Upper bound on ``messages``.
        MAX_NOTES (int): Upper bound on ``notes``.
        MAX_ID_CHARS (int): Upper bound on any single id / name.
        MAX_TEXT_CHARS (int): Upper bound on any single label / text.
        MAX_SOURCE_CHARS (int): Upper bound on the lint ``source``.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "mermaid_flow_tool"
    description: str = (
        "Mermaid diagram source generation tool — pure Python stdlib, "
        "no rendering and no mermaid CLI dependency. Builds "
        "flowchart TD/LR source from nodes/edges specs (mode='flowchart'), "
        "sequenceDiagram source from participants/messages/notes specs "
        "(mode='sequence'), and runs a basic sanity lint (declaration "
        "keyword, unbalanced quotes, reserved keyword node ids such as "
        "'end'/'style'/'note', dangling arrows) over a Mermaid source "
        "string (mode='lint')."
    )

    MODES: ClassVar[tuple] = ("flowchart", "sequence", "lint")
    DIRECTIONS: ClassVar[tuple] = ("TD", "LR")
    # shape name -> (opening delimiter, closing delimiter)
    SHAPES: ClassVar[dict[str, tuple]] = {
        "rect": ("[", "]"),
        "round": ("(", ")"),
        "stadium": ("([", "])"),
        "diamond": ("{", "}"),
        "hexagon": ("{{", "}}"),
        "circle": ("((", "))"),
        "parallelogram": ("[/", "/]"),
    }
    # arrow name -> mermaid link token
    ARROWS: ClassVar[dict[str, str]] = {
        "arrow": "-->",
        "dotted": "-.->",
        "thick": "==>",
    }
    # sequence message kind -> mermaid arrow token
    MESSAGE_KINDS: ClassVar[dict[str, str]] = {
        "solid": "->",
        "dashed": "-->",
    }
    # Mermaid label conventions: pipe replacement and quote entity.
    PIPE_REPLACEMENT: ClassVar[str] = "❘"  # U+2758 LIGHT VERTICAL BAR
    QUOTE_ENTITY: ClassVar[str] = "#quot;"
    # Mermaid entity for a literal semicolon in sequence text (a raw
    # semicolon is a statement separator there and truncates the text).
    SEMICOLON_ENTITY: ClassVar[str] = "#59;"

    MAX_NODES: ClassVar[int] = 500
    MAX_EDGES: ClassVar[int] = 1000
    MAX_PARTICIPANTS: ClassVar[int] = 100
    MAX_MESSAGES: ClassVar[int] = 2000
    MAX_NOTES: ClassVar[int] = 500
    MAX_ID_CHARS: ClassVar[int] = 200
    MAX_TEXT_CHARS: ClassVar[int] = 2000
    MAX_SOURCE_CHARS: ClassVar[int] = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        direction: Any = None,
        nodes: Any = None,
        edges: Any = None,
        participants: Any = None,
        messages: Any = None,
        notes: Any = None,
        source: Any = None,
    ) -> dict[str, Any]:
        """Generate or lint Mermaid diagram source.

        Args:
            mode (str): One of ``flowchart``, ``sequence`` or ``lint``.
            direction (str): Flowchart direction — ``TD`` (default) or
                ``LR``. Flowchart mode only.
            nodes (list[dict]): Flowchart nodes, each ``{id, label?,
                shape?}``; ``id`` is required, ``label`` and ``shape``
                (rect/round/stadium/diamond/hexagon/circle/
                parallelogram) are optional. A node without a label is
                declared bare (the sanitized id is shown).
            edges (list[dict]): Flowchart edges, each ``{from, to,
                label?, arrow?}``; ``from`` / ``to`` must reference
                declared node ids, ``arrow`` is one of arrow/dotted/
                thick. Optional (defaults to no edges).
            participants (list[dict]): Sequence participants, each
                ``{name, as?}``; names are sanitized like flowchart ids
                (see module docstring) and the original name is used as
                the display alias automatically when sanitization
                changed it and no explicit ``as`` was given.
            messages (list[dict]): Sequence messages, each ``{from, to,
                text, kind?}``; ``from`` / ``to`` must reference
                declared participants and ``kind`` is solid (default)
                or dashed.
            notes (list[dict]): Optional sequence notes, each ``{over,
                text}`` where ``over`` is one participant name or a
                list of one or two participant names.
            source (str): The Mermaid source to lint. Lint mode only.

        Returns:
            Dict[str, Any]: For the generation modes, a ``result``
                string with the diagram source plus counts (and
                ``id_mapping`` whenever any id was sanitized). For the
                lint mode, ``ok``, ``lines_checked`` and a list of
                ``issues`` (each ``{line, check, message}``). Lint is a
                basic sanity pass, not a full Mermaid parser.

        Raises:
            ValueError: If any parameter is malformed (before any
                generation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "flowchart":
            return self._run_flowchart(direction, nodes, edges)
        if mode == "sequence":
            return self._run_sequence(participants, messages, notes)
        return self._run_lint(source)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any generation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"mermaid_flow_tool: {message}")

    @classmethod
    def _validate_id_like(cls, value: Any, what: str) -> str:
        """Validate an identifier (node id / participant name)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{what} must be a non-empty string (got '')")
        if len(value) > cls.MAX_ID_CHARS:
            cls._invalid(
                f"{what} exceeds the {cls.MAX_ID_CHARS}-character limit "
                f"(got {len(value)} characters)"
            )
        if _CONTROL_CHARS.search(value):
            cls._invalid(
                f"{what} must not contain control characters such as "
                "newlines or tabs"
            )
        return value

    @classmethod
    def _validate_label(cls, value: Any, what: str) -> str:
        """Validate a label / display text / message text field."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{what} must be a non-empty string (got '')")
        if len(value) > cls.MAX_TEXT_CHARS:
            cls._invalid(
                f"{what} exceeds the {cls.MAX_TEXT_CHARS}-character limit "
                f"(got {len(value)} characters)"
            )
        if _CONTROL_CHARS.search(value):
            cls._invalid(
                f"{what} must not contain control characters such as "
                "newlines or tabs"
            )
        return value

    @classmethod
    def _validate_list(
        cls, items: Any, what: str, allow_empty: bool, max_items: int
    ) -> list:
        """Validate that a spec field is a list within the size cap."""
        if items is None:
            items = []
        if isinstance(items, bool) or not isinstance(items, list):
            cls._invalid(f"{what} must be a list of objects (got {items!r})")
        if not items and not allow_empty:
            cls._invalid(f"{what} must be a non-empty list (got [])")
        if len(items) > max_items:
            cls._invalid(
                f"{what} exceeds the {max_items}-item limit "
                f"(got {len(items)} items)"
            )
        return items

    # ------------------------------------------------------------------ #
    # Deterministic id sanitization
    # ------------------------------------------------------------------ #

    @classmethod
    def _build_id_map(
        cls,
        raw_ids: list,
        reserved: "frozenset[str]" = _RESERVED_FLOWCHART_IDS,
        case_insensitive: bool = False,
    ) -> dict[str, str]:
        """Sanitize identifiers deterministically.

        Every character outside ``[A-Za-z0-9_]`` becomes ``_`` (one per
        character); ids that collide with a Mermaid statement keyword
        (see ``_RESERVED_FLOWCHART_IDS`` / ``_RESERVED_SEQUENCE_IDS``)
        get a trailing underscore; distinct raw ids that still collide
        get ``_2``, ``_3``, ... suffixes in input order. Flowchart
        keyword collisions are exact-case (``Style`` is a legal id);
        sequence keyword collisions are case-insensitive (``Note``
        breaks a sequence diagram like ``note``).
        """
        reserved_lower = {word.lower() for word in reserved} \
            if case_insensitive else reserved
        mapping: dict[str, str] = {}
        used: set[str] = set()
        for raw in raw_ids:
            sanitized = _INVALID_ID_CHARS.sub("_", raw)
            check = sanitized.lower() if case_insensitive else sanitized
            if check in reserved_lower:
                sanitized += "_"
            candidate = sanitized
            suffix = 2
            while candidate in used:
                candidate = f"{sanitized}_{suffix}"
                suffix += 1
            mapping[raw] = candidate
            used.add(candidate)
        return mapping

    # ------------------------------------------------------------------ #
    # Label rendering (mermaid escaping conventions)
    # ------------------------------------------------------------------ #

    @classmethod
    def _render_node_label(cls, label: str) -> str:
        """Render a node label, quoting and escaping where needed."""
        label = label.replace("|", cls.PIPE_REPLACEMENT)
        if _NEEDS_QUOTES.search(label):
            return '"' + label.replace('"', cls.QUOTE_ENTITY) + '"'
        return label

    @classmethod
    def _render_edge_label(cls, label: str) -> str:
        """Render an edge label (pipes and brackets break |label| syntax)."""
        label = label.replace("|", cls.PIPE_REPLACEMENT)
        for raw, entity in _EDGE_LABEL_ENTITIES:
            label = label.replace(raw, entity)
        return label

    @classmethod
    def _render_sequence_text(cls, text: str) -> str:
        """Render free sequence text (a raw ';' splits statements)."""
        return text.replace(";", cls.SEMICOLON_ENTITY)

    @classmethod
    def _render_alias(cls, alias: str) -> str:
        """Render a display alias (quotes would break lint parity)."""
        return cls._render_sequence_text(alias).replace(
            '"', cls.QUOTE_ENTITY
        )

    # ------------------------------------------------------------------ #
    # flowchart mode
    # ------------------------------------------------------------------ #

    def _run_flowchart(
        self, direction: Any, nodes: Any, edges: Any
    ) -> dict[str, Any]:
        """Generate ``flowchart TD/LR`` source."""
        if direction is None:
            direction = "TD"
        if isinstance(direction, bool) or not isinstance(direction, str) \
                or direction not in self.DIRECTIONS:
            self._invalid(
                "direction must be one of: "
                f"{', '.join(self.DIRECTIONS)} (got {direction!r})"
            )

        node_specs = self._validate_list(
            nodes, "nodes", allow_empty=False, max_items=self.MAX_NODES
        )
        for index, node in enumerate(node_specs):
            if isinstance(node, bool) or not isinstance(node, dict):
                self._invalid(
                    f"node at index {index} must be an object with an 'id' "
                    f"key (got {node!r})"
                )
            node_id = self._validate_id_like(node.get("id"), f"node id at index {index}")
            label = node.get("label")
            if label is not None:
                self._validate_label(label, f"label of node {node_id!r}")
            shape = node.get("shape", "rect")
            if shape is None:
                shape = "rect"
            if isinstance(shape, bool) or not isinstance(shape, str) \
                    or shape not in self.SHAPES:
                self._invalid(
                    f"shape of node {node_id!r} must be one of: "
                    f"{', '.join(self.SHAPES)} (got {shape!r})"
                )

        declared_ids = [node["id"] for node in node_specs]
        if len(set(declared_ids)) != len(declared_ids):
            seen: set[str] = set()
            for node_id in declared_ids:
                if node_id in seen:
                    self._invalid(f"duplicate node id: {node_id!r}")
                seen.add(node_id)

        edge_specs = self._validate_list(
            edges, "edges", allow_empty=True, max_items=self.MAX_EDGES
        )
        unknown: list[str] = []
        for index, edge in enumerate(edge_specs):
            if isinstance(edge, bool) or not isinstance(edge, dict):
                self._invalid(
                    f"edge at index {index} must be an object with 'from' "
                    f"and 'to' keys (got {edge!r})"
                )
            for key in ("from", "to"):
                endpoint = edge.get(key)
                if endpoint is None or isinstance(endpoint, bool) \
                        or not isinstance(endpoint, str) or not endpoint:
                    self._invalid(
                        f"edge at index {index}: {key!r} must be a declared "
                        f"node id (got {endpoint!r})"
                    )
                if endpoint not in declared_ids and endpoint not in unknown:
                    unknown.append(endpoint)
            label = edge.get("label")
            if label is not None:
                self._validate_label(label, f"label of edge at index {index}")
            arrow = edge.get("arrow", "arrow")
            if arrow is None:
                arrow = "arrow"
            if isinstance(arrow, bool) or not isinstance(arrow, str) \
                    or arrow not in self.ARROWS:
                self._invalid(
                    f"arrow of edge at index {index} must be one of: "
                    f"{', '.join(self.ARROWS)} (got {arrow!r})"
                )
        if unknown:
            self._invalid(
                "edge endpoints reference undeclared node ids: "
                + ", ".join(repr(item) for item in unknown)
            )

        id_mapping = self._build_id_map(
            declared_ids, _RESERVED_FLOWCHART_IDS
        )
        lines = [f"flowchart {direction}"]
        for node in node_specs:
            sanitized = id_mapping[node["id"]]
            label = node.get("label")
            if label is None:
                lines.append(f"    {sanitized}")
            else:
                shape = node.get("shape") or "rect"
                opening, closing = self.SHAPES[shape]
                rendered = self._render_node_label(label)
                lines.append(f"    {sanitized}{opening}{rendered}{closing}")
        for edge in edge_specs:
            arrow_token = self.ARROWS[edge.get("arrow") or "arrow"]
            label = edge.get("label")
            label_part = (
                f"|{self._render_edge_label(label)}|" if label is not None else ""
            )
            lines.append(
                f"    {id_mapping[edge['from']]}{arrow_token}{label_part}"
                f"{id_mapping[edge['to']]}"
            )
        result: dict[str, Any] = {
            "mode": "flowchart",
            "direction": direction,
            "result": "\n".join(lines),
            "node_count": len(node_specs),
            "edge_count": len(edge_specs),
        }
        changed = {raw: san for raw, san in id_mapping.items() if raw != san}
        if changed:
            result["id_mapping"] = changed
        return result

    # ------------------------------------------------------------------ #
    # sequence mode
    # ------------------------------------------------------------------ #

    def _run_sequence(
        self, participants: Any, messages: Any, notes: Any
    ) -> dict[str, Any]:
        """Generate ``sequenceDiagram`` source."""
        participant_specs = self._validate_list(
            participants,
            "participants",
            allow_empty=False,
            max_items=self.MAX_PARTICIPANTS,
        )
        for index, participant in enumerate(participant_specs):
            if isinstance(participant, bool) or not isinstance(participant, dict):
                self._invalid(
                    f"participant at index {index} must be an object with a "
                    f"'name' key (got {participant!r})"
                )
            self._validate_id_like(
                participant.get("name"), f"participant name at index {index}"
            )
            alias = participant.get("as")
            if alias is not None:
                self._validate_label(
                    alias, f"display alias of participant {participant['name']!r}"
                )

        names = [p["name"] for p in participant_specs]
        if len(set(names)) != len(names):
            seen_names: set[str] = set()
            for name in names:
                if name in seen_names:
                    self._invalid(f"duplicate participant name: {name!r}")
                seen_names.add(name)

        message_specs = self._validate_list(
            messages, "messages", allow_empty=False, max_items=self.MAX_MESSAGES
        )
        unknown: list[str] = []
        for index, message in enumerate(message_specs):
            if isinstance(message, bool) or not isinstance(message, dict):
                self._invalid(
                    f"message at index {index} must be an object with "
                    f"'from', 'to' and 'text' keys (got {message!r})"
                )
            for key in ("from", "to"):
                endpoint = message.get(key)
                if endpoint is None or isinstance(endpoint, bool) \
                        or not isinstance(endpoint, str) or not endpoint:
                    self._invalid(
                        f"message at index {index}: {key!r} must be a "
                        f"declared participant name (got {endpoint!r})"
                    )
                if endpoint not in names and endpoint not in unknown:
                    unknown.append(endpoint)
            self._validate_label(
                message.get("text"), f"text of message at index {index}"
            )
            kind = message.get("kind", "solid")
            if kind is None:
                kind = "solid"
            if isinstance(kind, bool) or not isinstance(kind, str) \
                    or kind not in self.MESSAGE_KINDS:
                self._invalid(
                    f"kind of message at index {index} must be one of: "
                    f"{', '.join(self.MESSAGE_KINDS)} (got {kind!r})"
                )
        if unknown:
            self._invalid(
                "message endpoints reference undeclared participants: "
                + ", ".join(repr(item) for item in unknown)
            )

        note_specs = self._validate_list(
            notes, "notes", allow_empty=True, max_items=self.MAX_NOTES
        )
        note_unknown: list[str] = []
        for index, note in enumerate(note_specs):
            if isinstance(note, bool) or not isinstance(note, dict):
                self._invalid(
                    f"note at index {index} must be an object with 'over' "
                    f"and 'text' keys (got {note!r})"
                )
            over = note.get("over")
            if over is None or isinstance(over, bool):
                targets: list = []
            elif isinstance(over, str):
                targets = [over]
            elif isinstance(over, list):
                targets = over
            else:
                targets = []
            if not (1 <= len(targets) <= 2) or any(
                not isinstance(t, str) or not t for t in targets
            ):
                self._invalid(
                    f"note at index {index}: 'over' must be a declared "
                    "participant name or a list of one or two declared "
                    f"participant names (got {over!r})"
                )
            for target in targets:
                if target not in names and target not in note_unknown:
                    note_unknown.append(target)
            self._validate_label(
                note.get("text"), f"text of note at index {index}"
            )
        if note_unknown:
            self._invalid(
                "note 'over' references undeclared participants: "
                + ", ".join(repr(item) for item in note_unknown)
            )

        id_mapping = self._build_id_map(
            names, _RESERVED_SEQUENCE_IDS, case_insensitive=True
        )
        lines = ["sequenceDiagram"]
        for participant in participant_specs:
            name = participant["name"]
            sanitized = id_mapping[name]
            alias = participant.get("as")
            if alias is None and sanitized != name:
                # Keep the original spelling visible in the diagram.
                alias = name
            if alias is not None:
                lines.append(
                    f"    participant {sanitized} as {self._render_alias(alias)}"
                )
            else:
                lines.append(f"    participant {sanitized}")
        for message in message_specs:
            arrow_token = self.MESSAGE_KINDS[message.get("kind") or "solid"]
            lines.append(
                f"    {id_mapping[message['from']]}{arrow_token}"
                f"{id_mapping[message['to']]}: "
                f"{self._render_sequence_text(message['text'])}"
            )
        for note in note_specs:
            over = note["over"]
            if isinstance(over, list):
                over_names = ",".join(id_mapping[t] for t in over)
            else:
                over_names = id_mapping[over]
            lines.append(
                f"    note over {over_names}: "
                f"{self._render_sequence_text(note['text'])}"
            )
        result: dict[str, Any] = {
            "mode": "sequence",
            "result": "\n".join(lines),
            "participant_count": len(participant_specs),
            "message_count": len(message_specs),
            "note_count": len(note_specs),
        }
        changed = {raw: san for raw, san in id_mapping.items() if raw != san}
        if changed:
            result["id_mapping"] = changed
        return result

    # ------------------------------------------------------------------ #
    # lint mode (basic sanity pass — NOT a full mermaid parser)
    # ------------------------------------------------------------------ #

    def _run_lint(self, source: Any) -> dict[str, Any]:
        """Run a line-oriented sanity pass over Mermaid source.

        Checks: the diagram declaration keyword (flowchart / graph /
        sequenceDiagram) on the first meaningful line, per-line quote
        balance (for sequence diagrams only the part before the message
        colon — quote parity in free text is not a Mermaid rule), the
        reserved ``end`` keyword used as a flowchart node id
        (``subgraph`` opens are tracked so legitimate block-closing
        ``end`` lines are not flagged), other Mermaid statement keywords
        used as node ids or actor names, and arrow tokens with a missing
        source or target endpoint (for sequence diagrams the free text
        after the message colon is ignored — `A->A: see -->` is valid).
        Comment lines (``%%``) are skipped. Label text inside quotes,
        ``|pipes|`` and shape brackets is masked before the keyword
        checks so words like ``end`` inside labels do not false-positive.
        """
        if source is None or isinstance(source, bool) \
                or not isinstance(source, str):
            self._invalid(
                f"source must be a non-empty mermaid source string "
                f"(got {source!r})"
            )
        if not source.strip():
            self._invalid(
                "source must be a non-empty mermaid source string "
                "(got whitespace only)"
            )
        if len(source) > self.MAX_SOURCE_CHARS:
            self._invalid(
                f"source exceeds the {self.MAX_SOURCE_CHARS:,}-character "
                f"limit (got {len(source):,} characters)"
            )

        lines = source.splitlines()
        # (line number, stripped text) of every non-blank, non-comment line.
        meaningful = [
            (lineno, text.strip())
            for lineno, text in enumerate(lines, 1)
            if text.strip() and not text.strip().startswith("%%")
        ]
        issues: list[dict[str, Any]] = []
        diagram_type = None
        if not meaningful:
            issues.append(
                {
                    "line": 1,
                    "check": "diagram_keyword",
                    "message": (
                        "no diagram declaration found — the source contains "
                        "only blank or comment lines"
                    ),
                }
            )
        else:
            first_line, first_text = meaningful[0]
            match = _DIAGRAM_DECL.match(first_text)
            if match is None:
                issues.append(
                    {
                        "line": first_line,
                        "check": "diagram_keyword",
                        "message": (
                            "missing diagram declaration — the first "
                            "non-comment line must start with 'flowchart', "
                            "'graph' or 'sequenceDiagram'"
                        ),
                    }
                )
            else:
                keyword = match.group(1).lower()
                diagram_type = "sequence" if keyword == "sequencediagram" \
                    else "flowchart"

        subgraph_depth = 0
        for lineno, text in meaningful:
            # Sequence text after the message colon is free-form: quote
            # parity and trailing arrows there are valid Mermaid.
            if diagram_type == "sequence":
                structural = text.split(":", 1)[0]
            else:
                structural = text
            if structural.count('"') % 2 == 1:
                issues.append(
                    {
                        "line": lineno,
                        "check": "unbalanced_quotes",
                        "message": (
                            "line has an odd number of double-quote "
                            "characters — quotes in mermaid must be paired"
                        ),
                    }
                )
            if diagram_type == "flowchart" and _SUBGRAPH_OPEN.match(text):
                subgraph_depth += 1
            if diagram_type == "flowchart":
                masked = self._mask_label_spans(text)
                flagged_end = False
                for _ in _STANDALONE_END.finditer(masked):
                    if subgraph_depth > 0:
                        subgraph_depth -= 1
                    elif not flagged_end:
                        issues.append(
                            {
                                "line": lineno,
                                "check": "end_node_id",
                                "message": (
                                    "'end' is a reserved keyword in "
                                    "flowcharts and cannot be used as a "
                                    "node id — rename the node (e.g. "
                                    "'end1')"
                                ),
                            }
                        )
                        flagged_end = True
            if diagram_type is not None:
                reserved_ids, fold = (
                    (_RESERVED_SEQUENCE_IDS, True)
                    if diagram_type == "sequence"
                    else (_RESERVED_FLOWCHART_IDS, False)
                )
                masked = self._mask_label_spans(text)
                if diagram_type == "sequence":
                    masked = masked.split(":", 1)[0]
                # A bare `end` line legitimately closes alt/loop blocks
                # in sequence diagrams and subgraphs in flowcharts (via
                # the end_node_id check), and a bare `autonumber` line
                # legitimately enables numbering; only those keywords
                # mixed with other content — `end->A: hi`,
                # `autonumber->A` — are actor-name misuse.
                stripped_masked = masked.strip().strip(";").strip()
                bare_keyword_line = stripped_masked in ("end", "autonumber")
                for slot in _ID_SPLIT_ARROWS.split(masked):
                    word = slot.strip().strip(";").strip()
                    if not word:
                        continue
                    candidate = word.lower() if fold else word
                    if candidate in reserved_ids and not (
                        word in ("end", "autonumber")
                        and (bare_keyword_line or diagram_type == "flowchart")
                    ):
                        issues.append(
                            {
                                "line": lineno,
                                "check": "reserved_word_id",
                                "message": (
                                    f"{word!r} is a Mermaid statement "
                                    "keyword and cannot be used as a "
                                    "node id or actor name — rename it "
                                    "(e.g. append an underscore)"
                                ),
                            }
                        )
            for token in _ARROW_TOKENS:
                if structural.startswith(token):
                    issues.append(
                        {
                            "line": lineno,
                            "check": "dangling_arrow",
                            "message": (
                                f"line starts with the arrow token "
                                f"{token!r} — the arrow has no source "
                                "endpoint"
                            ),
                        }
                    )
                    break
            for token in _ARROW_TOKENS:
                if structural.endswith(token):
                    issues.append(
                        {
                            "line": lineno,
                            "check": "dangling_arrow",
                            "message": (
                                f"line ends with the arrow token {token!r} "
                                "— the arrow has no target endpoint"
                            ),
                        }
                    )
                    break
        return {
            "mode": "lint",
            "ok": not issues,
            "lines_checked": len(lines),
            "issues": issues,
        }

    @staticmethod
    def _mask_label_spans(text: str) -> str:
        """Remove label text so only structural tokens remain.

        Balanced ``"..."`` and ``|...|`` spans plus the contents of
        shape brackets (``(...)``/``[...]``/``{...}``, nested included)
        are stripped, leaving node ids, arrows and keywords in place.
        Lint keyword checks run against the masked text so the word
        ``end`` inside a node or edge label does not false-positive.
        """
        text = _QUOTED_SPANS.sub("", text)
        text = _PIPE_SPANS.sub("", text)
        previous = None
        while previous != text:
            previous = text
            for pattern in _BRACKET_GROUPS:
                text = pattern.sub("", text)
        return text

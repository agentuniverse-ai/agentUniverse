#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: plantuml_tool.py

"""PlantUML diagram source generation tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency PlantUML source
generator aimed at visualization agents. The tool never renders and
never shells out to the PlantUML jar or any plantuml CLI — it only
*generates* PlantUML source text from small structured specifications,
plus a basic syntax sanity lint, so agents can hand the output to any
PlantUML-compatible renderer (plantuml.com, IDE plug-ins, GitLab /
Gitee PlantUML pre-processing, ...).

PlantUML is a diagram ecosystem distinct from both Mermaid (see the
MermaidFlowTool) and raw Graphviz dot: its class diagram dialect covers
UML constructs neither of those covers — member visibility modifiers,
``interface`` / ``abstract`` / ``enum`` stereotypes, the composition /
aggregation diamond arrows and note attachment — and its sequence
dialect adds ``autonumber`` plus ``alt`` / ``loop`` / ``par`` / ``opt``
interaction frames.

Supported modes:

* ``class_diagram`` — build a UML class diagram from ``classes``
  (``{name, stereotype?, fields?, methods?, color?}``) and ``relations``
  (``{from, to, kind?, label?}``). Stereotypes: ``interface``,
  ``abstract``, ``enum`` (default plain ``class``). Fields:
  ``{visibility?, name, type?}`` with visibility one of ``+`` (default),
  ``-``, ``#``, ``~``. Methods: ``{visibility?, name, params?, return?}``
  with ``params`` a list of ``{name, type?}``. Relation kinds and their
  PlantUML arrows: ``extends`` ``<|--``, ``implements`` ``<|..``,
  ``composition`` ``*--``, ``aggregation`` ``o--``, ``association``
  ``--``, ``dependency`` ``..>``. Orientation: ``from`` renders on the
  left of the arrow and carries the hollow triangle (``<|``) or the
  composition / aggregation diamond (``*`` / ``o``), so for extends /
  implements / composition / aggregation ``from`` is the parent,
  interface or whole end and ``to`` the child / implementing / part
  end; for dependency the ``..>`` arrowhead lands on ``to``, so
  ``from`` is the dependent end. Optional ``notes`` (``{on, text}``)
  attach a note to a declared class (``note right of``).
* ``sequence`` — build a sequence diagram from ``participants``
  (``{name, as?, type?}`` with type one of actor / boundary / control /
  entity / database / participant), ``messages`` (``{from, to, text,
  kind?, activate?, deactivate_after?}`` with kind ``solid`` ``->``
  default / ``dashed`` ``-->``), optional ``notes`` (``{over: name |
  [a, b], text}``) and optional ``frames`` (``{kind: alt|loop|par|opt,
  label?, message_indexes}`` wrapping the given message indexes in an
  ``alt/loop/par/opt ... end`` block). ``autonumber`` (default False)
  turns on PlantUML message numbering. ``activate`` activates the
  message *receiver* (``to``) and ``deactivate_after`` deactivates the
  message *sender* (``from``) after the message — the canonical
  PlantUML reply pattern (``A -> B: request`` / ``activate B`` /
  ``B --> A: reply`` / ``deactivate B``); activations are strictly
  pair-checked (see below).
* ``validate`` — run a *basic sanity check* over a PlantUML source
  string: ``@startuml`` / ``@enduml`` delimiter balance (counted per
  line, so literal delimiters inside message text do not count), use
  of a message endpoint before its participant is declared,
  interaction frame containment (unclosed / stray ``end`` / frames
  that wrap zero messages) and multi-line note containment (a
  ``note over ...`` block that is never closed with ``end note``, or a
  stray ``end note``; note bodies themselves are skipped, so
  arrow-like or ``end``-like note text does not trip the other
  checks). This is deliberately NOT a full PlantUML parser — it is a
  cheap line-oriented heuristic pass; a clean result does not
  guarantee the source renders.

Determinism and escaping conventions (documented contract):

* Class and participant identifiers are sanitized to
  ``[A-Za-z0-9_]``: every invalid character is mapped to ``_`` (one per
  character). If two distinct original names still collide after
  sanitization, later ones (in input order) get ``_2``, ``_3``, ...
  suffixes. When sanitization changes a name, the *original spelling*
  is preserved as the display alias (``"Original Name" as Sanitized``)
  and the full ``id_mapping`` (original -> sanitized, changed entries
  only) is reported in the result whenever at least one id changed.
* Output order is exactly the input order. Class diagrams emit
  ``@startuml``, the classes (members in input order), the relations,
  the notes and ``@enduml``. Sequence diagrams emit ``@startuml``, the
  optional ``autonumber``, the participants, the messages (frames wrap
  their message ranges, activation lines follow their message), the
  notes and ``@enduml``. Frame bodies and class member blocks are
  indented with four spaces; lines are joined with a single ``\n``
  (no trailing newline).

Input validation is strict and happens before any generation:
malformed parameters (wrong types, empty class / participant /
message lists, unknown mode / stereotype / kind / visibility / arrow
kind, duplicate class / participant names, duplicate field names or
method signatures inside one class, relation endpoints or note targets
that reference *undeclared* names, frame indexes out of range or not
an ascending contiguous run, overlapping or out-of-order frames,
activation lines that are not strictly paired, member names that are
not plain identifiers, names containing double quotes, text fields
containing control characters, oversized inputs) raise a
``ValueError``, mirroring the other common tools. Free-text fields
(labels, message and note text) may contain colons and double quotes:
those are inert in PlantUML display text.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Characters that may appear in a sanitized PlantUML identifier.
_INVALID_ID_CHARS = re.compile(r"[^A-Za-z0-9_]")
# Control characters are rejected in every text field.
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
# A member (field / method / parameter) name must be a plain identifier.
_MEMBER_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# A color is a color word or a 6-digit hex triplet.
_COLOR_WORD = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
_COLOR_HEX = re.compile(r"^[0-9A-Fa-f]{6}$")

# validate mode: participant / actor style declaration lines.
_DECL_LINE = re.compile(
    r"^(?:participant|actor|boundary|control|entity|database)\s+(.+)$"
)
_DECL_AS = re.compile(r"\s+as\s+([A-Za-z0-9_]+)\s*$")
_DECL_QUOTED = re.compile(r'^"([^"]*)"\s*(?:as\s+([A-Za-z0-9_]+))?')
# validate mode: a message line needs spaced '->' or '-->' arrows.
_MSG_LINE = re.compile(r"^(\S+)\s+(-->|->)\s+(\S+)")
# validate mode: interaction frame opens and the closing 'end'.
_FRAME_OPEN = re.compile(r"^(?:alt|loop|par|opt)\b")
_FRAME_CLOSE = re.compile(r"^end\s*$")
# 'end note' closes a multi-line note, not a frame.
_END_NOTE = re.compile(r"^end\s+note\b")
_NOTE_LINE = re.compile(r"^note\b")


class PlantumlTool(Tool):
    """PlantUML diagram source generator built purely on the stdlib.

    The tool generates PlantUML ``class_diagram`` / ``sequence`` source
    from structured specifications and lints PlantUML source strings;
    it never renders anything and has no dependency on the plantuml jar
    or CLI.

    Class attributes:
        MAX_CLASSES (int): Upper bound on the ``classes`` list length.
        MAX_RELATIONS (int): Upper bound on the ``relations`` list.
        MAX_PARTICIPANTS (int): Upper bound on ``participants``.
        MAX_MESSAGES (int): Upper bound on ``messages``.
        MAX_NOTES (int): Upper bound on ``notes``.
        MAX_FRAMES (int): Upper bound on ``frames``.
        MAX_PARAMS (int): Upper bound on one method's ``params``.
        MAX_NAME_CHARS (int): Upper bound on any single id / name.
        MAX_TEXT_CHARS (int): Upper bound on any single text field.
        MAX_SOURCE_CHARS (int): Upper bound on the lint ``source``.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "plantuml_tool"
    description: str = (
        "PlantUML diagram source generation tool — pure Python stdlib, "
        "no rendering and no plantuml jar/CLI dependency. Builds UML "
        "class diagram source from classes/relations/notes specs "
        "(mode='class_diagram') with stereotypes, visibility-modified "
        "fields/methods and the six UML relation arrows, sequence "
        "diagram source from participants/messages/notes/frames specs "
        "(mode='sequence') with autonumber, receiver-activation / "
        "sender-deactivation lines and alt/loop/par/opt frames, and "
        "runs a basic sanity lint (@startuml/@enduml balance, "
        "participant-before-use, frame containment, multi-line note "
        "containment) over a PlantUML source string (mode='validate')."
    )

    MODES: ClassVar[tuple] = ("class_diagram", "sequence", "validate")
    STEREOTYPES: ClassVar[dict[str, str]] = {
        None: "class",
        "interface": "interface",
        "abstract": "abstract class",
        "enum": "enum",
    }
    VISIBILITIES: ClassVar[tuple] = ("+", "-", "#", "~")
    # relation kind -> (arrow, from-role description)
    RELATION_KINDS: ClassVar[dict[str, str]] = {
        "extends": "<|--",
        "implements": "<|..",
        "composition": "*--",
        "aggregation": "o--",
        "association": "--",
        "dependency": "..>",
    }
    PARTICIPANT_TYPES: ClassVar[tuple] = (
        "participant", "actor", "boundary", "control", "entity", "database",
    )
    MESSAGE_KINDS: ClassVar[dict[str, str]] = {
        "solid": "->",
        "dashed": "-->",
    }
    FRAME_KINDS: ClassVar[tuple] = ("alt", "loop", "par", "opt")

    MAX_CLASSES: ClassVar[int] = 200
    MAX_RELATIONS: ClassVar[int] = 500
    MAX_PARTICIPANTS: ClassVar[int] = 100
    MAX_MESSAGES: ClassVar[int] = 2000
    MAX_NOTES: ClassVar[int] = 500
    MAX_FRAMES: ClassVar[int] = 100
    MAX_PARAMS: ClassVar[int] = 20
    MAX_NAME_CHARS: ClassVar[int] = 200
    MAX_TEXT_CHARS: ClassVar[int] = 2000
    MAX_SOURCE_CHARS: ClassVar[int] = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        classes: Any = None,
        relations: Any = None,
        notes: Any = None,
        participants: Any = None,
        messages: Any = None,
        frames: Any = None,
        autonumber: Any = None,
        source: Any = None,
    ) -> dict[str, Any]:
        """Generate or lint PlantUML diagram source.

        Args:
            mode (str): One of ``class_diagram``, ``sequence`` or
                ``validate``.
            classes (list[dict]): Class diagram classes, each ``{name,
                stereotype?, fields?, methods?, color?}`` with
                stereotype one of interface / abstract / enum, fields
                ``{visibility?, name, type?}`` and methods
                ``{visibility?, name, params?, return?}``. Visibility is
                one of ``+`` (default), ``-``, ``#``, ``~``. Class
                diagram mode only (required).
            relations (list[dict]): Class diagram relations, each
                ``{from, to, kind?, label?}`` with kind one of extends
                (<|--), implements (<|..), composition (*--),
                aggregation (o--), association (--), dependency (..>);
                both endpoints must reference declared class names.
                ``from`` renders on the left of the arrow and carries
                the triangle / diamond, so it is the parent, interface
                or whole end for extends / implements / composition /
                aggregation, while for dependency the arrowhead lands
                on ``to`` (``from`` is the dependent end). Optional.
            notes (list[dict]): Class diagram notes, each ``{on, text}``
                attaching a ``note right of`` to the declared class
                ``on``. Optional. (For the sequence mode the note shape
                is ``{over, text}`` — see the module docstring.)
            participants (list[dict]): Sequence participants, each
                ``{name, as?, type?}`` with type one of actor /
                boundary / control / entity / database / participant
                (default). Sequence mode only (required).
            messages (list[dict]): Sequence messages, each ``{from, to,
                text, kind?, activate?, deactivate_after?}``;
                ``from`` / ``to`` must reference declared participants,
                kind is solid (default) or dashed, ``activate``
                activates the receiver (``to``) and
                ``deactivate_after`` deactivates the sender (``from``)
                right after the message (strict pairing: every
                activation is closed by a later ``deactivate_after``
                and none repeats).
            frames (list[dict]): Optional sequence interaction frames,
                each ``{kind: alt|loop|par|opt, label?,
                message_indexes}`` where ``message_indexes`` is a
                non-empty ascending contiguous run of message indexes
                (0-based); frames must not overlap and must be given
                in start order.
            autonumber (bool): Turn on PlantUML ``autonumber`` message
                numbering. Default False. Sequence mode only.
            source (str): The PlantUML source to lint. Validate mode
                only.

        Returns:
            Dict[str, Any]: For the generation modes, a ``result``
                string with the PlantUML source plus counts (and
                ``id_mapping`` whenever any name was sanitized). For
                the validate mode, ``ok``, ``lines_checked`` and a list
                of ``issues`` (each ``{line, check, message}``) with
                checks named ``delimiter_balance``,
                ``participant_before_use``, ``frame_containment`` and
                ``note_containment``. The lint is a basic sanity pass,
                not a full PlantUML parser.

        Raises:
            ValueError: If any parameter is malformed (before any
                generation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "class_diagram":
            return self._run_class_diagram(classes, relations, notes)
        if mode == "sequence":
            return self._run_sequence(
                participants, messages, notes, frames, autonumber
            )
        return self._run_validate(source)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any generation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"plantuml_tool: {message}")

    @classmethod
    def _validate_name(cls, value: Any, what: str) -> str:
        """Validate an identifier (class / participant name)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{what} must be a non-empty string (got '')")
        if len(value) > cls.MAX_NAME_CHARS:
            cls._invalid(
                f"{what} exceeds the {cls.MAX_NAME_CHARS}-character limit "
                f"(got {len(value)} characters)"
            )
        if '"' in value:
            cls._invalid(f"{what} must not contain double quotes")
        if _CONTROL_CHARS.search(value):
            cls._invalid(
                f"{what} must not contain control characters such as "
                "newlines or tabs"
            )
        return value

    @classmethod
    def _validate_text(cls, value: Any, what: str) -> str:
        """Validate a free-text field (label / message / note text)."""
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
    def _validate_member_name(cls, value: Any, what: str) -> str:
        """Validate a field / method / parameter name (plain id)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be an identifier (got {value!r})")
        if not _MEMBER_NAME.match(value):
            cls._invalid(
                f"{what} must match [A-Za-z_][A-Za-z0-9_]* (got {value!r})"
            )
        return value

    @classmethod
    def _validate_type(cls, value: Any, what: str) -> str:
        """Validate a field / parameter / return type expression."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{what} must be a non-empty string (got '')")
        if len(value) > cls.MAX_NAME_CHARS:
            cls._invalid(
                f"{what} exceeds the {cls.MAX_NAME_CHARS}-character limit "
                f"(got {len(value)} characters)"
            )
        if ":" in value or "{" in value or "}" in value or '"' in value:
            cls._invalid(
                f"{what} must not contain ':', '{{', '}}' or double quotes "
                f"(got {value!r})"
            )
        if _CONTROL_CHARS.search(value):
            cls._invalid(
                f"{what} must not contain control characters such as "
                "newlines or tabs"
            )
        return value

    @classmethod
    def _validate_visibility(cls, value: Any, what: str) -> str:
        """Validate a visibility modifier."""
        if value is None:
            return "+"
        if isinstance(value, bool) or not isinstance(value, str) \
                or value not in cls.VISIBILITIES:
            cls._invalid(
                f"{what} must be one of: {', '.join(cls.VISIBILITIES)} "
                f"(got {value!r})"
            )
        return value

    @classmethod
    def _validate_color(cls, value: Any, what: str) -> str:
        """Validate a color spec (word or 6-digit hex)."""
        if value is None or isinstance(value, bool) \
                or not isinstance(value, str) \
                or not (_COLOR_WORD.match(value) or _COLOR_HEX.match(value)):
            cls._invalid(
                f"{what} must be a color word (LightBlue) or a 6-digit hex "
                f"triplet (99CCFF) without the leading '#' (got {value!r})"
            )
        return value

    @classmethod
    def _validate_list(
        cls,
        value: Any,
        what: str,
        allow_empty: bool,
        max_items: int,
    ) -> list:
        """Validate that a spec argument is a list within bounds."""
        if value is None:
            cls._invalid(f"{what} must be a list (got None)")
        if isinstance(value, bool) or not isinstance(value, list):
            cls._invalid(f"{what} must be a list (got {value!r})")
        if not allow_empty and not value:
            cls._invalid(f"{what} must not be empty")
        if len(value) > max_items:
            cls._invalid(
                f"{what} exceeds the {max_items}-item limit "
                f"(got {len(value)} items)"
            )
        return value

    @classmethod
    def _validate_flag(cls, value: Any, what: str) -> bool:
        """Validate a boolean flag (activate / deactivate / autonumber)."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        cls._invalid(f"{what} must be a boolean (got {value!r})")

    @classmethod
    def _build_id_map(cls, names: list[str]) -> dict[str, str]:
        """Deterministically map raw names to sanitized PlantUML ids.

        Invalid characters become ``_`` (one per character); distinct
        raw names that collide afterwards get ``_2``, ``_3``, ...
        suffixes in input order.
        """
        mapping: dict[str, str] = {}
        used: set[str] = set()
        for raw in names:
            base = _INVALID_ID_CHARS.sub("_", raw)
            candidate = base
            counter = 2
            while candidate in used:
                candidate = f"{base}_{counter}"
                counter += 1
            mapping[raw] = candidate
            used.add(candidate)
        return mapping

    # ------------------------------------------------------------------ #
    # class_diagram mode
    # ------------------------------------------------------------------ #

    def _run_class_diagram(
        self, classes: Any, relations: Any, notes: Any
    ) -> dict[str, Any]:
        """Generate PlantUML class diagram source."""
        class_specs = self._validate_list(
            classes, "classes", allow_empty=False, max_items=self.MAX_CLASSES
        )
        relation_specs = self._validate_list(
            relations or [], "relations", allow_empty=True,
            max_items=self.MAX_RELATIONS,
        )
        note_specs = self._validate_list(
            notes or [], "notes", allow_empty=True, max_items=self.MAX_NOTES
        )

        declared_names: list[str] = []
        for index, spec in enumerate(class_specs):
            if isinstance(spec, bool) or not isinstance(spec, dict):
                self._invalid(
                    f"class at index {index} must be an object with a "
                    f"'name' key (got {spec!r})"
                )
            name = self._validate_name(
                spec.get("name"), f"name of class at index {index}"
            )
            if name in declared_names:
                self._invalid(f"duplicate class name: {name!r}")
            declared_names.append(name)
            stereotype = spec.get("stereotype")
            if stereotype is not None:
                if isinstance(stereotype, bool) \
                        or not isinstance(stereotype, str) \
                        or stereotype not in self.STEREOTYPES:
                    self._invalid(
                        f"stereotype of class {name!r} must be one of: "
                        f"{', '.join(k for k in self.STEREOTYPES if k)} "
                        f"(got {stereotype!r})"
                    )
            color = spec.get("color")
            if color is not None:
                self._validate_color(
                    color, f"color of class {name!r}"
                )
            self._validate_class_members(spec, name)

        unknown: list[str] = []
        for index, spec in enumerate(relation_specs):
            if isinstance(spec, bool) or not isinstance(spec, dict):
                self._invalid(
                    f"relation at index {index} must be an object with "
                    f"'from' and 'to' keys (got {spec!r})"
                )
            for key in ("from", "to"):
                endpoint = spec.get(key)
                if endpoint is None or isinstance(endpoint, bool) \
                        or not isinstance(endpoint, str) or not endpoint:
                    self._invalid(
                        f"relation at index {index}: {key!r} must be a "
                        f"declared class name (got {endpoint!r})"
                    )
                if endpoint not in declared_names \
                        and endpoint not in unknown:
                    unknown.append(endpoint)
            kind = spec.get("kind", "association")
            if kind is None:
                kind = "association"
            if isinstance(kind, bool) or not isinstance(kind, str) \
                    or kind not in self.RELATION_KINDS:
                self._invalid(
                    f"kind of relation at index {index} must be one of: "
                    f"{', '.join(self.RELATION_KINDS)} (got {kind!r})"
                )
            label = spec.get("label")
            if label is not None:
                self._validate_text(
                    label, f"label of relation at index {index}"
                )
        if unknown:
            self._invalid(
                "relation endpoints reference undeclared class names: "
                + ", ".join(repr(item) for item in unknown)
            )

        for index, spec in enumerate(note_specs):
            if isinstance(spec, bool) or not isinstance(spec, dict):
                self._invalid(
                    f"note at index {index} must be an object with 'on' "
                    f"and 'text' keys (got {spec!r})"
                )
            target = spec.get("on")
            if target is None or isinstance(target, bool) \
                    or not isinstance(target, str) or not target:
                self._invalid(
                    f"note at index {index}: 'on' must be a declared class "
                    f"name (got {target!r})"
                )
            if target not in declared_names:
                self._invalid(
                    f"note at index {index} references undeclared class "
                    f"name: {target!r}"
                )
            self._validate_text(
                spec.get("text"), f"text of note at index {index}"
            )

        id_mapping = self._build_id_map(declared_names)
        lines = ["@startuml"]
        for spec in class_specs:
            lines.extend(self._render_class(spec, id_mapping))
        for spec in relation_specs:
            kind = spec.get("kind") or "association"
            label = spec.get("label")
            label_part = f" : {label}" if label is not None else ""
            lines.append(
                f"{id_mapping[spec['from']]} "
                f"{self.RELATION_KINDS[kind]} "
                f"{id_mapping[spec['to']]}{label_part}"
            )
        for spec in note_specs:
            lines.append(
                f"note right of {id_mapping[spec['on']]} : {spec['text']}"
            )
        lines.append("@enduml")

        result: dict[str, Any] = {
            "mode": "class_diagram",
            "result": "\n".join(lines),
            "class_count": len(class_specs),
            "relation_count": len(relation_specs),
            "note_count": len(note_specs),
        }
        changed = {raw: san for raw, san in id_mapping.items() if raw != san}
        if changed:
            result["id_mapping"] = changed
        return result

    def _validate_class_members(self, spec: dict, name: str) -> None:
        """Validate the fields / methods lists of one class spec."""
        fields = spec.get("fields")
        if fields is None:
            fields = []
        if isinstance(fields, bool) or not isinstance(fields, list):
            self._invalid(
                f"fields of class {name!r} must be a list (got {fields!r})"
            )
        methods = spec.get("methods")
        if methods is None:
            methods = []
        if isinstance(methods, bool) or not isinstance(methods, list):
            self._invalid(
                f"methods of class {name!r} must be a list (got {methods!r})"
            )
        field_names: set[str] = set()
        for index, field in enumerate(fields):
            if isinstance(field, bool) or not isinstance(field, dict):
                self._invalid(
                    f"field at index {index} of class {name!r} must be an "
                    f"object with a 'name' key (got {field!r})"
                )
            field_name = self._validate_member_name(
                field.get("name"),
                f"name of field at index {index} of class {name!r}",
            )
            if field_name in field_names:
                self._invalid(
                    f"duplicate field name {field_name!r} in class {name!r}"
                )
            field_names.add(field_name)
            self._validate_visibility(
                field.get("visibility"),
                f"visibility of field {field_name!r} of class {name!r}",
            )
            field_type = field.get("type")
            if field_type is not None:
                self._validate_type(
                    field_type,
                    f"type of field {field_name!r} of class {name!r}",
                )
        method_sigs: set[tuple] = set()
        for index, method in enumerate(methods):
            if isinstance(method, bool) or not isinstance(method, dict):
                self._invalid(
                    f"method at index {index} of class {name!r} must be an "
                    f"object with a 'name' key (got {method!r})"
                )
            method_name = self._validate_member_name(
                method.get("name"),
                f"name of method at index {index} of class {name!r}",
            )
            params = method.get("params")
            if params is None:
                params = []
            if isinstance(params, bool) or not isinstance(params, list):
                self._invalid(
                    f"params of method {method_name!r} of class {name!r} "
                    f"must be a list (got {params!r})"
                )
            if len(params) > self.MAX_PARAMS:
                self._invalid(
                    f"params of method {method_name!r} of class {name!r} "
                    f"exceeds the {self.MAX_PARAMS}-item limit "
                    f"(got {len(params)} items)"
                )
            for p_index, param in enumerate(params):
                if isinstance(param, bool) or not isinstance(param, dict):
                    self._invalid(
                        f"param at index {p_index} of method {method_name!r} "
                        f"of class {name!r} must be an object with a 'name' "
                        f"key (got {param!r})"
                    )
                self._validate_member_name(
                    param.get("name"),
                    f"name of param at index {p_index} of method "
                    f"{method_name!r} of class {name!r}",
                )
                param_type = param.get("type")
                if param_type is not None:
                    self._validate_type(
                        param_type,
                        f"type of param at index {p_index} of method "
                        f"{method_name!r} of class {name!r}",
                    )
            signature = (method_name, len(params))
            if signature in method_sigs:
                self._invalid(
                    f"duplicate method signature {method_name!r} with "
                    f"{len(params)} parameter(s) in class {name!r}"
                )
            method_sigs.add(signature)
            self._validate_visibility(
                method.get("visibility"),
                f"visibility of method {method_name!r} of class {name!r}",
            )
            return_type = method.get("return")
            if return_type is not None:
                self._validate_type(
                    return_type,
                    f"return type of method {method_name!r} of class "
                    f"{name!r}",
                )

    def _render_class(
        self, spec: dict, id_mapping: dict[str, str]
    ) -> list[str]:
        """Render one class block (header plus member lines)."""
        raw_name = spec["name"]
        sanitized = id_mapping[raw_name]
        keyword = self.STEREOTYPES[spec.get("stereotype")]
        color = spec.get("color")
        header = keyword
        if sanitized == raw_name:
            header += f" {sanitized}"
        else:
            header += f' "{raw_name}" as {sanitized}'
        if color is not None:
            header += f" #{color}"
        fields = spec.get("fields") or []
        methods = spec.get("methods") or []
        if not fields and not methods:
            return [header]
        lines = [f"{header} {{"]
        for field in fields:
            visibility = field.get("visibility") or "+"
            member = f"    {visibility}{field['name']}"
            if field.get("type") is not None:
                member += f": {field['type']}"
            lines.append(member)
        for method in methods:
            visibility = method.get("visibility") or "+"
            params = method.get("params") or []
            rendered_params = ", ".join(
                param["name"] if param.get("type") is None
                else f"{param['name']}: {param['type']}"
                for param in params
            )
            member = f"    {visibility}{method['name']}({rendered_params})"
            if method.get("return") is not None:
                member += f": {method['return']}"
            lines.append(member)
        lines.append("}")
        return lines

    # ------------------------------------------------------------------ #
    # sequence mode
    # ------------------------------------------------------------------ #

    def _run_sequence(
        self,
        participants: Any,
        messages: Any,
        notes: Any,
        frames: Any,
        autonumber: Any,
    ) -> dict[str, Any]:
        """Generate PlantUML sequence diagram source."""
        participant_specs = self._validate_list(
            participants, "participants", allow_empty=False,
            max_items=self.MAX_PARTICIPANTS,
        )
        message_specs = self._validate_list(
            messages, "messages", allow_empty=False,
            max_items=self.MAX_MESSAGES,
        )
        note_specs = self._validate_list(
            notes or [], "notes", allow_empty=True, max_items=self.MAX_NOTES
        )
        frame_specs = self._validate_list(
            frames or [], "frames", allow_empty=True,
            max_items=self.MAX_FRAMES,
        )
        autonumber_flag = self._validate_flag(
            autonumber, "autonumber"
        )

        declared_names: list[str] = []
        for index, spec in enumerate(participant_specs):
            if isinstance(spec, bool) or not isinstance(spec, dict):
                self._invalid(
                    f"participant at index {index} must be an object with a "
                    f"'name' key (got {spec!r})"
                )
            name = self._validate_name(
                spec.get("name"), f"name of participant at index {index}"
            )
            if name in declared_names:
                self._invalid(f"duplicate participant name: {name!r}")
            declared_names.append(name)
            alias = spec.get("as")
            if alias is not None:
                self._validate_name(
                    alias, f"as of participant {name!r}"
                )
            p_type = spec.get("type")
            if p_type is not None:
                if isinstance(p_type, bool) or not isinstance(p_type, str) \
                        or p_type not in self.PARTICIPANT_TYPES:
                    self._invalid(
                        f"type of participant {name!r} must be one of: "
                        f"{', '.join(self.PARTICIPANT_TYPES)} (got {p_type!r})"
                    )

        active: list[str] = []
        unknown: list[str] = []
        for index, spec in enumerate(message_specs):
            if isinstance(spec, bool) or not isinstance(spec, dict):
                self._invalid(
                    f"message at index {index} must be an object with "
                    f"'from', 'to' and 'text' keys (got {spec!r})"
                )
            for key in ("from", "to"):
                endpoint = spec.get(key)
                if endpoint is None or isinstance(endpoint, bool) \
                        or not isinstance(endpoint, str) or not endpoint:
                    self._invalid(
                        f"message at index {index}: {key!r} must be a "
                        f"declared participant name (got {endpoint!r})"
                    )
                if endpoint not in declared_names \
                        and endpoint not in unknown:
                    unknown.append(endpoint)
            self._validate_text(
                spec.get("text"), f"text of message at index {index}"
            )
            kind = spec.get("kind", "solid")
            if kind is None:
                kind = "solid"
            if isinstance(kind, bool) or not isinstance(kind, str) \
                    or kind not in self.MESSAGE_KINDS:
                self._invalid(
                    f"kind of message at index {index} must be one of: "
                    f"{', '.join(self.MESSAGE_KINDS)} (got {kind!r})"
                )
            receiver = spec.get("to")
            sender = spec.get("from")
            activate = self._validate_flag(
                spec.get("activate"),
                f"activate of message at index {index}",
            )
            deactivate = self._validate_flag(
                spec.get("deactivate_after"),
                f"deactivate_after of message at index {index}",
            )
            if activate:
                if receiver in active:
                    self._invalid(
                        f"message at index {index} activates {receiver!r} "
                        f"which is already active"
                    )
                active.append(receiver)
            if deactivate:
                if sender not in active:
                    self._invalid(
                        f"message at index {index} deactivates {sender!r} "
                        f"which is not active"
                    )
                active.remove(sender)
        if unknown:
            self._invalid(
                "message endpoints reference undeclared participant names: "
                + ", ".join(repr(item) for item in unknown)
            )
        if active:
            self._invalid(
                "unmatched activate without a later deactivate_after for: "
                + ", ".join(repr(item) for item in active)
            )

        for index, spec in enumerate(note_specs):
            if isinstance(spec, bool) or not isinstance(spec, dict):
                self._invalid(
                    f"note at index {index} must be an object with 'over' "
                    f"and 'text' keys (got {spec!r})"
                )
            over = spec.get("over")
            if isinstance(over, bool) or not isinstance(over, (str, list)):
                self._invalid(
                    f"note at index {index}: 'over' must be one participant "
                    f"name or a list of one or two (got {over!r})"
                )
            names = [over] if isinstance(over, str) else over
            if not names or len(names) > 2:
                self._invalid(
                    f"note at index {index}: 'over' must be one participant "
                    f"name or a list of one or two (got {over!r})"
                )
            for name in names:
                if name is None or isinstance(name, bool) \
                        or not isinstance(name, str) or not name:
                    self._invalid(
                        f"note at index {index}: 'over' entries must be "
                        f"declared participant names (got {name!r})"
                    )
                if name not in declared_names:
                    self._invalid(
                        f"note at index {index} references undeclared "
                        f"participant name: {name!r}"
                    )
            self._validate_text(
                spec.get("text"), f"text of note at index {index}"
            )

        spans = self._validate_frames(frame_specs, len(message_specs))

        id_mapping = self._build_id_map(declared_names)
        lines = ["@startuml"]
        if autonumber_flag:
            lines.append("autonumber")
        for spec in participant_specs:
            raw_name = spec["name"]
            sanitized = id_mapping[raw_name]
            p_type = spec.get("type") or "participant"
            alias = spec.get("as")
            if sanitized != raw_name and alias is None:
                alias = raw_name
            if alias is not None:
                lines.append(f'{p_type} "{alias}" as {sanitized}')
            else:
                lines.append(f"{p_type} {sanitized}")
        frame_by_start = {start: spec for spec, start, _ in spans}
        end_by_start = {start: end for _, start, end in spans}
        open_frames: list[int] = []
        for index, spec in enumerate(message_specs):
            if index in frame_by_start:
                open_frames.append(index)
                frame_spec = frame_by_start[index]
                label = frame_spec.get("label")
                kind = frame_spec["kind"]
                if label is not None:
                    lines.append(f"{kind} {label}")
                else:
                    lines.append(kind)
            indent = "    " if open_frames else ""
            sender = id_mapping[spec["from"]]
            receiver = id_mapping[spec["to"]]
            kind = spec.get("kind") or "solid"
            lines.append(
                f"{indent}{sender} {self.MESSAGE_KINDS[kind]} {receiver} : "
                f"{spec['text']}"
            )
            if spec.get("activate"):
                lines.append(f"{indent}activate {receiver}")
            if spec.get("deactivate_after"):
                lines.append(f"{indent}deactivate {sender}")
            while open_frames and end_by_start[open_frames[-1]] == index:
                open_frames.pop()
                lines.append("end")
        for spec in note_specs:
            over = spec["over"]
            names = [over] if isinstance(over, str) else over
            rendered = ", ".join(id_mapping[name] for name in names)
            lines.append(f"note over {rendered} : {spec['text']}")
        lines.append("@enduml")

        result: dict[str, Any] = {
            "mode": "sequence",
            "result": "\n".join(lines),
            "participant_count": len(participant_specs),
            "message_count": len(message_specs),
            "note_count": len(note_specs),
            "frame_count": len(frame_specs),
            "autonumber": autonumber_flag,
        }
        changed = {raw: san for raw, san in id_mapping.items() if raw != san}
        if changed:
            result["id_mapping"] = changed
        return result

    def _validate_frames(
        self, frame_specs: list, message_count: int
    ) -> list[tuple[dict, int, int]]:
        """Validate frame specs; return (spec, start, end) in order."""
        spans: list[tuple[dict, int, int]] = []
        previous_end = -1
        for index, spec in enumerate(frame_specs):
            if isinstance(spec, bool) or not isinstance(spec, dict):
                self._invalid(
                    f"frame at index {index} must be an object with 'kind' "
                    f"and 'message_indexes' keys (got {spec!r})"
                )
            kind = spec.get("kind")
            if isinstance(kind, bool) or not isinstance(kind, str) \
                    or kind not in self.FRAME_KINDS:
                self._invalid(
                    f"kind of frame at index {index} must be one of: "
                    f"{', '.join(self.FRAME_KINDS)} (got {kind!r})"
                )
            label = spec.get("label")
            if label is not None:
                self._validate_text(
                    label, f"label of frame at index {index}"
                )
            indexes = spec.get("message_indexes")
            if indexes is None or isinstance(indexes, bool) \
                    or not isinstance(indexes, list) or not indexes:
                self._invalid(
                    f"message_indexes of frame at index {index} must be a "
                    f"non-empty list of message indexes (got {indexes!r})"
                )
            for i_index, value in enumerate(indexes):
                if isinstance(value, bool) or not isinstance(value, int):
                    self._invalid(
                        f"message_indexes of frame at index {index} must "
                        f"contain integers (got {value!r} at position "
                        f"{i_index})"
                    )
            for value in indexes:
                if value < 0 or value >= message_count:
                    self._invalid(
                        f"message_indexes of frame at index {index} must be "
                        f"within 0..{message_count - 1} (got {value})"
                    )
            if indexes != sorted(indexes):
                self._invalid(
                    f"message_indexes of frame at index {index} must be "
                    f"ascending (got {indexes!r})"
                )
            if len(set(indexes)) != len(indexes):
                self._invalid(
                    f"message_indexes of frame at index {index} must not "
                    f"contain duplicates (got {indexes!r})"
                )
            start, end = indexes[0], indexes[-1]
            if indexes != list(range(start, end + 1)):
                self._invalid(
                    f"message_indexes of frame at index {index} must form a "
                    f"contiguous run (got {indexes!r})"
                )
            if start <= previous_end:
                self._invalid(
                    f"frame at index {index} overlaps or follows out of "
                    f"order: it starts at message {start} but a previous "
                    f"frame already covers through message {previous_end}"
                )
            previous_end = end
            spans.append((spec, start, end))
        return spans

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(self, source: Any) -> dict[str, Any]:
        """Run a basic sanity lint over a PlantUML source string."""
        if source is None or isinstance(source, bool) \
                or not isinstance(source, str):
            self._invalid(
                f"source must be a non-empty string (got {source!r})"
            )
        if not source:
            self._invalid("source must be a non-empty string (got '')")
        if len(source) > self.MAX_SOURCE_CHARS:
            self._invalid(
                f"source exceeds the {self.MAX_SOURCE_CHARS}-character "
                f"limit (got {len(source)} characters)"
            )

        issues: list[dict[str, Any]] = []
        lines = source.split("\n")

        # --- @startuml / @enduml delimiter balance ------------------- #
        startuml_lines = [
            number for number, raw_line in enumerate(lines, start=1)
            if raw_line.strip().startswith("@startuml")
        ]
        enduml_lines = [
            number for number, raw_line in enumerate(lines, start=1)
            if raw_line.strip().startswith("@enduml")
        ]
        if not startuml_lines:
            issues.append({
                "line": 1,
                "check": "delimiter_balance",
                "message": "missing '@startuml' delimiter",
            })
        if not enduml_lines:
            issues.append({
                "line": len(lines),
                "check": "delimiter_balance",
                "message": "missing '@enduml' delimiter",
            })
        if len(startuml_lines) > 1:
            issues.append({
                "line": startuml_lines[1],
                "check": "delimiter_balance",
                "message": f"'@startuml' appears {len(startuml_lines)} "
                           f"times (expected exactly 1)",
            })
        if len(enduml_lines) > 1:
            issues.append({
                "line": enduml_lines[1],
                "check": "delimiter_balance",
                "message": f"'@enduml' appears {len(enduml_lines)} times "
                           f"(expected exactly 1)",
            })
        if startuml_lines and enduml_lines \
                and enduml_lines[0] < startuml_lines[0]:
            issues.append({
                "line": 1,
                "check": "delimiter_balance",
                "message": "'@enduml' appears before '@startuml'",
            })

        # --- participant-before-use, frame and note containment ------- #
        declared: set[str] = set()
        frame_stack: list[tuple[int, str]] = []
        in_note = False
        note_open_line = 0
        for number, raw_line in enumerate(lines, start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith(("'", "/'")):
                continue
            if stripped.startswith(("@startuml", "@enduml")):
                continue
            if in_note:
                if _END_NOTE.match(stripped):
                    in_note = False
                continue
            if _NOTE_LINE.match(stripped) and ":" not in stripped \
                    and not stripped.startswith('note "'):
                in_note = True
                note_open_line = number
                continue
            if _END_NOTE.match(stripped):
                issues.append({
                    "line": number,
                    "check": "note_containment",
                    "message": "'end note' without a matching multi-line "
                               "note",
                })
                continue
            match = _DECL_LINE.match(stripped)
            if match:
                declared.add(self._lint_declared_id(match.group(1)))
                continue
            match = _MSG_LINE.match(stripped)
            if match:
                endpoints = [match.group(1), match.group(3)]
                if endpoints[1].endswith(":"):
                    endpoints[1] = endpoints[1][:-1]
                for endpoint in endpoints:
                    if endpoint not in declared:
                        issues.append({
                            "line": number,
                            "check": "participant_before_use",
                            "message": f"message endpoint {endpoint!r} is "
                                       f"used before it is declared",
                        })
                if frame_stack:
                    start_line, kind, _ = frame_stack[-1]
                    frame_stack[-1] = (start_line, kind, True)
                continue
            if _FRAME_OPEN.match(stripped):
                frame_stack.append((number, stripped.split()[0], False))
                continue
            if _FRAME_CLOSE.match(stripped):
                if not frame_stack:
                    issues.append({
                        "line": number,
                        "check": "frame_containment",
                        "message": "'end' without a matching alt/loop/par/"
                                   "opt frame",
                    })
                else:
                    start_line, kind, has_message = frame_stack.pop()
                    if not has_message:
                        issues.append({
                            "line": start_line,
                            "check": "frame_containment",
                            "message": f"{kind} frame starting here wraps "
                                       f"zero messages",
                        })
                continue
        for start_line, kind, _has_message in frame_stack:
            issues.append({
                "line": start_line,
                "check": "frame_containment",
                "message": f"{kind} frame starting here is never closed "
                           f"with 'end'",
            })
        if in_note:
            issues.append({
                "line": note_open_line,
                "check": "note_containment",
                "message": "multi-line note starting here is never closed "
                           "with 'end note'",
            })

        return {
            "mode": "validate",
            "ok": not issues,
            "lines_checked": len(lines),
            "issues": issues,
        }

    @classmethod
    def _lint_declared_id(cls, rest: str) -> str:
        """Extract the reference id from a participant declaration rest."""
        rest = rest.strip()
        match = _DECL_QUOTED.match(rest)
        if match:
            return match.group(2) if match.group(2) else match.group(1)
        match = _DECL_AS.search(rest)
        if match:
            return match.group(1)
        return rest.split()[0]

#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_plantuml_tool.py

"""Offline unit tests for PlantumlTool.

The tool is built purely on the standard library and never renders
anything, shells out to a jar or touches the network, so this suite
runs fully offline. Every assertion is deterministic: the class_diagram
/ sequence modes are checked against exact expected PlantUML source
strings (each visibility modifier, each stereotype, each of the six
relation arrows, methods with parameters and return types, autonumber,
receiver-activation / sender-deactivation pairing, notes over single
participants and pairs, alt/loop/par/opt frames wrapping exactly their
message ranges, id sanitization with the reported mapping and display
aliases, colors), and the validate mode against exact issue payloads
(delimiter balance, participant-before-use, frame containment).
The error matrix covers every strict-validation branch.
"""

import re
import unittest

from agentuniverse.agent.action.tool.common_tool import PlantumlTool
from agentuniverse.agent.action.tool.common_tool.plantuml_tool import (
    PlantumlTool as DirectPlantumlTool,
)


class PlantumlToolClassDiagramTest(unittest.TestCase):
    """Exact-source ground truths for the class_diagram mode."""

    def setUp(self) -> None:
        self.tool = PlantumlTool()

    def test_minimal_class_without_members_exact(self) -> None:
        result = self.tool.execute(
            mode="class_diagram", classes=[{"name": "Foo"}]
        )
        self.assertEqual(
            result,
            {
                "mode": "class_diagram",
                "result": "@startuml\nclass Foo\n@enduml",
                "class_count": 1,
                "relation_count": 0,
                "note_count": 0,
            },
        )

    def test_two_classes_declared_in_input_order(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "Foo"}, {"name": "Bar"}],
        )
        self.assertEqual(
            result["result"],
            "@startuml\nclass Foo\nclass Bar\n@enduml",
        )

    def test_class_with_field_and_method_exact(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {
                    "name": "Circle",
                    "fields": [{"name": "radius", "type": "double"}],
                    "methods": [
                        {
                            "name": "area",
                            "params": [],
                            "return": "double",
                        }
                    ],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\n"
            "class Circle {\n"
            "    +radius: double\n"
            "    +area(): double\n"
            "}\n"
            "@enduml",
        )

    def test_default_visibility_is_public(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {
                    "name": "F",
                    "fields": [{"name": "x"}],
                    "methods": [{"name": "m"}],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\nclass F {\n    +x\n    +m()\n}\n@enduml",
        )

    def test_every_field_visibility_modifier(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {
                    "name": "Vis",
                    "fields": [
                        {"visibility": "+", "name": "pub"},
                        {"visibility": "-", "name": "priv"},
                        {"visibility": "#", "name": "prot"},
                        {"visibility": "~", "name": "pack"},
                    ],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\n"
            "class Vis {\n"
            "    +pub\n"
            "    -priv\n"
            "    #prot\n"
            "    ~pack\n"
            "}\n"
            "@enduml",
        )

    def test_every_method_visibility_modifier(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {
                    "name": "M",
                    "methods": [
                        {"visibility": "+", "name": "pub"},
                        {"visibility": "-", "name": "priv"},
                        {"visibility": "#", "name": "prot"},
                        {"visibility": "~", "name": "pack"},
                    ],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\n"
            "class M {\n"
            "    +pub()\n"
            "    -priv()\n"
            "    #prot()\n"
            "    ~pack()\n"
            "}\n"
            "@enduml",
        )

    def test_method_params_and_return_type_combinations(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {
                    "name": "S",
                    "methods": [
                        {"name": "noParamsNoReturn"},
                        {"name": "plainParams", "params": [
                            {"name": "a"}, {"name": "b"},
                        ]},
                        {"name": "typedParams", "params": [
                            {"name": "x", "type": "int"},
                            {"name": "ys", "type": "List<int>"},
                        ]},
                        {
                            "name": "typedAll",
                            "params": [{"name": "n", "type": "int"}],
                            "return": "Map<String, int>",
                        },
                        {"name": "onlyReturn", "return": "void"},
                    ],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\n"
            "class S {\n"
            "    +noParamsNoReturn()\n"
            "    +plainParams(a, b)\n"
            "    +typedParams(x: int, ys: List<int>)\n"
            "    +typedAll(n: int): Map<String, int>\n"
            "    +onlyReturn(): void\n"
            "}\n"
            "@enduml",
        )

    def test_stereotype_interface(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {
                    "name": "Shape",
                    "stereotype": "interface",
                    "methods": [{"name": "draw"}],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\ninterface Shape {\n    +draw()\n}\n@enduml",
        )

    def test_stereotype_abstract(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {
                    "name": "Base",
                    "stereotype": "abstract",
                    "fields": [{"name": "id", "type": "long"}],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\nabstract class Base {\n    +id: long\n}\n@enduml",
        )

    def test_stereotype_enum(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {
                    "name": "Color",
                    "stereotype": "enum",
                    "fields": [{"name": "RED"}, {"name": "GREEN"}],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\nenum Color {\n    +RED\n    +GREEN\n}\n@enduml",
        )

    def test_every_relation_kind_arrow(self) -> None:
        kinds = {
            "extends": "Vehicle <|-- Car",
            "implements": "Shape <|.. Circle",
            "composition": "Car *-- Wheel",
            "aggregation": "Team o-- Player",
            "association": "Student -- Course",
            "dependency": "Order ..> Printer",
        }
        for kind, expected_line in kinds.items():
            with self.subTest(kind=kind):
                result = self.tool.execute(
                    mode="class_diagram",
                    classes=[
                        {"name": "Vehicle"}, {"name": "Car"},
                        {"name": "Shape"}, {"name": "Circle"},
                        {"name": "Wheel"}, {"name": "Team"},
                        {"name": "Player"}, {"name": "Student"},
                        {"name": "Course"}, {"name": "Order"},
                        {"name": "Printer"},
                    ],
                    relations=[{
                        "from": expected_line.split(" ")[0],
                        "to": expected_line.split(" ")[-1],
                        "kind": kind,
                    }],
                )
                lines = result["result"].split("\n")
                self.assertEqual(lines[-2], expected_line)

    def test_relation_default_kind_is_association(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "A"}, {"name": "B"}],
            relations=[{"from": "A", "to": "B"}],
        )
        self.assertIn("A -- B", result["result"])

    def test_relation_with_label(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "Order"}, {"name": "LineItem"}],
            relations=[{
                "from": "Order", "to": "LineItem",
                "kind": "composition", "label": "1..*",
            }],
        )
        self.assertIn("Order *-- LineItem : 1..*", result["result"])

    def test_relations_keep_input_order(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "A"}, {"name": "B"}, {"name": "C"}],
            relations=[
                {"from": "A", "to": "B"},
                {"from": "C", "to": "A", "kind": "dependency"},
            ],
        )
        body = result["result"].split("\n")
        self.assertEqual(body[-3], "A -- B")
        self.assertEqual(body[-2], "C ..> A")

    def test_color_word_and_hex(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[
                {"name": "Sunny", "color": "LightBlue"},
                {"name": "Hexy", "color": "99CCFF",
                 "fields": [{"name": "n", "type": "int"}]},
            ],
        )
        self.assertIn("class Sunny #LightBlue", result["result"])
        self.assertIn("class Hexy #99CCFF {", result["result"])

    def test_class_note_attachment(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "Foo"}, {"name": "Bar"}],
            notes=[{"on": "Foo", "text": "this is a note"}],
        )
        self.assertEqual(
            result["result"],
            "@startuml\nclass Foo\nclass Bar\n"
            "note right of Foo : this is a note\n@enduml",
        )
        self.assertEqual(result["note_count"], 1)

    def test_name_sanitization_alias_and_mapping(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "My Class!"}, {"name": "Ok"}],
            relations=[{"from": "My Class!", "to": "Ok"}],
        )
        self.assertEqual(
            result["result"],
            '@startuml\nclass "My Class!" as My_Class_\nclass Ok\n'
            "My_Class_ -- Ok\n@enduml",
        )
        self.assertEqual(
            result["id_mapping"], {"My Class!": "My_Class_"}
        )

    def test_sanitization_collision_suffixes(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "a b"}, {"name": "a.b"}, {"name": "a_b"}],
        )
        self.assertEqual(
            result["result"],
            '@startuml\nclass "a b" as a_b\nclass "a.b" as a_b_2\n'
            'class "a_b" as a_b_3\n@enduml',
        )
        self.assertEqual(
            result["id_mapping"],
            {"a b": "a_b", "a.b": "a_b_2", "a_b": "a_b_3"},
        )

    def test_unsanitized_names_report_no_mapping(self) -> None:
        result = self.tool.execute(
            mode="class_diagram", classes=[{"name": "Plain"}]
        )
        self.assertNotIn("id_mapping", result)

    def test_deterministic_output(self) -> None:
        spec = {
            "mode": "class_diagram",
            "classes": [
                {
                    "name": "A", "stereotype": "interface",
                    "methods": [{"name": "go", "return": "void"}],
                },
                {"name": "B", "fields": [{"name": "x", "type": "int"}]},
            ],
            "relations": [
                {"from": "A", "to": "B", "kind": "implements",
                 "label": "realizes"},
            ],
        }
        self.assertEqual(
            self.tool.execute(**spec), self.tool.execute(**spec)
        )

    def test_relation_orientation_triangle_and_diamond_on_from(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "Parent"}, {"name": "Child"},
                     {"name": "Whole"}, {"name": "Part"},
                     {"name": "Dependent"}, {"name": "Provider"}],
            relations=[
                {"from": "Parent", "to": "Child", "kind": "extends"},
                {"from": "Whole", "to": "Part", "kind": "composition"},
                {"from": "Dependent", "to": "Provider",
                 "kind": "dependency"},
            ],
        )
        lines = result["result"].split("\n")
        self.assertIn("Parent <|-- Child", lines)
        self.assertIn("Whole *-- Part", lines)
        self.assertIn("Dependent ..> Provider", lines)

    def test_relation_label_with_colon_and_quotes_allowed(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "A"}, {"name": "B"}],
            relations=[{
                "from": "A", "to": "B",
                "label": 'ratio 1:2 say "hi"',
            }],
        )
        self.assertIn('A -- B : ratio 1:2 say "hi"', result["result"])

    def test_note_text_with_quotes_allowed(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{"name": "A"}],
            notes=[{"on": "A", "text": 'He said "no"'}],
        )
        self.assertIn('note right of A : He said "no"', result["result"])


class PlantumlToolSequenceTest(unittest.TestCase):
    """Exact-source ground truths for the sequence mode."""

    def setUp(self) -> None:
        self.tool = PlantumlTool()

    def test_minimal_sequence_exact(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "Alice"}, {"name": "Bob"}],
            messages=[{"from": "Alice", "to": "Bob", "text": "hello"}],
        )
        self.assertEqual(
            result,
            {
                "mode": "sequence",
                "result": (
                    "@startuml\nparticipant Alice\nparticipant Bob\n"
                    "Alice -> Bob : hello\n@enduml"
                ),
                "participant_count": 2,
                "message_count": 1,
                "note_count": 0,
                "frame_count": 0,
                "autonumber": False,
            },
        )

    def test_every_participant_type_keyword(self) -> None:
        types = {
            "actor": "actor U",
            "boundary": "boundary B",
            "control": "control C",
            "entity": "entity E",
            "database": "database D",
            "participant": "participant P",
        }
        for p_type, expected_line in types.items():
            with self.subTest(p_type=p_type):
                result = self.tool.execute(
                    mode="sequence",
                    participants=[{"name": expected_line.split(" ")[1],
                                   "type": p_type}],
                    messages=[{
                        "from": expected_line.split(" ")[1],
                        "to": expected_line.split(" ")[1],
                        "text": "self",
                    }],
                )
                self.assertIn(expected_line, result["result"])

    def test_default_participant_type(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "Svc"}],
            messages=[{"from": "Svc", "to": "Svc", "text": "tick"}],
        )
        self.assertIn("participant Svc", result["result"])

    def test_explicit_display_alias(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "db", "as": "Primary DB"}],
            messages=[{"from": "db", "to": "db", "text": "ping"}],
        )
        self.assertEqual(
            result["result"],
            '@startuml\nparticipant "Primary DB" as db\n'
            "db -> db : ping\n@enduml",
        )

    def test_name_sanitization_keeps_display(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "Msg Queue"}],
            messages=[{"from": "Msg Queue", "to": "Msg Queue",
                       "text": "poll"}],
        )
        self.assertEqual(
            result["result"],
            '@startuml\nparticipant "Msg Queue" as Msg_Queue\n'
            "Msg_Queue -> Msg_Queue : poll\n@enduml",
        )
        self.assertEqual(
            result["id_mapping"], {"Msg Queue": "Msg_Queue"}
        )

    def test_message_kind_solid_and_dashed(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[
                {"from": "A", "to": "B", "text": "sync call"},
                {"from": "B", "to": "A", "text": "async return",
                 "kind": "dashed"},
            ],
        )
        self.assertIn("A -> B : sync call", result["result"])
        self.assertIn("B --> A : async return", result["result"])

    def test_autonumber_emitted_first_and_omitted_by_default(self) -> None:
        participants = [{"name": "A"}, {"name": "B"}]
        messages = [{"from": "A", "to": "B", "text": "x"}]
        with_number = self.tool.execute(
            mode="sequence", participants=participants,
            messages=messages, autonumber=True,
        )
        without_number = self.tool.execute(
            mode="sequence", participants=participants, messages=messages,
        )
        self.assertEqual(
            with_number["result"],
            "@startuml\nautonumber\nparticipant A\nparticipant B\n"
            "A -> B : x\n@enduml",
        )
        self.assertNotIn("autonumber", without_number["result"])
        self.assertTrue(with_number["autonumber"])
        self.assertFalse(without_number["autonumber"])

    def test_activate_deactivate_canonical_pairing(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "User"}, {"name": "A"}],
            messages=[
                {"from": "User", "to": "A", "text": "DoWork",
                 "activate": True},
                {"from": "A", "to": "A", "text": "Internal call"},
                {"from": "A", "to": "User", "text": "Done",
                 "kind": "dashed", "deactivate_after": True},
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\n"
            "participant User\n"
            "participant A\n"
            "User -> A : DoWork\n"
            "activate A\n"
            "A -> A : Internal call\n"
            "A --> User : Done\n"
            "deactivate A\n"
            "@enduml",
        )

    def test_activate_and_deactivate_on_same_self_message(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[
                {"from": "A", "to": "A", "text": "quick",
                 "activate": True, "deactivate_after": True},
            ],
        )
        self.assertIn("A -> A : quick\nactivate A\ndeactivate A",
                      result["result"])

    def test_two_sequential_activations(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[
                {"from": "A", "to": "B", "text": "one", "activate": True},
                {"from": "B", "to": "A", "text": "ack",
                 "deactivate_after": True},
                {"from": "A", "to": "B", "text": "two", "activate": True},
                {"from": "B", "to": "A", "text": "ack2",
                 "deactivate_after": True},
            ],
        )
        lines = result["result"].split("\n")
        self.assertEqual(lines.count("activate B"), 2)
        self.assertEqual(lines.count("deactivate B"), 2)

    def test_note_over_single_participant(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[{"from": "A", "to": "B", "text": "x"}],
            notes=[{"over": "A", "text": "left alone"}],
        )
        self.assertIn("note over A : left alone", result["result"])

    def test_note_over_pair(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "Alice"}, {"name": "Bob"}],
            messages=[{"from": "Alice", "to": "Bob", "text": "hi"}],
            notes=[{"over": ["Alice", "Bob"], "text": "collaboration"}],
        )
        self.assertEqual(
            result["result"],
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "Alice -> Bob : hi\nnote over Alice, Bob : collaboration\n"
            "@enduml",
        )

    def test_notes_emitted_after_messages_in_input_order(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[{"from": "A", "to": "B", "text": "x"}],
            notes=[
                {"over": "B", "text": "second"},
                {"over": "A", "text": "first"},
            ],
        )
        self.assertTrue(
            result["result"].index("note over B : second")
            < result["result"].index("note over A : first"),
        )

    def test_every_frame_kind_wraps_exactly_its_messages(self) -> None:
        for kind in ("alt", "loop", "par", "opt"):
            with self.subTest(kind=kind):
                result = self.tool.execute(
                    mode="sequence",
                    participants=[{"name": "A"}, {"name": "B"}],
                    messages=[
                        {"from": "A", "to": "B", "text": "before"},
                        {"from": "A", "to": "B", "text": "inside"},
                        {"from": "A", "to": "B", "text": "after"},
                    ],
                    frames=[{
                        "kind": kind, "label": "guarded",
                        "message_indexes": [1],
                    }],
                )
                self.assertEqual(
                    result["result"],
                    "@startuml\n"
                    "participant A\n"
                    "participant B\n"
                    "A -> B : before\n"
                    f"{kind} guarded\n"
                    "    A -> B : inside\n"
                    "end\n"
                    "A -> B : after\n"
                    "@enduml",
                )

    def test_frame_without_label_emits_bare_keyword(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[{"from": "A", "to": "B", "text": "x"}],
            frames=[{"kind": "opt", "message_indexes": [0]}],
        )
        self.assertIn("\nopt\n    A -> B : x\nend\n", result["result"])

    def test_frame_covering_all_messages(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[
                {"from": "A", "to": "B", "text": "x"},
                {"from": "B", "to": "A", "text": "y"},
            ],
            frames=[{"kind": "par", "message_indexes": [0, 1]}],
        )
        self.assertEqual(
            result["result"],
            "@startuml\nparticipant A\nparticipant B\n"
            "par\n    A -> B : x\n    B -> A : y\nend\n@enduml",
        )
        self.assertEqual(result["frame_count"], 1)

    def test_two_sequential_frames(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[
                {"from": "A", "to": "B", "text": "one"},
                {"from": "A", "to": "B", "text": "two"},
                {"from": "A", "to": "B", "text": "three"},
            ],
            frames=[
                {"kind": "alt", "label": "first",
                 "message_indexes": [0]},
                {"kind": "loop", "label": "second",
                 "message_indexes": [1, 2]},
            ],
        )
        self.assertEqual(
            result["result"],
            "@startuml\nparticipant A\nparticipant B\n"
            "alt first\n    A -> B : one\nend\n"
            "loop second\n    A -> B : two\n    A -> B : three\nend\n"
            "@enduml",
        )

    def test_activation_lines_indented_inside_frames(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[
                {"from": "A", "to": "B", "text": "call", "activate": True},
                {"from": "B", "to": "A", "text": "ret",
                 "deactivate_after": True},
            ],
            frames=[{"kind": "loop", "label": "r",
                     "message_indexes": [0, 1]}],
        )
        self.assertIn(
            "loop r\n    A -> B : call\n    activate B\n"
            "    B -> A : ret\n    deactivate B\nend",
            result["result"],
        )

    def test_deterministic_output(self) -> None:
        spec = {
            "mode": "sequence",
            "participants": [
                {"name": "U", "type": "actor"}, {"name": "S"},
            ],
            "messages": [
                {"from": "U", "to": "S", "text": "go", "activate": True},
                {"from": "S", "to": "U", "text": "done", "kind": "dashed",
                 "deactivate_after": True},
            ],
            "autonumber": True,
        }
        self.assertEqual(
            self.tool.execute(**spec), self.tool.execute(**spec)
        )

    def test_message_text_with_quotes_and_colon_allowed(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[{
                "from": "A", "to": "B",
                "text": 'charge 1: "total" @enduml',
            }],
        )
        self.assertIn(
            'A -> B : charge 1: "total" @enduml', result["result"]
        )
        linted = self.tool.execute(
            mode="validate", source=result["result"]
        )
        self.assertEqual(linted["issues"], [])

    def test_cjk_participant_names_quoted_alias(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "用户服务"}, {"name": "网关"}],
            messages=[{"from": "用户服务", "to": "网关", "text": "请求"}],
        )
        self.assertEqual(
            result["result"],
            '@startuml\n'
            'participant "用户服务" as ____\n'
            'participant "网关" as __\n'
            '____ -> __ : 请求\n'
            '@enduml',
        )
        self.assertEqual(
            result["id_mapping"], {"用户服务": "____", "网关": "__"}
        )


class PlantumlToolValidateTest(unittest.TestCase):
    """Exact issue payloads for the validate mode."""

    def setUp(self) -> None:
        self.tool = PlantumlTool()

    def test_clean_sequence_source_passes(self) -> None:
        source = (
            "@startuml\n"
            "actor User\n"
            "participant Service\n"
            "User -> Service : request\n"
            "activate Service\n"
            "Service --> User : response\n"
            "deactivate Service\n"
            "@enduml"
        )
        self.assertEqual(
            self.tool.execute(mode="validate", source=source),
            {
                "mode": "validate",
                "ok": True,
                "lines_checked": 8,
                "issues": [],
            },
        )

    def test_clean_class_source_passes(self) -> None:
        source = (
            "@startuml\n"
            "interface Shape {\n"
            "    +draw(): void\n"
            "}\n"
            "class Circle\n"
            "Shape <|.. Circle\n"
            "@enduml"
        )
        self.assertEqual(
            self.tool.execute(mode="validate", source=source),
            {
                "mode": "validate",
                "ok": True,
                "lines_checked": 7,
                "issues": [],
            },
        )

    def test_missing_startuml(self) -> None:
        result = self.tool.execute(
            mode="validate", source="participant A\n@enduml"
        )
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["issues"]), 1)
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "delimiter_balance")
        self.assertIn("missing '@startuml'", issue["message"])

    def test_missing_enduml(self) -> None:
        result = self.tool.execute(
            mode="validate", source="@startuml\nparticipant A"
        )
        self.assertFalse(result["ok"])
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "delimiter_balance")
        self.assertIn("missing '@enduml'", issue["message"])

    def test_duplicate_delimiters(self) -> None:
        source = (
            "@startuml\nparticipant A\n@enduml\n@startuml\n@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        checks = [i["check"] for i in result["issues"]]
        messages = " | ".join(i["message"] for i in result["issues"])
        self.assertEqual(checks.count("delimiter_balance"), 2)
        self.assertIn("'@startuml' appears 2 times", messages)
        self.assertIn("'@enduml' appears 2 times", messages)

    def test_enduml_before_startuml(self) -> None:
        result = self.tool.execute(
            mode="validate", source="@enduml\n@startuml"
        )
        messages = " | ".join(i["message"] for i in result["issues"])
        self.assertIn("'@enduml' appears before '@startuml'", messages)

    def test_participant_used_before_declaration(self) -> None:
        source = (
            "@startuml\n"
            "A -> B : hello\n"
            "participant A\n"
            "participant B\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        self.assertFalse(result["ok"])
        before_issues = [i for i in result["issues"]
                         if i["check"] == "participant_before_use"]
        self.assertEqual(len(before_issues), 2)
        self.assertEqual({i["line"] for i in before_issues}, {2})

    def test_undeclared_endpoint(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "A -> Ghost : hello\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "participant_before_use")
        self.assertEqual(issue["line"], 3)
        self.assertIn("'Ghost'", issue["message"])

    def test_declared_via_alias_and_quote_are_recognized(self) -> None:
        source = (
            "@startuml\n"
            'participant "The Caller" as Caller\n'
            "database Store\n"
            "Caller -> Store : write\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        self.assertEqual(result["issues"], [])

    def test_self_message_ok(self) -> None:
        source = "@startuml\nparticipant A\nA -> A : tick\n@enduml"
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_unclosed_frame(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "participant B\n"
            "loop retry\n"
            "    A -> B : ping\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        self.assertEqual(len(result["issues"]), 1)
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "frame_containment")
        self.assertEqual(issue["line"], 4)
        self.assertIn("never closed", issue["message"])

    def test_stray_end_without_frame(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "A -> A : x\n"
            "end\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "frame_containment")
        self.assertIn("'end' without a matching", issue["message"])

    def test_empty_frame_wrapping_zero_messages(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "participant B\n"
            "A -> B : before\n"
            "alt cold branch\n"
            "end\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        self.assertEqual(len(result["issues"]), 1)
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "frame_containment")
        self.assertEqual(issue["line"], 5)
        self.assertIn("wraps zero messages", issue["message"])

    def test_nested_frames_balanced(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "alt outer\n"
            "    A -> A : one\n"
            "    opt inner\n"
            "        A -> A : two\n"
            "    end\n"
            "end\n"
            "@enduml"
        )
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_end_note_not_counted_as_frame_end(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "note over A\n"
            "multi-line note body\n"
            "end note\n"
            "@enduml"
        )
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_comments_and_blank_lines_skipped(self) -> None:
        source = (
            "@startuml\n"
            "' a full-line comment\n"
            "\n"
            "participant A\n"
            "A -> A : tick\n"
            "@enduml"
        )
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_double_arrow_line_not_a_false_message(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "A ->> A : broadcast\n"
            "@enduml"
        )
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_multiline_note_body_skipped(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "participant B\n"
            "note over A\n"
            "A -> B : sketch inside the note body\n"
            "end\n"
            "end note\n"
            "A -> B : real\n"
            "@enduml"
        )
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_note_body_frame_keyword_not_phantom_frame(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "note over A\n"
            "loop forever text\n"
            "end note\n"
            "A -> A : x\n"
            "@enduml"
        )
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_delimiter_literal_in_message_text_not_counted(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "participant B\n"
            "A -> B : the @enduml marker ends a diagram\n"
            "@enduml"
        )
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_named_startuml_delimiter_recognized(self) -> None:
        source = (
            "@startuml my-diagram\n"
            "participant A\n"
            "A -> A : x\n"
            "@enduml"
        )
        self.assertEqual(self.tool.execute(
            mode="validate", source=source)["issues"], [])

    def test_inline_note_with_colon_not_treated_as_multiline(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "note over A : quick memo\n"
            "A -> Ghost : x\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "participant_before_use")
        self.assertEqual(issue["line"], 4)

    def test_unclosed_multiline_note_flagged(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "note over A\n"
            "body that never ends\n"
            "A -> A : x\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        self.assertEqual(len(result["issues"]), 1)
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "note_containment")
        self.assertEqual(issue["line"], 3)
        self.assertIn("never closed", issue["message"])

    def test_stray_end_note_flagged(self) -> None:
        source = (
            "@startuml\n"
            "participant A\n"
            "end note\n"
            "A -> A : x\n"
            "@enduml"
        )
        result = self.tool.execute(mode="validate", source=source)
        issue = result["issues"][0]
        self.assertEqual(issue["check"], "note_containment")
        self.assertEqual(issue["line"], 3)
        self.assertIn("'end note' without", issue["message"])

    def test_second_delimiter_reported_on_its_line(self) -> None:
        source = (
            "@startuml\n"
            "@startuml\n"
            "@enduml\n"
            "@enduml\n"
        )
        result = self.tool.execute(mode="validate", source=source)
        by_check = [i for i in result["issues"]
                    if i["check"] == "delimiter_balance"]
        self.assertEqual([i["line"] for i in by_check], [2, 4])

    def test_round_trip_generated_source_passes_lint(self) -> None:
        generated = self.tool.execute(
            mode="sequence",
            participants=[{"name": "U", "type": "actor"}, {"name": "S"}],
            messages=[
                {"from": "U", "to": "S", "text": "go", "activate": True},
                {"from": "S", "to": "U", "text": "done",
                 "deactivate_after": True},
            ],
            frames=[{"kind": "loop", "label": "r",
                     "message_indexes": [0, 1]}],
            autonumber=True,
        )
        linted = self.tool.execute(
            mode="validate", source=generated["result"]
        )
        self.assertTrue(linted["ok"])


class PlantumlToolErrorTest(unittest.TestCase):
    """Every strict-validation branch raises ValueError."""

    def setUp(self) -> None:
        self.tool = PlantumlTool()

    def assert_invalid(self, fragment: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        message = str(ctx.exception)
        self.assertTrue(
            message.startswith("plantuml_tool: "),
            f"missing tool prefix: {message!r}",
        )
        self.assertIn(fragment, message)

    # --- mode and shared argument validation ----------------------- #

    def test_unknown_mode(self) -> None:
        self.assert_invalid(
            "mode must be one of", mode="deployment", classes=[{"name": "A"}],
        )

    # --- class_diagram: classes ------------------------------------ #

    def test_classes_missing(self) -> None:
        self.assert_invalid(
            "classes must be a list", mode="class_diagram",
        )

    def test_classes_empty(self) -> None:
        self.assert_invalid(
            "classes must not be empty", mode="class_diagram", classes=[],
        )

    def test_classes_not_a_list(self) -> None:
        self.assert_invalid(
            "classes must be a list", mode="class_diagram", classes="Foo",
        )

    def test_class_not_an_object(self) -> None:
        self.assert_invalid(
            "class at index 0 must be an object",
            mode="class_diagram", classes=["Foo"],
        )

    def test_class_missing_name(self) -> None:
        self.assert_invalid(
            "name of class at index 0",
            mode="class_diagram", classes=[{"fields": []}],
        )

    def test_class_name_not_string(self) -> None:
        self.assert_invalid(
            "name of class at index 0 must be a non-empty string",
            mode="class_diagram", classes=[{"name": 42}],
        )

    def test_class_name_with_quotes(self) -> None:
        self.assert_invalid(
            "must not contain double quotes",
            mode="class_diagram", classes=[{"name": 'Ev"il'}],
        )

    def test_class_name_too_long(self) -> None:
        self.assert_invalid(
            "exceeds the 200-character limit",
            mode="class_diagram", classes=[{"name": "a" * 201}],
        )

    def test_duplicate_class_name(self) -> None:
        self.assert_invalid(
            "duplicate class name: 'Foo'",
            mode="class_diagram",
            classes=[{"name": "Foo"}, {"name": "Foo"}],
        )

    def test_bad_stereotype(self) -> None:
        self.assert_invalid(
            "stereotype of class 'A' must be one of",
            mode="class_diagram",
            classes=[{"name": "A", "stereotype": "widget"}],
        )

    def test_bad_color(self) -> None:
        self.assert_invalid(
            "color of class 'A' must be a color word",
            mode="class_diagram",
            classes=[{"name": "A", "color": "#red"}],
        )

    def test_fields_not_a_list(self) -> None:
        self.assert_invalid(
            "fields of class 'A' must be a list",
            mode="class_diagram",
            classes=[{"name": "A", "fields": "x"}],
        )

    def test_field_not_an_object(self) -> None:
        self.assert_invalid(
            "field at index 0 of class 'A'",
            mode="class_diagram",
            classes=[{"name": "A", "fields": ["x"]}],
        )

    def test_field_bad_name(self) -> None:
        self.assert_invalid(
            "must match [A-Za-z_][A-Za-z0-9_]*",
            mode="class_diagram",
            classes=[{"name": "A", "fields": [{"name": "2x"}]}],
        )

    def test_duplicate_field_name(self) -> None:
        self.assert_invalid(
            "duplicate field name 'x' in class 'A'",
            mode="class_diagram",
            classes=[{"name": "A",
                      "fields": [{"name": "x"}, {"name": "x"}]}],
        )

    def test_bad_field_visibility(self) -> None:
        self.assert_invalid(
            "visibility of field 'x' of class 'A' must be one of",
            mode="class_diagram",
            classes=[{"name": "A",
                      "fields": [{"name": "x", "visibility": "*"}]}],
        )

    def test_field_type_with_colon(self) -> None:
        self.assert_invalid(
            "must not contain ':'",
            mode="class_diagram",
            classes=[{"name": "A",
                      "fields": [{"name": "x", "type": "a:b"}]}],
        )

    def test_methods_not_a_list(self) -> None:
        self.assert_invalid(
            "methods of class 'A' must be a list",
            mode="class_diagram",
            classes=[{"name": "A", "methods": "go"}],
        )

    def test_method_missing_name(self) -> None:
        self.assert_invalid(
            "name of method at index 0 of class 'A'",
            mode="class_diagram",
            classes=[{"name": "A", "methods": [{"params": []}]}],
        )

    def test_params_not_a_list(self) -> None:
        self.assert_invalid(
            "params of method 'go' of class 'A' must be a list",
            mode="class_diagram",
            classes=[{"name": "A",
                      "methods": [{"name": "go", "params": "x"}]}],
        )

    def test_param_not_an_object(self) -> None:
        self.assert_invalid(
            "param at index 0 of method 'go' of class 'A'",
            mode="class_diagram",
            classes=[{"name": "A",
                      "methods": [{"name": "go", "params": ["x"]}]}],
        )

    def test_duplicate_method_signature(self) -> None:
        self.assert_invalid(
            "duplicate method signature 'go' with 1 parameter(s) in class 'A'",
            mode="class_diagram",
            classes=[{
                "name": "A",
                "methods": [
                    {"name": "go", "params": [{"name": "x"}]},
                    {"name": "go", "params": [{"name": "y"}]},
                ],
            }],
        )

    def test_same_method_name_different_arity_allowed(self) -> None:
        result = self.tool.execute(
            mode="class_diagram",
            classes=[{
                "name": "A",
                "methods": [
                    {"name": "go", "params": [{"name": "x"}]},
                    {"name": "go"},
                ],
            }],
        )
        self.assertIn("+go(x)", result["result"])
        self.assertIn("+go()", result["result"])

    def test_bad_return_type(self) -> None:
        self.assert_invalid(
            "return type of method 'go' of class 'A'",
            mode="class_diagram",
            classes=[{"name": "A",
                      "methods": [{"name": "go", "return": "in{}t"}]}],
        )

    # --- class_diagram: relations ---------------------------------- #

    def test_relation_not_an_object(self) -> None:
        self.assert_invalid(
            "relation at index 0 must be an object",
            mode="class_diagram",
            classes=[{"name": "A"}], relations=["A -- A"],
        )

    def test_relation_missing_endpoint(self) -> None:
        self.assert_invalid(
            "relation at index 0: 'to' must be a declared class name",
            mode="class_diagram",
            classes=[{"name": "A"}], relations=[{"from": "A"}],
        )

    def test_relation_unknown_endpoints_listed_together(self) -> None:
        self.assert_invalid(
            "relation endpoints reference undeclared class names: "
            "'X', 'Y'",
            mode="class_diagram",
            classes=[{"name": "A"}],
            relations=[{"from": "X", "to": "Y"}],
        )

    def test_relation_bad_kind(self) -> None:
        self.assert_invalid(
            "kind of relation at index 0 must be one of",
            mode="class_diagram",
            classes=[{"name": "A"}, {"name": "B"}],
            relations=[{"from": "A", "to": "B", "kind": "nests"}],
        )

    def test_relation_bad_label(self) -> None:
        self.assert_invalid(
            "label of relation at index 0 must be a non-empty string",
            mode="class_diagram",
            classes=[{"name": "A"}, {"name": "B"}],
            relations=[{"from": "A", "to": "B", "label": 3}],
        )

    def test_class_note_not_an_object(self) -> None:
        self.assert_invalid(
            "note at index 0 must be an object",
            mode="class_diagram", classes=[{"name": "A"}], notes=["x"],
        )

    def test_class_note_unknown_target(self) -> None:
        self.assert_invalid(
            "note at index 0 references undeclared class name: 'Ghost'",
            mode="class_diagram", classes=[{"name": "A"}],
            notes=[{"on": "Ghost", "text": "boo"}],
        )

    def test_class_note_missing_text(self) -> None:
        self.assert_invalid(
            "text of note at index 0 must be a non-empty string",
            mode="class_diagram", classes=[{"name": "A"}],
            notes=[{"on": "A"}],
        )

    # --- sequence: participants ------------------------------------ #

    def test_participants_missing(self) -> None:
        self.assert_invalid(
            "participants must be a list", mode="sequence",
        )

    def test_participants_empty(self) -> None:
        self.assert_invalid(
            "participants must not be empty", mode="sequence",
            participants=[],
        )

    def test_participant_missing_name(self) -> None:
        self.assert_invalid(
            "name of participant at index 0",
            mode="sequence", participants=[{"type": "actor"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
        )

    def test_duplicate_participant_name(self) -> None:
        self.assert_invalid(
            "duplicate participant name: 'A'",
            mode="sequence", participants=[{"name": "A"}, {"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
        )

    def test_bad_participant_type(self) -> None:
        self.assert_invalid(
            "type of participant 'A' must be one of",
            mode="sequence",
            participants=[{"name": "A", "type": "robot"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
        )

    def test_bad_participant_alias(self) -> None:
        self.assert_invalid(
            "as of participant 'A'",
            mode="sequence",
            participants=[{"name": "A", "as": ""}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
        )

    # --- sequence: messages ----------------------------------------- #

    def test_messages_missing(self) -> None:
        self.assert_invalid(
            "messages must be a list", mode="sequence",
            participants=[{"name": "A"}],
        )

    def test_message_not_an_object(self) -> None:
        self.assert_invalid(
            "message at index 0 must be an object",
            mode="sequence",
            participants=[{"name": "A"}], messages=["A -> A"],
        )

    def test_message_missing_text(self) -> None:
        self.assert_invalid(
            "text of message at index 0 must be a non-empty string",
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[{"from": "A", "to": "B"}],
        )

    def test_message_bad_kind(self) -> None:
        self.assert_invalid(
            "kind of message at index 0 must be one of",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x", "kind": "wavy"}],
        )

    def test_message_unknown_endpoints(self) -> None:
        self.assert_invalid(
            "message endpoints reference undeclared participant names: "
            "'X', 'Y'",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "X", "to": "Y", "text": "x"}],
        )

    def test_activate_twice(self) -> None:
        self.assert_invalid(
            "message at index 1 activates 'B' which is already active",
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[
                {"from": "A", "to": "B", "text": "one", "activate": True},
                {"from": "A", "to": "B", "text": "two", "activate": True},
            ],
        )

    def test_deactivate_without_activate(self) -> None:
        self.assert_invalid(
            "message at index 0 deactivates 'A' which is not active",
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[{"from": "A", "to": "B", "text": "x",
                       "deactivate_after": True}],
        )

    def test_unmatched_activate_at_end(self) -> None:
        self.assert_invalid(
            "unmatched activate without a later deactivate_after for: 'B'",
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[
                {"from": "A", "to": "B", "text": "one", "activate": True},
                {"from": "A", "to": "B", "text": "two"},
            ],
        )

    def test_activate_flag_not_boolean(self) -> None:
        self.assert_invalid(
            "activate of message at index 0 must be a boolean",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x",
                       "activate": "yes"}],
        )

    # --- sequence: notes --------------------------------------------- #

    def test_sequence_note_missing_over(self) -> None:
        self.assert_invalid(
            "note at index 0: 'over' must be one participant name",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
            notes=[{"text": "floating"}],
        )

    def test_sequence_note_three_participants(self) -> None:
        self.assert_invalid(
            "note at index 0: 'over' must be one participant name",
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}, {"name": "C"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
            notes=[{"over": ["A", "B", "C"], "text": "crowded"}],
        )

    def test_sequence_note_unknown_participant(self) -> None:
        self.assert_invalid(
            "note at index 0 references undeclared participant name: 'Z'",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
            notes=[{"over": "Z", "text": "who"}],
        )

    # --- sequence: frames --------------------------------------------- #

    def test_frame_bad_kind(self) -> None:
        self.assert_invalid(
            "kind of frame at index 0 must be one of",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
            frames=[{"kind": "seq", "message_indexes": [0]}],
        )

    def test_frame_missing_indexes(self) -> None:
        self.assert_invalid(
            "message_indexes of frame at index 0 must be a non-empty list",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
            frames=[{"kind": "loop"}],
        )

    def test_frame_non_integer_index(self) -> None:
        self.assert_invalid(
            "must contain integers",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
            frames=[{"kind": "loop", "message_indexes": [True]}],
        )

    def test_frame_index_out_of_range(self) -> None:
        self.assert_invalid(
            "must be within 0..1",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[
                {"from": "A", "to": "A", "text": "x"},
                {"from": "A", "to": "A", "text": "y"},
            ],
            frames=[{"kind": "loop", "message_indexes": [2]}],
        )

    def test_frame_indexes_not_ascending(self) -> None:
        self.assert_invalid(
            "must be ascending",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[
                {"from": "A", "to": "A", "text": "x"},
                {"from": "A", "to": "A", "text": "y"},
            ],
            frames=[{"kind": "loop", "message_indexes": [1, 0]}],
        )

    def test_frame_indexes_not_contiguous(self) -> None:
        self.assert_invalid(
            "must form a contiguous run",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[
                {"from": "A", "to": "A", "text": "x"},
                {"from": "A", "to": "A", "text": "y"},
                {"from": "A", "to": "A", "text": "z"},
            ],
            frames=[{"kind": "loop", "message_indexes": [0, 2]}],
        )

    def test_frames_overlapping(self) -> None:
        self.assert_invalid(
            "overlaps or follows out of order",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[
                {"from": "A", "to": "A", "text": "x"},
                {"from": "A", "to": "A", "text": "y"},
            ],
            frames=[
                {"kind": "loop", "message_indexes": [0, 1]},
                {"kind": "opt", "message_indexes": [1]},
            ],
        )

    def test_frames_out_of_order(self) -> None:
        self.assert_invalid(
            "overlaps or follows out of order",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[
                {"from": "A", "to": "A", "text": "x"},
                {"from": "A", "to": "A", "text": "y"},
            ],
            frames=[
                {"kind": "loop", "message_indexes": [1]},
                {"kind": "opt", "message_indexes": [0]},
            ],
        )

    def test_frame_bad_label(self) -> None:
        self.assert_invalid(
            "label of frame at index 0 must be a non-empty string",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
            frames=[{"kind": "loop", "label": "", "message_indexes": [0]}],
        )

    def test_autonumber_not_boolean(self) -> None:
        self.assert_invalid(
            "autonumber must be a boolean",
            mode="sequence",
            participants=[{"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
            autonumber="on",
        )

    # --- validate: source ---------------------------------------------- #

    def test_validate_source_missing(self) -> None:
        self.assert_invalid(
            "source must be a non-empty string", mode="validate",
        )

    def test_validate_source_not_string(self) -> None:
        self.assert_invalid(
            "source must be a non-empty string",
            mode="validate", source=123,
        )

    def test_validate_source_too_long(self) -> None:
        self.assert_invalid(
            "exceeds the 100000-character limit",
            mode="validate", source="x" * 100_001,
        )


class PlantumlToolSanitizationPropertyTest(unittest.TestCase):
    """Seeded property checks over many hostile name sets."""

    class _Lcg:
        def __init__(self, seed: int) -> None:
            self.state = seed

        def randint(self, low: int, high: int) -> int:
            self.state = (
                self.state * 6364136223846793005
                + 1442695040888963407
            ) % (1 << 64)
            return low + (self.state >> 33) % (high - low + 1)

        def choice(self, items: list) -> str:
            return items[self.randint(0, len(items) - 1)]

    def setUp(self) -> None:
        self.tool = PlantumlTool()
        self.id_re = re.compile(r"^[A-Za-z0-9_]+$")

    def _random_names(self, rng: "_Lcg") -> list[str]:
        alphabet = [*"abZ_09 -.!@#$%^&*()+=[]<>?/\\|~`;,",
                    "用户", "Интерфейс", "é", "日本語", "Δ", "note", "end",
                    "as", "activate", "participant", "class", "loop"]
        names: list[str] = []
        seen: set[str] = set()
        while len(names) < rng.randint(1, 8):
            name = "".join(
                rng.choice(alphabet) for _ in range(rng.randint(1, 12))
            )
            if name and name not in seen and '"' not in name:
                seen.add(name)
                names.append(name)
        return names

    def test_200_seeded_name_sets_deterministic_and_unique(self) -> None:
        rng = self._Lcg(20261021)
        for trial in range(200):
            names = self._random_names(rng)
            with self.subTest(trial=trial, names=names):
                classes = [{"name": name} for name in names]
                relations = [{"from": names[0], "to": names[-1]}]
                first_class = self.tool.execute(
                    mode="class_diagram", classes=classes,
                    relations=relations,
                )
                second_class = self.tool.execute(
                    mode="class_diagram", classes=classes,
                    relations=relations,
                )
                first_seq = self.tool.execute(
                    mode="sequence",
                    participants=classes,
                    messages=[{
                        "from": names[0], "to": names[-1], "text": "m",
                    }],
                )
                second_seq = self.tool.execute(
                    mode="sequence",
                    participants=classes,
                    messages=[{
                        "from": names[0], "to": names[-1], "text": "m",
                    }],
                )
                self.assertEqual(first_class, second_class)
                self.assertEqual(first_seq, second_seq)
                for result in (first_class, first_seq):
                    mapping = result.get("id_mapping", {})
                    emitted = [mapping.get(n, n) for n in names]
                    self.assertEqual(len(set(emitted)), len(emitted))
                    for emitted_id in emitted:
                        self.assertTrue(self.id_re.match(emitted_id))
                mapping = first_class.get("id_mapping", {})
                relation_line = first_class["result"].split("\n")[-2]
                endpoints = relation_line.split(" -- ")
                self.assertEqual(
                    endpoints,
                    [mapping.get(names[0], names[0]),
                     mapping.get(names[-1], names[-1])],
                )


class PlantumlToolImportTest(unittest.TestCase):
    """The tool is exported from the common_tool package."""

    def test_package_export(self) -> None:
        from agentuniverse.agent.action.tool.common_tool import (
            PlantumlTool as Exported,
        )

        self.assertIs(Exported, DirectPlantumlTool)
        self.assertEqual(DirectPlantumlTool().name, "plantuml_tool")


if __name__ == "__main__":
    unittest.main()

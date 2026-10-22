# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_checklist_completeness_analyzer.py

import unittest
from pathlib import Path

import yaml

from agentuniverse.agent.action.knowledge.doc_processor.checklist_completeness_analyzer import \
    ChecklistCompletenessAnalyzer
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Realistic ops runbook mixing every accepted form plus every rejected
# look-alike. Hand counts over the ACCEPTED items only:
#   checked (6):  Migrate database schema; Dry-run on staging (nested
#                  indent); publish API docs ('*' marker, upper X);
#                  merge release branch (ordered '1.'); update landing
#                  copy (bare line-start checkbox); ship it
#   unchecked (6): Purge old sessions; Schedule production window
#                  (nested indent); rotate secrets ('+' marker); tag the
#                  build (ordered '2.'); fix dropdown a11y (bare); the
#                  empty-label item '- [ ]'
# total=12, checked=6, unchecked=6, ratio=0.5, empty_labels=1,
# missing_items = the 5 non-empty unchecked labels in document order,
# missing_truncated=False.
# Rejected look-alikes: the escaped '\[x]'; both items inside the fenced
# block; '[o]', '[maybe]', '[]'; the mid-sentence '[x]'.
RUNBOOK = """# Release runbook

## Backend
- [x] Migrate database schema
- [ ] Purge old sessions
  - [x] Dry-run on staging
  - [ ] Schedule production window
* [X] publish API docs
+ [ ] rotate secrets
1. [x] merge release branch
2. [ ] tag the build

## Frontend
[x] update landing copy
[ ] fix dropdown a11y
- [ ]
- [x] ship it

## Notes
Escaped literal: \\[x] not a task
Ops log (code block, must not count):
```
- [x] restart cache cluster
- [ ] escalate ticket 4711
```
Plain brackets: [o] optional, [maybe] someday, [] neither.
The box [x] mid-sentence is prose, not a task.
"""

EXPECTED_MISSING = [
    "Purge old sessions",
    "Schedule production window",
    "rotate secrets",
    "tag the build",
    "fix dropdown a11y",
]

# All-done list: 3/3 checked, ratio 1.0, nothing missing.
ALL_DONE = "- [x] a\n- [X] b\n* [x] c\n"

# All-open list: 2/2 unchecked, ratio 0.0, both labels missing.
ALL_OPEN = "- [ ] write tests\n- [ ] review docs\n"

# Third-done: 1/3 -> ratio 0.3333 (4-decimal ground truth).
THIRD_DONE = "- [x] one\n- [ ] two\n- [ ] three\n"

# No checkboxes at all: total=0, ratio None, note stamped.
PROSE = "Just paragraphs. Nothing to tick. [Not a checkbox either.]\n"

# Unclosed fence: everything after the opener is code and ignored, so
# only the item before the fence counts (total=1, checked=1).
UNCLOSED_FENCE = "- [x] counted\n```python\n- [ ] inside unclosed fence\n"

# Tab-indented nested item and trailing whitespace in the label:
# total=2, unchecked=2, labels stripped of trailing spaces/tabs.
TAB_INDENT = "- [ ] outer   \n\t- [ ] inner\t\n"

# CJK labels: total=2, checked=1, missing ['检查权限'].
CJK_LIST = "- [x] 备份数据\n- [ ] 检查权限\n"

_YAML_PATH = Path(__file__).resolve().parents[7] / \
    "agentuniverse/agent/action/knowledge/doc_processor/checklist_completeness_analyzer.yaml"


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestChecklistCompletenessAnalyzer(unittest.TestCase):
    """Comprehensive test suite for ChecklistCompletenessAnalyzer."""

    def setUp(self):
        self.analyzer = ChecklistCompletenessAnalyzer()
        self.query = Query(query_str="checklists")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _report(self, text: str, analyzer=None) -> dict:
        """Run the analyzer over one document and return its report."""
        doc = _doc(text)
        out = (analyzer or self.analyzer)._process_docs([doc], self.query)
        self.assertEqual(len(out), 1)
        return out[0].metadata["checklist"]

    # ========== Ground-truth analysis tests ==========

    def test_runbook_ground_truth(self):
        """The mixed runbook yields the hand-counted 12-item analysis."""
        report = self._report(RUNBOOK)
        self.assertEqual(report["total"], 12)
        self.assertEqual(report["checked"], 6)
        self.assertEqual(report["unchecked"], 6)
        self.assertEqual(report["ratio"], 0.5)
        self.assertEqual(report["empty_labels"], 1)
        self.assertEqual(report["missing_items"], EXPECTED_MISSING)
        self.assertFalse(report["missing_truncated"])

    def test_all_done(self):
        """Fully checked list: ratio 1.0, no missing items."""
        report = self._report(ALL_DONE)
        self.assertEqual((report["total"], report["checked"]), (3, 3))
        self.assertEqual(report["ratio"], 1.0)
        self.assertEqual(report["missing_items"], [])
        self.assertFalse(report["missing_truncated"])

    def test_all_open(self):
        """Fully open list: ratio 0.0, both labels missing."""
        report = self._report(ALL_OPEN)
        self.assertEqual((report["total"], report["checked"]), (2, 0))
        self.assertEqual(report["ratio"], 0.0)
        self.assertEqual(report["missing_items"],
                         ["write tests", "review docs"])

    def test_third_done_rounding(self):
        """1/3 completion rounds to the 4-decimal ground truth 0.3333."""
        report = self._report(THIRD_DONE)
        self.assertEqual(report["ratio"], 0.3333)

    def test_no_checkboxes(self):
        """Prose without checkboxes: zero counts, ratio None, note set."""
        doc = _doc(PROSE)
        out = self.analyzer._process_docs([doc], self.query)
        report = out[0].metadata["checklist"]
        self.assertEqual(report["total"], 0)
        self.assertIsNone(report["ratio"])
        self.assertEqual(report["missing_items"], [])
        self.assertEqual(out[0].metadata["checklist_note"],
                         "no checkboxes found")

    def test_blank_text(self):
        """Blank text behaves like prose: zero counts, no crash."""
        report = self._report("")
        self.assertEqual(report["total"], 0)
        self.assertIsNone(report["ratio"])

    def test_none_text(self):
        """The analyzer's None guard: None text is analyzed as blank."""
        report = self.analyzer._analyze(None)
        self.assertEqual(report["total"], 0)
        self.assertIsNone(report["ratio"])

    def test_unclosed_fence_ignores_rest(self):
        """After an unclosed fence every later line counts as code."""
        report = self._report(UNCLOSED_FENCE)
        self.assertEqual(report["total"], 1)
        self.assertEqual(report["checked"], 1)

    def test_tilde_fence_ignored(self):
        """Tilde fences guard their content exactly like backticks."""
        text = "- [ ] counted\n~~~\n- [x] ignored\n~~~\n- [x] counted too\n"
        report = self._report(text)
        self.assertEqual((report["total"], report["checked"]), (2, 1))

    def test_tab_indent_and_label_stripping(self):
        """Tab-indented items count; labels lose trailing whitespace."""
        report = self._report(TAB_INDENT)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["missing_items"], ["outer", "inner"])

    def test_cjk_labels(self):
        """CJK labels are extracted verbatim into missing_items."""
        report = self._report(CJK_LIST)
        self.assertEqual(report["missing_items"], ["检查权限"])

    def test_empty_input_doc_list(self):
        """An empty document batch passes through as an empty list."""
        self.assertEqual(self.analyzer._process_docs([], self.query), [])

    # ========== Metadata stamping tests ==========

    def test_metadata_shared_mapping_not_mutated(self):
        """A metadata mapping shared between documents is copied before
        the stamp, so the sibling never observes the new key."""
        shared = {"source": "wiki"}
        first, second = _doc(ALL_DONE, **shared), _doc(ALL_DONE, **shared)
        first.metadata = shared
        second.metadata = shared
        self.analyzer._process_docs([first], self.query)
        self.assertIsNot(first.metadata, second.metadata)
        self.assertNotIn("checklist", second.metadata)
        self.assertIn("checklist", first.metadata)
        self.assertEqual(first.metadata["source"], "wiki")

    def test_custom_and_disabled_keys(self):
        """Custom metadata keys are honoured; '' disables the stamps."""
        configer = self._create_configer({
            'name': 'cca', 'description': 'd',
            'checklist_key': 'tasks', 'note_key': 'tasks_note',
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        doc = _doc(ALL_DONE)
        analyzer._process_docs([doc], self.query)
        self.assertIn("tasks", doc.metadata)
        self.assertNotIn("checklist", doc.metadata)

        configer = self._create_configer({
            'name': 'cca', 'description': 'd',
            'checklist_key': '', 'note_key': '',
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        doc = _doc(PROSE)
        analyzer._process_docs([doc], self.query)
        self.assertIsNone(doc.metadata)

    def test_existing_metadata_preserved(self):
        """Pre-existing metadata entries survive the stamp."""
        doc = _doc(ALL_DONE, lang="en")
        self.analyzer._process_docs([doc], self.query)
        self.assertEqual(doc.metadata["lang"], "en")
        self.assertIn("checklist", doc.metadata)

    def test_determinism(self):
        """Repeated runs over the same batch give identical metadata."""
        def run():
            doc = _doc(RUNBOOK)
            self.analyzer._process_docs([doc], self.query)
            return doc.metadata["checklist"]
        self.assertEqual(run(), run())

    # ========== missing_items cap tests ==========

    def test_cap_truncates_missing_items(self):
        """max_items_reported caps the stored labels and sets the flag."""
        configer = self._create_configer({
            'name': 'cca', 'description': 'd', 'max_items_reported': 2,
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        report = self._report(RUNBOOK, analyzer)
        self.assertEqual(report["missing_items"], EXPECTED_MISSING[:2])
        self.assertTrue(report["missing_truncated"])
        self.assertEqual(report["unchecked"], 6)

    def test_cap_zero_keeps_none(self):
        """max_items_reported=0 stores no labels but still truncates."""
        configer = self._create_configer({
            'name': 'cca', 'description': 'd', 'max_items_reported': 0,
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        report = self._report(RUNBOOK, analyzer)
        self.assertEqual(report["missing_items"], [])
        self.assertTrue(report["missing_truncated"])

    def test_cap_equal_to_candidates_not_truncated(self):
        """A cap at least as large as the candidate count never flags."""
        configer = self._create_configer({
            'name': 'cca', 'description': 'd', 'max_items_reported': 5,
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        report = self._report(RUNBOOK, analyzer)
        self.assertEqual(len(report["missing_items"]), 5)
        self.assertFalse(report["missing_truncated"])

    # ========== Filter-mode tests ==========

    def test_filter_min_ratio(self):
        """min_ratio drops incomplete docs; None-ratio docs always kept."""
        configer = self._create_configer({
            'name': 'cca', 'description': 'd', 'min_ratio': 0.6,
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        docs = [_doc(RUNBOOK), _doc(ALL_DONE), _doc(PROSE)]
        out = analyzer._process_docs(docs, self.query)
        self.assertEqual([d.text for d in out], [ALL_DONE, PROSE])

    def test_filter_max_ratio(self):
        """max_ratio drops over-complete docs; None-ratio docs kept."""
        configer = self._create_configer({
            'name': 'cca', 'description': 'd', 'max_ratio': 0.4,
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        docs = [_doc(RUNBOOK), _doc(ALL_OPEN), _doc(PROSE), _doc(ALL_DONE)]
        out = analyzer._process_docs(docs, self.query)
        self.assertEqual([d.text for d in out], [ALL_OPEN, PROSE])

    def test_filter_bounds_inclusive(self):
        """Bounds match with equality, they do not exclude the value."""
        configer = self._create_configer({
            'name': 'cca', 'description': 'd',
            'min_ratio': 0.5, 'max_ratio': 0.5,
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        out = analyzer._process_docs([_doc(RUNBOOK)], self.query)
        self.assertEqual(len(out), 1)

    def test_filter_order_preserved(self):
        """Filter mode keeps the original batch order."""
        configer = self._create_configer({
            'name': 'cca', 'description': 'd', 'min_ratio': 0.0,
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        docs = [_doc(ALL_OPEN), _doc(RUNBOOK), _doc(ALL_DONE)]
        out = analyzer._process_docs(docs, self.query)
        self.assertEqual([d.text for d in out],
                         [ALL_OPEN, RUNBOOK, ALL_DONE])

    def test_no_bounds_returns_all(self):
        """Default configuration is stamp-only: nothing is dropped."""
        docs = [_doc(RUNBOOK), _doc(ALL_DONE), _doc(PROSE), _doc(ALL_OPEN)]
        out = self.analyzer._process_docs(docs, self.query)
        self.assertEqual(len(out), 4)

    # ========== Initialization and validation tests ==========

    def test_default_configuration(self):
        """Defaults: no ratio bounds (stamp only), standard keys, cap 25."""
        analyzer = ChecklistCompletenessAnalyzer()
        self.assertIsNone(analyzer.min_ratio)
        self.assertIsNone(analyzer.max_ratio)
        self.assertEqual(analyzer.checklist_key, "checklist")
        self.assertEqual(analyzer.note_key, "checklist_note")
        self.assertEqual(analyzer.max_items_reported, 25)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'checklist_completeness_analyzer',
            'description': 'checklist analyzer',
            'min_ratio': 0.25,
            'max_ratio': 1,
            'checklist_key': 'tasks',
            'note_key': 'tasks_note',
            'max_items_reported': 3,
        })
        analyzer = ChecklistCompletenessAnalyzer()
        analyzer._initialize_by_component_configer(configer)
        self.assertEqual(analyzer.min_ratio, 0.25)
        self.assertEqual(analyzer.max_ratio, 1.0)
        self.assertEqual(analyzer.checklist_key, "tasks")
        self.assertEqual(analyzer.note_key, "tasks_note")
        self.assertEqual(analyzer.max_items_reported, 3)
        self.assertEqual(analyzer.name, "checklist_completeness_analyzer")

    def test_invalid_configuration_raises(self):
        """The full error matrix fails eagerly at load time."""
        base = {
            'name': 'cca', 'description': 'd',
            'min_ratio': None, 'max_ratio': None,
            'checklist_key': 'checklist', 'note_key': 'checklist_note',
            'max_items_reported': 25,
        }
        cases = [
            {'min_ratio': 'high'},
            {'min_ratio': True},
            {'min_ratio': -0.1},
            {'min_ratio': 1.5},
            {'max_ratio': '0.5'},
            {'max_ratio': False},
            {'max_ratio': -1},
            {'max_ratio': 2},
            {'min_ratio': 0.8, 'max_ratio': 0.2},
            {'checklist_key': 7},
            {'note_key': ['a']},
            {'max_items_reported': -1},
            {'max_items_reported': True},
            {'max_items_reported': 2.5},
            {'max_items_reported': 'many'},
        ]
        for override in cases:
            with self.subTest(override=override):
                configer = self._create_configer({**base, **override})
                analyzer = ChecklistCompletenessAnalyzer()
                with self.assertRaises(ValueError):
                    analyzer._initialize_by_component_configer(configer)

    # ========== Shipped YAML sanity ==========

    def test_shipped_yaml_matches_component(self):
        """The shipped YAML registers this module and class."""
        with open(_YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["metadata"]["type"], "DOC_PROCESSOR")
        self.assertEqual(
            data["metadata"]["module"],
            "agentuniverse.agent.action.knowledge.doc_processor."
            "checklist_completeness_analyzer")
        self.assertEqual(data["metadata"]["class"],
                         "ChecklistCompletenessAnalyzer")
        self.assertEqual(data["name"], "checklist_completeness_analyzer")
        self.assertIsNone(data["min_ratio"])
        self.assertIsNone(data["max_ratio"])
        self.assertEqual(data["max_items_reported"], 25)


if __name__ == "__main__":
    unittest.main()

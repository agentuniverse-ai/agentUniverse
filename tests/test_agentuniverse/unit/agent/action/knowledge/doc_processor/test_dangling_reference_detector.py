# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_dangling_reference_detector.py

import unittest

import yaml

from agentuniverse.agent.action.knowledge.doc_processor.dangling_reference_detector import DanglingReferenceDetector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# An English paper-like document exercising every anchor flavour (colon
# caption, "Fig. N." caption, bold markdown caption, table caption,
# keyword equation caption) plus healthy and dangling references.
EN_DOC = "\n".join([
    "Figure 1: System architecture.",
    "Fig. 2. Throughput results.",
    "**Figure 3.** Error breakdown.",
    "Table 1: Datasets.",
    "Equation (1): loss definition.",
    "The pipeline is shown in Figure 1 and Figure 4.",
    "As shown in Fig. 2, throughput improves.",
    "See Figures 1-3 for details.",
    "Table 1 lists the corpora; Table 2 lists baselines.",
    "By Eq. (1) the loss decreases; by Eq. (2) it grows.",
])

# A Chinese document with the same structure: 图/表/式 anchors and
# 如图N所示 / 见表N / 公式(N) references.
ZH_DOC = "\n".join([
    "图1：系统架构。",
    "表1：数据集。",
    "式（1）：损失定义。",
    "如图1所示，系统包含三个模块。",
    "见表2了解基线方法。",
    "由公式(2)可知损失下降。",
])


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestDanglingReferenceDetector(unittest.TestCase):
    """Comprehensive test suite for DanglingReferenceDetector."""

    def setUp(self):
        self.detector = DanglingReferenceDetector()
        self.query = Query(query_str="broken documents")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _run(self, text, detector=None, **metadata):
        """Process a single document and return (document, metadata)."""
        doc = _doc(text, **metadata)
        result = (detector or self.detector).process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        return doc, doc.metadata

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 30, ±30 context chars, range guard 50, all lists
        on, default metadata keys."""
        d = DanglingReferenceDetector()
        self.assertEqual(d.max_report, 30)
        self.assertEqual(d.context_chars, 30)
        self.assertEqual(d.max_range_span, 50)
        self.assertTrue(d.include_unreferenced)
        self.assertEqual(d.dangling_key, "dangling_references")
        self.assertEqual(d.unreferenced_key, "unreferenced_anchors")
        self.assertEqual(d.integrity_key, "reference_integrity")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'dangling_reference_detector',
            'description': 'dangling reference detector',
            'max_report': 5,
            'context_chars': 12,
            'max_range_span': 8,
            'include_unreferenced': False,
            'dangling_key': 'broken_refs',
            'unreferenced_key': 'orphan_anchors',
            'integrity_key': 'verdict',
        })
        d = DanglingReferenceDetector()
        d._initialize_by_component_configer(configer)
        self.assertEqual(d.max_report, 5)
        self.assertEqual(d.context_chars, 12)
        self.assertEqual(d.max_range_span, 8)
        self.assertFalse(d.include_unreferenced)
        self.assertEqual(d.dangling_key, "broken_refs")
        self.assertEqual(d.unreferenced_key, "orphan_anchors")
        self.assertEqual(d.integrity_key, "verdict")
        self.assertEqual(d.name, "dangling_reference_detector")

    def test_invalid_configuration_raises(self):
        """Out-of-range / mistyped knobs and non-string metadata keys all
        fail eagerly at load time."""
        base = {
            'name': 'd', 'description': 'x',
            'max_report': 30, 'context_chars': 30, 'max_range_span': 50,
            'include_unreferenced': True, 'dangling_key': 'a',
            'unreferenced_key': 'b', 'integrity_key': 'c',
        }
        for key, value in (
            ('max_report', -1),
            ('max_report', 2.5),
            ('max_report', True),
            ('context_chars', -1),
            ('context_chars', 'big'),
            ('context_chars', True),
            ('max_range_span', 0),
            ('max_range_span', 1.5),
            ('max_range_span', True),
            ('dangling_key', 7),
            ('unreferenced_key', ['x']),
            ('integrity_key', {}),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                DanglingReferenceDetector()._initialize_by_component_configer(
                    self._create_configer(config))

    def test_yaml_definition_file(self):
        """The shipped yaml declares the right component identity and
        default knob values."""
        import os
        path = os.path.join(os.path.dirname(__file__),
                            '..', '..', '..', '..', '..', '..', '..',
                            'agentuniverse', 'agent', 'action', 'knowledge',
                            'doc_processor',
                            'dangling_reference_detector.yaml')
        with open(os.path.abspath(path), 'r', encoding='utf-8') as fh:
            data = yaml.safe_load(fh)
        self.assertEqual(data['name'], 'dangling_reference_detector')
        self.assertEqual(data['metadata']['type'], 'DOC_PROCESSOR')
        self.assertEqual(data['metadata']['module'],
                         'agentuniverse.agent.action.knowledge.'
                         'doc_processor.dangling_reference_detector')
        self.assertEqual(data['metadata']['class'], 'DanglingReferenceDetector')
        self.assertEqual(data['max_report'], 30)
        self.assertEqual(data['context_chars'], 30)
        self.assertEqual(data['max_range_span'], 50)
        self.assertTrue(data['include_unreferenced'])

    # ========== English scanning ground truth ==========

    def test_english_anchors_and_references(self):
        """EN_DOC defines figures 1-3, table 1, equation 1; references hit
        all of them except figure 4 / table 2 / equation 2 dangle."""
        _, meta = self._run(EN_DOC)
        dangling = meta['dangling_references']
        self.assertEqual(meta['dangling_count'], 3)
        self.assertEqual(meta['reference_integrity'], 'dangling')
        self.assertEqual(
            sorted((e['kind'], e['id']) for e in dangling),
            [('equation', 2), ('figure', 4), ('table', 2)])
        self.assertEqual(meta['unreferenced_anchor_count'], 0)
        self.assertEqual(meta['unreferenced_anchors'], [])

        # Every dangling entry carries a span inside the text plus a
        # context window that actually contains the mention.
        for entry in dangling:
            start, end = entry['span']
            self.assertEqual(len(entry['span']), 2)
            self.assertGreaterEqual(start, 0)
            self.assertLess(end, len(EN_DOC))
            self.assertIn(EN_DOC[start:end].strip(' .;,'), entry['context'])

    def test_english_anchor_flavours(self):
        """Each anchor flavour alone (colon caption, Fig. N. caption, bold
        markdown caption, table caption, keyword equation caption) is
        recognized, and referencing it clears the report."""
        for caption, kind, token in (
            ("Figure 3: Overview.", 'figure', "Figure 3"),
            ("Fig. 3. Overview.", 'figure', "Fig. 3"),
            ("**Figure 3.** Overview.", 'figure', "Figure 3"),
            ("Table 3: Overview.", 'table', "Table 3"),
            ("Equation (3): Overview.", 'equation', "Equation (3)"),
        ):
            text = caption + "\nAs discussed for " + token + " above."
            _, meta = self._run(text)
            self.assertEqual(meta['dangling_count'], 0, msg=caption)
            self.assertEqual(meta['unreferenced_anchor_count'], 0, msg=caption)
            self.assertEqual(meta['reference_integrity'], 'ok', msg=caption)

    def test_sentence_final_period_stays_a_reference(self):
        """"This is depicted in Figure 3." — the trailing period is
        sentence punctuation, not caption punctuation."""
        _, meta = self._run("This is depicted in Figure 3.")
        self.assertEqual(meta['dangling_count'], 1)
        self.assertEqual(meta['dangling_references'][0]['kind'], 'figure')
        self.assertEqual(meta['dangling_references'][0]['id'], 3)
        self.assertEqual(meta['reference_integrity'], 'dangling')

    def test_line_initial_mention_without_caption_punct_is_reference(self):
        """"Figure 3 shows..." starts the line but is a subject mention,
        not a caption."""
        _, meta = self._run("Figure 3 shows the layers.")
        self.assertEqual(meta['dangling_count'], 1)
        self.assertEqual(meta['dangling_references'][0]['id'], 3)
        self.assertEqual(meta['unreferenced_anchor_count'], 0)

    def test_markdown_block_markers_precede_anchors(self):
        """List bullets, blockquotes, headings, ordered-list markers and
        bold markers all keep a caption in anchor position."""
        text = "\n".join([
            "- Figure 3: bullet caption",
            "> Figure 4: quote caption",
            "## Figure 5: heading caption",
            "1. Figure 6: ordered caption",
            "**Figure 7.** bold caption",
            "Refs: Figure 3, Figure 4, Figure 5, Figure 6 and Figure 7.",
        ])
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['unreferenced_anchor_count'], 0)
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_decimal_figure_number_is_not_a_caption_anchor(self):
        """"Figure 3.5" parses as a reference to figure 3, never as an
        anchor whose caption period belongs to a decimal."""
        _, meta = self._run("Figure 3.5 shows the pipeline.")
        self.assertEqual(meta['dangling_count'], 1)
        self.assertEqual(meta['dangling_references'][0]['id'], 3)
        self.assertEqual(meta['unreferenced_anchor_count'], 0)

    def test_caption_referencing_itself_is_sound(self):
        """Same-sentence repetition: line-initial "Figure 3:" is the
        anchor, the mid-sentence "Figure 3" is the reference — sound."""
        text = ("Figure 3: The architecture in detail. "
                "As Figure 3 shows, three layers exist.")
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['unreferenced_anchor_count'], 0)
        self.assertEqual(meta['reference_integrity'], 'ok')

    # ========== Chinese scanning ground truth ==========

    def test_chinese_anchors_and_references(self):
        """ZH_DOC anchors 图1/表1/式（1）; 如图1所示 resolves, 见表2 and
        公式(2) dangle."""
        _, meta = self._run(ZH_DOC)
        self.assertEqual(meta['dangling_count'], 2)
        self.assertEqual(meta['reference_integrity'], 'dangling')
        self.assertEqual(
            sorted((e['kind'], e['id']) for e in meta['dangling_references']),
            [('equation', 2), ('table', 2)])
        # 表1 and 式（1） are anchored but never referenced.
        self.assertEqual(meta['unreferenced_anchor_count'], 2)
        self.assertEqual(
            sorted((e['kind'], e['id'])
                   for e in meta['unreferenced_anchors']),
            [('equation', 1), ('table', 1)])

    def test_chinese_anchor_flavours(self):
        """图N：/表N： captions anchor; ASCII colon after 表N anchors too."""
        text = "\n".join([
            "图4：处理流程。",
            "表5: 结果汇总。",
            "如图4所示，共两步。",
            "见表5。",
        ])
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['unreferenced_anchor_count'], 0)
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_chinese_report_word_does_not_create_table(self):
        """"报表2" (report form) must not register a table-2 mention."""
        _, meta = self._run("本月报表2份已提交。")
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_chinese_bare_shi_reference_with_parens(self):
        """"式(5)" mid-sentence is an equation reference; "公式5" and
        "方程(7)" work as well."""
        _, meta = self._run("将式(5)代入公式5和方程(7)即可。")
        self.assertEqual(meta['dangling_count'], 3)
        self.assertEqual(
            sorted(e['id'] for e in meta['dangling_references']
                   if e['kind'] == 'equation'),
            [5, 5, 7])

    # ========== Equation-specific rules ==========

    def test_bare_equation_number_anchors_at_line_end(self):
        """A line-final "(7)" after closing punctuation anchors equation 7;
        the keyword reference to it then resolves."""
        text = "By Eq. (7) we proceed.\nz = f(w)  (7)"
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_bare_equation_number_needs_preceding_punctuation(self):
        """"(9)" right after a digit is part of the formula, not a number
        tag; "(5)" after a word is an inline citation, not an anchor."""
        _, meta = self._run("E = mc2  (9)\nwe substitute into (5) yields")
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['unreferenced_anchor_count'], 0)
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_bare_equation_number_inline_citation_stays_out(self):
        """Mid-sentence "(5)" followed by more text on the line is a
        citation and must not become an equation anchor."""
        _, meta = self._run("as shown previously. (5) Further work extends it.")
        self.assertEqual(meta['unreferenced_anchor_count'], 0)

    def test_equation_keyword_anchor_flavours(self):
        """"Eq. (5)." at line start anchors; keyword claim prevents the
        bare pass from double counting the "(5)"."""
        text = "Eq. (5). The update rule.\nEquation (5) applies."
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['unreferenced_anchor_count'], 0)

    # ========== Range expansion ==========

    def test_range_expansion_en_and_zh(self):
        """"Figures 3-5" / "Figs. 3-5" / "Eqs. (5)-(7)" / "图3至图5" expand
        to every covered id."""
        _, meta = self._run("See Figures 3-5 and Figs. 3-5 for details.")
        self.assertEqual(meta['dangling_count'], 6)
        self.assertEqual(sorted(e['id'] for e in meta['dangling_references']),
                         [3, 3, 4, 4, 5, 5])

        _, meta = self._run("Apply Eqs. (5)-(7) in order.")
        self.assertEqual(sorted(e['id'] for e in meta['dangling_references']),
                         [5, 6, 7])

        _, meta = self._run("图3至图5如前所述。")
        self.assertEqual(sorted(e['id'] for e in meta['dangling_references']),
                         [3, 4, 5])

    def test_range_against_partial_anchors(self):
        """Only the ids outside an anchored range dangle; the anchored id
        is referenced and not reported unreferenced."""
        text = "Figure 4: The only defined figure.\nSee Figures 3-5."
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 2)
        self.assertEqual(
            sorted(e['id'] for e in meta['dangling_references']), [3, 5])
        self.assertEqual(meta['unreferenced_anchor_count'], 0)

    def test_inverted_range_degrades_to_single_id(self):
        """"Figures 5-3" is not a real range; only figure 5 is referenced."""
        _, meta = self._run("Figures 5-3 are broken.")
        self.assertEqual(meta['dangling_count'], 1)
        self.assertEqual(meta['dangling_references'][0]['id'], 5)

    def test_range_expansion_clamped(self):
        """Ranges longer than max_range_span are clamped from the lower
        bound, by default and when configured."""
        _, meta = self._run("Figures 1-80 are listed.")
        self.assertEqual(meta['dangling_count'], 50)
        self.assertEqual(meta['dangling_references'][0]['id'], 1)
        # The list is capped at 30 while the count keeps the full 50.
        self.assertEqual(len(meta['dangling_references']), 30)
        self.assertEqual(meta['dangling_references'][-1]['id'], 30)

        detector = DanglingReferenceDetector()
        detector.max_range_span = 10
        _, meta = self._run("Figures 1-80 are listed.", detector=detector)
        self.assertEqual(meta['dangling_count'], 10)
        self.assertEqual(meta['dangling_references'][-1]['id'], 10)

    # ========== Dangling / unreferenced arithmetic ==========

    def test_unreferenced_anchors_are_informational(self):
        """Anchors nothing points at are listed with spans and never flip
        the verdict on their own."""
        text = "\n".join([
            "Figure 5: An orphan figure.",
            "Table 9: An orphan table.",
            "Equation 4: An orphan equation.",
            "See Figure 6 and Table 9 below.",
        ])
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 1)
        self.assertEqual(meta['dangling_references'][0]['id'], 6)
        self.assertEqual(meta['unreferenced_anchor_count'], 2)
        self.assertEqual(
            sorted((e['kind'], e['id'])
                   for e in meta['unreferenced_anchors']),
            [('equation', 4), ('figure', 5)])
        self.assertEqual(meta['reference_integrity'], 'dangling')

    def test_unreferenced_only_keeps_ok_verdict(self):
        """A document whose only finding is unreferenced anchors stays
        'ok' — the info-level contract."""
        text = "Figure 5: An orphan figure.\nTable 9: Another orphan."
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['unreferenced_anchor_count'], 2)
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_kind_namespaces_are_independent(self):
        """Figure 3 anchored does not define table 3 or equation 3."""
        text = "Figure 3: Overview.\nTable 3 and Eq. (3) follow."
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 2)
        self.assertEqual(
            sorted((e['kind'], e['id']) for e in meta['dangling_references']),
            [('equation', 3), ('table', 3)])
        # Figure 3 itself is anchored but never referenced.
        self.assertEqual(meta['unreferenced_anchor_count'], 1)
        self.assertEqual(meta['unreferenced_anchors'][0]['id'], 3)

    def test_repeated_dangling_reference_counted_per_occurrence(self):
        """Two mentions of the same undefined id are two findings."""
        _, meta = self._run("See Figure 9 here and Figure 9 there.")
        self.assertEqual(meta['dangling_count'], 2)
        self.assertEqual(meta['dangling_references'][0]['id'], 9)
        self.assertEqual(meta['dangling_references'][1]['id'], 9)

    # ========== Reporting behavior ==========

    def test_report_list_capped_but_count_full(self):
        """35 dangling mentions produce a 30-entry list and a full count."""
        text = "\n".join(f"see Figure {i}" for i in range(1, 36))
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 35)
        self.assertEqual(len(meta['dangling_references']), 30)
        self.assertEqual(meta['dangling_references'][0]['id'], 1)
        self.assertEqual(meta['dangling_references'][-1]['id'], 30)
        self.assertEqual(meta['reference_integrity'], 'dangling')

    def test_max_report_zero_disables_lists_not_counts(self):
        """max_report=0 drops both list keys while counts and the verdict
        survive."""
        detector = DanglingReferenceDetector()
        detector.max_report = 0
        _, meta = self._run("Figure 5: orphan.\nSee Figure 6.", detector)
        self.assertNotIn('dangling_references', meta)
        self.assertNotIn('unreferenced_anchors', meta)
        self.assertEqual(meta['dangling_count'], 1)
        self.assertEqual(meta['unreferenced_anchor_count'], 1)
        self.assertEqual(meta['reference_integrity'], 'dangling')

    def test_context_window_boundaries(self):
        """Context is exactly ±30 chars around the span, clamped at the
        document edges."""
        text = "x" * 40 + "see Figure 7" + "y" * 40
        _, meta = self._run(text)
        self.assertEqual(len(meta['dangling_references']), 1)
        entry = meta['dangling_references'][0]
        start, end = entry['span']
        self.assertEqual(text[start:end], "Figure 7")
        # 30 chars before the span reach back over "see ": 26 x's + "see ".
        self.assertEqual(entry['context'],
                         "x" * 26 + "see Figure 7" + "y" * 30)

        _, meta = self._run("see Fig. 2")
        entry = meta['dangling_references'][0]
        self.assertEqual(entry['context'], "see Fig. 2")

    def test_custom_context_chars(self):
        """context_chars shrinks or widens the window."""
        detector = DanglingReferenceDetector()
        detector.context_chars = 2
        _, meta = self._run("x" * 40 + "see Figure 7" + "y" * 40, detector)
        # ±2 chars around the span "Figure 7" itself.
        self.assertEqual(meta['dangling_references'][0]['context'],
                         "e Figure 7yy")

    def test_metadata_keys_configurable_and_disableable(self):
        """Custom key names are honored; '' disables the matching stamp
        while the fixed count keys always land."""
        configer = self._create_configer({
            'name': 'd', 'description': 'x',
            'dangling_key': 'broken', 'unreferenced_key': '',
            'integrity_key': 'verdict',
        })
        detector = DanglingReferenceDetector()
        detector._initialize_by_component_configer(configer)
        _, meta = self._run("Figure 5: orphan.\nSee Figure 6.", detector)
        self.assertIn('broken', meta)
        self.assertNotIn('dangling_references', meta)
        self.assertNotIn('unreferenced_anchors', meta)
        self.assertEqual(meta['verdict'], 'dangling')
        self.assertEqual(meta['dangling_count'], 1)
        self.assertEqual(meta['unreferenced_anchor_count'], 1)

        detector = DanglingReferenceDetector()
        detector.integrity_key = ''
        detector.dangling_key = ''
        _, meta = self._run("See Figure 6.", detector)
        self.assertNotIn('reference_integrity', meta)
        self.assertNotIn('dangling_references', meta)
        self.assertEqual(meta['dangling_count'], 1)

    def test_include_unreferenced_false_skips_list(self):
        """Turning the informational list off keeps its count."""
        detector = DanglingReferenceDetector()
        detector.include_unreferenced = False
        _, meta = self._run("Figure 5: orphan.", detector)
        self.assertNotIn('unreferenced_anchors', meta)
        self.assertEqual(meta['unreferenced_anchor_count'], 1)
        self.assertEqual(meta['reference_integrity'], 'ok')

    # ========== Pipeline behavior ==========

    def test_clean_document_all_matched(self):
        """A fully consistent bilingual document passes with 'ok'."""
        text = "\n".join([
            "Figure 1: Overview.",
            "We follow Figure 1 closely.",
            "Table 2: Data.",
            "Table 2 lists rows.",
            "Equation (3): Loss.",
            "Per Equation (3) we optimize.",
            "图4：流程。",
            "如图4所示。",
            "表5：结果。",
            "见表5。",
        ])
        _, meta = self._run(text)
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['dangling_references'], [])
        self.assertEqual(meta['unreferenced_anchor_count'], 0)
        self.assertEqual(meta['unreferenced_anchors'], [])
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_plain_text_passthrough(self):
        """No mentions at all: stamped with an empty, 'ok' report."""
        _, meta = self._run("Plain text without any numbered objects.")
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['unreferenced_anchor_count'], 0)
        self.assertEqual(meta['dangling_references'], [])
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_empty_text(self):
        """Empty text scans to an empty, 'ok' report."""
        _, meta = self._run("")
        self.assertEqual(meta['dangling_count'], 0)
        self.assertEqual(meta['reference_integrity'], 'ok')

    def test_empty_batch(self):
        """An empty batch returns an empty list."""
        self.assertEqual(self.detector.process_docs([], self.query), [])

    def test_multi_document_batch_independent(self):
        """Each document is analyzed and stamped independently; order is
        preserved."""
        docs = [
            _doc("See Figure 9 now."),
            _doc("Figure 1: Fine.\nSee Figure 1."),
            _doc("nothing here"),
        ]
        result = self.detector.process_docs(docs, self.query)
        self.assertEqual([d.text.split('\n')[0] for d in result],
                         ["See Figure 9 now.", "Figure 1: Fine.",
                          "nothing here"])
        self.assertEqual(result[0].metadata['dangling_count'], 1)
        self.assertEqual(result[0].metadata['reference_integrity'],
                         'dangling')
        self.assertEqual(result[1].metadata['reference_integrity'], 'ok')
        self.assertEqual(result[1].metadata['unreferenced_anchor_count'], 0)
        self.assertEqual(result[2].metadata['dangling_count'], 0)

    def test_documents_not_corrupted(self):
        """Text and id stay untouched, existing metadata survives, and the
        original metadata mapping object is not mutated in place."""
        original_meta = {'src': 'paper', 'page': 3}
        doc = _doc("See Figure 9.", **original_meta)
        frozen = dict(original_meta)
        result = self.detector.process_docs([doc], self.query)
        out = result[0]
        self.assertEqual(out.text, "See Figure 9.")
        self.assertEqual(out.id, doc.id)
        self.assertEqual(out.metadata['src'], 'paper')
        self.assertEqual(out.metadata['page'], 3)
        # The mapping we handed in was copied, not edited.
        self.assertEqual(original_meta, frozen)
        self.assertNotIn('dangling_references', original_meta)

    def test_deterministic(self):
        """Two fresh detectors produce byte-identical metadata."""
        _, first = self._run(EN_DOC + "\n" + ZH_DOC)
        _, second = self._run(EN_DOC + "\n" + ZH_DOC)
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()

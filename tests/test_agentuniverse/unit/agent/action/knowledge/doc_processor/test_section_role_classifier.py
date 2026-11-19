# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_section_role_classifier.py

"""Offline unit tests for the SectionRoleClassifier doc processor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.section_role_classifier import \
    SectionRoleClassifier
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer


def make_doc(heading_lines):
    """Build a document from ``(heading, body_lines)`` pairs."""
    parts = []
    for heading, body in heading_lines:
        parts.append(heading)
        parts.extend(body)
    return Document(text="\n".join(parts) + "\n")


class SectionRoleClassifierTestBase(unittest.TestCase):
    """Shared helpers."""

    def setUp(self):
        self.classifier = SectionRoleClassifier()

    def classify(self, text):
        """Run the classifier on one document; return its metadata."""
        doc = Document(text=text)
        result = self.classifier.process_docs([doc])
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], doc)
        return doc.metadata

    def roles(self, text):
        meta = self.classify(text)
        return [(r['heading'], r['role'], r['confidence'])
                for r in meta['section_roles']]


class TestKeywordFamilies(SectionRoleClassifierTestBase):
    """Every keyword family, English and Chinese."""

    CASES = [
        # (heading, expected role)
        ('Introduction', 'intro'),
        ('INTRO', 'intro'),
        ('Background and Motivation', 'intro'),
        ('Related Work', 'intro'),
        ('引言', 'intro'),
        ('研究背景', 'intro'),
        ('Methods', 'method'),
        ('Our Methodology', 'method'),
        ('The Proposed Approach', 'method'),
        ('Experimental Setup', 'method'),
        ('Materials', 'method'),
        ('方法', 'method'),
        ('实验设置', 'method'),
        ('Results', 'results'),
        ('Evaluation', 'results'),
        ('Main Findings', 'results'),
        ('Performance Analysis', 'results'),
        ('实验结果', 'method'),  # '实验' (method) listed before '结果' (results)
        ('结果与讨论', 'results'),
        ('数据分析', 'results'),
        ('Discussion', 'discussion'),
        ('Limitations', 'discussion'),
        ('有效性威胁', 'discussion'),
        ('Conclusion', 'conclusion'),
        ('Conclusions and Future Work', 'conclusion'),
        ('Summary', 'conclusion'),
        ('结论', 'conclusion'),
        ('总结', 'conclusion'),
        ('Abstract', 'abstract'),
        ('摘要', 'abstract'),
        ('References', 'references'),
        ('Bibliography', 'references'),
        ('参考文献', 'references'),
        ('Acknowledgments', 'acknowledgments'),
        ('Acknowledgements', 'acknowledgments'),
    ]

    def test_keyword_roles(self):
        for heading, expected in self.CASES:
            with self.subTest(heading=heading):
                text = "# Preamble Section\n\nbody\n\n## %s\n\nbody\n" % heading
                got = self.roles(text)
                matches = [r for r in got if r[0] == heading]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0][1], expected)
                # Keyword matches always carry high confidence.
                self.assertEqual(matches[0][2], 'high')

    def test_chinese_heading_families(self):
        text = (
            "# 引言\n\n提出了问题。\n\n"
            "# 方法\n\n提出方法。\n\n"
            "# 结果\n\n给出结果。\n\n"
            "# 有效性威胁\n\n讨论局限。\n\n"
            "# 结论\n\n总结全文。\n"
        )
        self.assertEqual(
            [r[1] for r in self.roles(text)],
            ['intro', 'method', 'results', 'discussion', 'conclusion'],
        )


class TestPositionalFallback(SectionRoleClassifierTestBase):
    """Unmatched headings fall back to position with low confidence."""

    def test_first_and_last_unmatched(self):
        text = (
            "# The Beginning of Everything\n\nfirst body\n\n"
            "# Unmatched Middle Part\n\nmiddle body\n\n"
            "# Wrapping the Whole Thing Up\n\nlast body\n"
        )
        got = self.roles(text)
        self.assertEqual([r[1] for r in got],
                         ['intro', 'other', 'conclusion'])
        self.assertEqual([r[2] for r in got], ['low', 'low', 'low'])

    def test_fallback_confidence_distinct_from_keyword(self):
        text = "# Something\n\nbody\n\n# Conclusion\n\nbody\n"
        got = self.roles(text)
        # First is positional (low), second matched (high).
        self.assertEqual(got[0][2], 'low')
        self.assertEqual(got[1][2], 'high')

    def test_single_unmatched_section_is_intro(self):
        got = self.roles("# Only One Section\n\nbody\n")
        self.assertEqual(got[0][1], 'intro')

    def test_keyword_beats_position(self):
        # A keyword-matched first section keeps its keyword role.
        text = "# Method\n\nbody\n\n# Something Else Entirely\n\nbody\n"
        got = self.roles(text)
        self.assertEqual(got[0][1], 'method')
        self.assertEqual(got[0][2], 'high')
        self.assertEqual(got[1][1], 'conclusion')
        self.assertEqual(got[1][2], 'low')

    def test_positional_fallback_disabled(self):
        self.classifier.positional_fallback = False
        text = ("# The Beginning\n\nbody\n\n"
                "# Middle\n\nbody\n\n# The End\n\nbody\n")
        self.assertEqual([r[1] for r in self.roles(text)],
                         ['other', 'other', 'other'])


class TestMultiMatchPrecedence(SectionRoleClassifierTestBase):
    """A heading matching several families resolves to the first listed."""

    def test_results_and_discussion(self):
        got = self.roles("## Results and Discussion\n\nbody\n")
        self.assertEqual(got[0][1], 'results')

    def test_experimental_setup_and_results(self):
        got = self.roles("## Experimental Setup and Results\n\nbody\n")
        self.assertEqual(got[0][1], 'method')

    def test_introduction_and_conclusions(self):
        got = self.roles("## Introduction and Conclusions\n\nbody\n")
        self.assertEqual(got[0][1], 'intro')

    def test_precedence_order(self):
        # Family order: intro > method > results > discussion >
        # conclusion > abstract > references > acknowledgments.
        cases = [
            ('Background and Methods', 'intro'),
            ('Methods and Results', 'method'),
            ('Findings and Discussion', 'results'),
            ('Discussion and Conclusion', 'discussion'),
            ('Summary and References', 'conclusion'),
            ('Abstract and References', 'abstract'),
            ('References and Acknowledgments', 'references'),
        ]
        for heading, expected in cases:
            with self.subTest(heading=heading):
                got = self.roles("## %s\n\nbody\n" % heading)
                self.assertEqual(got[0][1], expected)

    def test_related_work_prefers_intro(self):
        # 'related work' is a member of both intro (primary) and
        # references (secondary); intro is listed first so it wins.
        got = self.roles("## Related Work\n\nbody\n")
        self.assertEqual(got[0][1], 'intro')


class TestSectionRecords(SectionRoleClassifierTestBase):
    """Record shape: heading, level, span, para_count."""

    def test_record_fields_and_levels(self):
        text = ("# Introduction\n\nbody\n\n"
                "## Methods\n\nbody\n\n"
                "### Deep Heading\n\nbody\n")
        meta = self.classify(text)
        records = meta['section_roles']
        self.assertEqual([r['heading'] for r in records],
                         ['Introduction', 'Methods', 'Deep Heading'])
        self.assertEqual([r['level'] for r in records], [1, 2, 3])

    def test_para_count(self):
        text = ("# Method\n\n"
                "First paragraph.\n\n"
                "Second paragraph line one.\n"
                "Second paragraph line two.\n\n"
                "Third paragraph.\n\n"
                "# Results\n\nOnly paragraph.\n")
        meta = self.classify(text)
        records = meta['section_roles']
        self.assertEqual(records[0]['para_count'], 3)
        self.assertEqual(records[1]['para_count'], 1)

    def test_para_count_zero_for_empty_section(self):
        meta = self.classify("# Method\n\n# Results\n\nbody\n")
        self.assertEqual(meta['section_roles'][0]['para_count'], 0)

    def test_span_offsets(self):
        text = "# Introduction\n\nintro body\n\n# Methods\n\nmethod body\n"
        meta = self.classify(text)
        records = meta['section_roles']
        for record in records:
            start, end = record['span']
            snippet = text[start:end]
            self.assertTrue(
                snippet.startswith('# ' + record['heading']),
                "span should start at the heading line")
        # Sections are contiguous and ordered.
        self.assertEqual(records[0]['span'][1], records[1]['span'][0])
        # The last section runs to the end of the text.
        self.assertEqual(records[-1]['span'][1], len(text))


class TestHasImradAndCounts(SectionRoleClassifierTestBase):
    """role_counts and has_imrad arithmetic."""

    def test_full_imrad_paper(self):
        text = ("# Abstract\n\nsummary\n\n"
                "# Introduction\n\nbody\n\n"
                "# Related Work\n\nbody\n\n"
                "# Methods\n\nbody\n\n"
                "# Results\n\nbody\n\n"
                "# Discussion\n\nbody\n\n"
                "# Conclusion\n\nbody\n\n"
                "# References\n\nbody\n\n"
                "# Acknowledgments\n\nbody\n")
        meta = self.classify(text)
        self.assertTrue(meta['has_imrad'])
        self.assertEqual(meta['role_counts'],
                         {'abstract': 1, 'intro': 2, 'method': 1,
                          'results': 1, 'discussion': 1, 'conclusion': 1,
                          'references': 1, 'acknowledgments': 1})

    def test_has_imrad_missing_one_core_role(self):
        # No results section: has_imrad must be False.
        text = ("# Introduction\n\nbody\n\n"
                "# Methods\n\nbody\n\n"
                "# Conclusion\n\nbody\n")
        meta = self.classify(text)
        self.assertFalse(meta['has_imrad'])
        self.assertEqual(meta['role_counts'],
                         {'intro': 1, 'method': 1, 'conclusion': 1})

    def test_non_core_roles_do_not_satisfy_imrad(self):
        # abstract/references/acknowledgments present but method missing.
        text = ("# Abstract\n\nbody\n\n"
                "# Introduction\n\nbody\n\n"
                "# Results\n\nbody\n\n"
                "# Conclusion\n\nbody\n\n"
                "# References\n\nbody\n\n"
                "# Acknowledgments\n\nbody\n")
        meta = self.classify(text)
        self.assertFalse(meta['has_imrad'])

    def test_positional_roles_count_toward_imrad(self):
        # Unmatched first/last sections fall back to intro/conclusion.
        text = ("# Beginning\n\nbody\n\n"
                "# Methods\n\nbody\n\n"
                "# Results\n\nbody\n\n"
                "# Ending\n\nbody\n")
        meta = self.classify(text)
        self.assertTrue(meta['has_imrad'])
        self.assertEqual(meta['role_counts']['intro'], 1)
        self.assertEqual(meta['role_counts']['conclusion'], 1)


class TestCapAndPassthrough(SectionRoleClassifierTestBase):
    """section_roles cap and the no-headings passthrough."""

    def test_cap_limits_listing_not_counts(self):
        # 35 sections: listing capped at 30 (default), counts cover all 35.
        lines = []
        for i in range(34):
            lines.append("# Part %d\n\nbody\n\n" % i)
        lines.append("# Conclusion\n\nbody\n")
        text = "".join(lines)
        meta = self.classify(text)
        self.assertEqual(len(meta['section_roles']), 30)
        self.assertEqual(meta['section_roles'][-1]['heading'], 'Part 29')
        self.assertEqual(meta['role_counts'],
                         {'intro': 1, 'other': 33, 'conclusion': 1})
        self.assertFalse(meta['has_imrad'])

    def test_configurable_cap(self):
        self.classifier.max_sections = 2
        text = "# Introduction\n\nb\n\n# Methods\n\nb\n\n# Results\n\nb\n"
        meta = self.classify(text)
        self.assertEqual(len(meta['section_roles']), 2)
        self.assertEqual(meta['role_counts'],
                         {'intro': 1, 'method': 1, 'results': 1})

    def test_no_headings_passthrough(self):
        text = "Just plain prose.\n\nNo headings anywhere.\n"
        doc = Document(text=text, metadata={'source': 'notes.txt'})
        result = self.classifier.process_docs([doc])
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, text)
        self.assertEqual(doc.metadata['source'], 'notes.txt')
        self.assertEqual(doc.metadata['section_roles'], [])
        self.assertEqual(doc.metadata['role_counts'], {})
        self.assertFalse(doc.metadata['has_imrad'])
        self.assertIn('No ATX headings', doc.metadata['section_roles_note'])

    def test_headings_inside_fences_are_ignored(self):
        text = ("# Introduction\n\n"
                "```python\n"
                "# not a heading, a comment\n"
                "def f():\n"
                "    pass\n"
                "```\n\n"
                "# Conclusion\n\nbody\n")
        got = self.roles(text)
        self.assertEqual([r[0] for r in got],
                         ['Introduction', 'Conclusion'])

    def test_tilde_fences_are_ignored(self):
        text = ("# Method\n\n~~~\n# fenced comment\n~~~\n\n# Results\n\nb\n")
        got = self.roles(text)
        self.assertEqual([r[0] for r in got], ['Method', 'Results'])

    def test_non_atx_lines_are_not_headings(self):
        text = ("# Introduction\n\n"
                "#nospace\n\n"
                "####### seven hashes\n\n"
                "## Closed Heading ##\n\nbody\n")
        got = self.roles(text)
        self.assertEqual([r[0] for r in got],
                         ['Introduction', 'Closed Heading'])

    def test_empty_and_multiple_docs(self):
        self.assertEqual(self.classifier.process_docs([]), [])
        docs = [Document(text="# Introduction\n\nb\n"),
                Document(text="# Methods\n\nb\n")]
        result = self.classifier.process_docs(docs)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].metadata['role_counts'], {'intro': 1})
        self.assertEqual(result[1].metadata['role_counts'], {'method': 1})


class TestConfigAndDeterminism(SectionRoleClassifierTestBase):
    """Configer initialization, validation and determinism."""

    def _make_configer(self, config):
        cfg = Configer()
        cfg.value = config
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        if not hasattr(configer, 'name'):
            configer.name = config.get('name', 'test_section_role_classifier')
        if not hasattr(configer, 'description'):
            configer.description = config.get(
                'description', 'Test classifier description')
        return configer

    def test_defaults(self):
        classifier = SectionRoleClassifier()
        self.assertEqual(classifier.max_sections, 30)
        self.assertTrue(classifier.positional_fallback)

    def test_configer_initialization(self):
        configer = self._make_configer({
            'name': 'section_role_classifier',
            'description': 'Test classifier',
            'max_sections': 5,
            'positional_fallback': False,
        })
        classifier = SectionRoleClassifier()
        classifier._initialize_by_component_configer(configer)
        self.assertEqual(classifier.max_sections, 5)
        self.assertFalse(classifier.positional_fallback)
        self.assertEqual(classifier.name, 'section_role_classifier')

    def test_config_validation_bad_max_sections(self):
        for bad in (0, -1, 'many', 2.5, True):
            configer = self._make_configer({
                'name': 'test', 'description': 'd',
                'max_sections': bad,
            })
            classifier = SectionRoleClassifier()
            with self.subTest(max_sections=bad), self.assertRaises(ValueError):
                classifier._initialize_by_component_configer(configer)

    def test_config_validation_bad_positional_fallback(self):
        configer = self._make_configer({
            'name': 'test', 'description': 'd',
            'positional_fallback': 'yes',
        })
        classifier = SectionRoleClassifier()
        with self.assertRaises(ValueError):
            classifier._initialize_by_component_configer(configer)

    def test_yaml_definition_is_valid(self):
        import os
        import yaml
        import agentuniverse
        yaml_path = os.path.join(
            os.path.dirname(agentuniverse.__file__),
            'agent', 'action', 'knowledge', 'doc_processor',
            'section_role_classifier.yaml')
        self.assertTrue(os.path.isfile(yaml_path), yaml_path)
        with open(yaml_path, 'r', encoding='utf-8') as fh:
            data = yaml.safe_load(fh)
        self.assertEqual(data['name'], 'section_role_classifier')
        self.assertEqual(data['metadata']['type'], 'DOC_PROCESSOR')
        self.assertEqual(data['metadata']['class'], 'SectionRoleClassifier')
        self.assertEqual(data['metadata']['module'],
                         'agentuniverse.agent.action.knowledge.doc_processor'
                         '.section_role_classifier')
        self.assertEqual(data['max_sections'], 30)
        self.assertTrue(data['positional_fallback'])

    def test_deterministic_output(self):
        text = ("# Introduction\n\nbody\n\n"
                "# Methods\n\nbody\n\n"
                "# Results and Discussion\n\nbody\n\n"
                "# Oddly Titled Tail\n\nbody\n")
        first = Document(text=text)
        second = Document(text=text)
        self.classifier.process_docs([first])
        self.classifier.process_docs([second])
        self.assertEqual(first.metadata, second.metadata)
        # And stable across a fresh instance with identical config.
        other = SectionRoleClassifier()
        third = Document(text=text)
        other.process_docs([third])
        self.assertEqual(first.metadata, third.metadata)


if __name__ == '__main__':
    unittest.main()

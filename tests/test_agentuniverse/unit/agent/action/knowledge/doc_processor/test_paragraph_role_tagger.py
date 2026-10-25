# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_paragraph_role_tagger.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.paragraph_role_tagger import \
    ParagraphRoleTagger
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Cue-free narrative paragraphs used for the elaboration default.
NARRATIVE_A = "The valley sits between two ridgelines."
NARRATIVE_B = "Farms occupy the lower slopes near the river."
NARRATIVE_C = "Villages cluster around the old bridge."


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _single(text: str) -> dict:
    """Process a one-paragraph document, returning its metadata."""
    tagger = ParagraphRoleTagger()
    result = tagger.process_docs([_doc(text)], Query(query_str='roles'))
    return result[0].metadata


class TestParagraphRoleTagger(unittest.TestCase):
    """Comprehensive test suite for ParagraphRoleTagger."""

    def setUp(self):
        self.tagger = ParagraphRoleTagger()
        self.query = Query(query_str='paragraph roles')

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _entry(self, text: str, index: int = 0) -> dict:
        """Return the paragraph_roles entry `index` of one-paragraph-
        (or larger) document text."""
        result = self.tagger.process_docs([_doc(text)], self.query)
        return result[0].metadata['paragraph_roles'][index]

    def _middle_entry(self, text: str) -> dict:
        """Return the entry of `text` placed between two cue-free
        narrative paragraphs, so no positional bonus applies."""
        result = self.tagger.process_docs(
            [_doc(f'{NARRATIVE_A}\n\n{text}\n\n{NARRATIVE_C}')],
            self.query)
        return result[0].metadata['paragraph_roles'][1]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: 8 early words, 0.5 positional bonus, 50-entry cap
        and the three standard metadata keys."""
        t = ParagraphRoleTagger()
        self.assertEqual(t.early_words, 8)
        self.assertEqual(t.positional_bonus, 0.5)
        self.assertEqual(t.max_role_entries, 50)
        self.assertEqual(t.roles_key, 'paragraph_roles')
        self.assertEqual(t.counts_key, 'role_counts')
        self.assertEqual(t.pattern_key, 'dominant_pattern')

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'paragraph_role_tagger',
            'description': 'paragraph role tagger',
            'early_words': 4,
            'positional_bonus': 1.0,
            'max_role_entries': 10,
            'roles_key': 'roles',
            'counts_key': 'counts',
            'pattern_key': 'pattern',
        })
        t = ParagraphRoleTagger()
        t._initialize_by_component_configer(configer)
        self.assertEqual(t.early_words, 4)
        self.assertEqual(t.positional_bonus, 1.0)
        self.assertEqual(t.max_role_entries, 10)
        self.assertEqual(t.roles_key, 'roles')
        self.assertEqual(t.counts_key, 'counts')
        self.assertEqual(t.pattern_key, 'pattern')
        self.assertEqual(t.name, 'paragraph_role_tagger')

    def test_invalid_configuration_raises(self):
        """Out-of-range or mistyped parameters fail at load time."""
        base = {
            'name': 't', 'description': 'd',
            'early_words': 8, 'positional_bonus': 0.5,
            'max_role_entries': 50,
            'roles_key': 'paragraph_roles',
            'counts_key': 'role_counts',
            'pattern_key': 'dominant_pattern',
        }
        for key, value in (
            ('early_words', 0),
            ('early_words', -3),
            ('early_words', 2.5),
            ('early_words', True),
            ('positional_bonus', -0.5),
            ('positional_bonus', 'big'),
            ('positional_bonus', True),
            ('max_role_entries', 0),
            ('max_role_entries', -1),
            ('max_role_entries', 1.5),
            ('roles_key', 5),
            ('counts_key', ['x']),
            ('pattern_key', {}),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f'{key}={value!r}'):
                ParagraphRoleTagger()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Per-role cue detection (English) ==========

    def test_intro_cues_english(self):
        """Early intro cues tag the paragraph as intro with the matched
        cue reported."""
        meta = _single('First of all, the framework loads its '
                       'configuration. It then validates every entry '
                       'before the service starts.')
        self.assertEqual(meta['paragraph_roles'][0]['role'], 'intro')
        self.assertEqual(meta['paragraph_roles'][0]['cue'], 'first of all')

        meta = _single('In this article we survey the design.')
        self.assertEqual(meta['paragraph_roles'][0]['role'], 'intro')
        self.assertEqual(meta['paragraph_roles'][0]['cue'],
                         'in this article')

    def test_transition_cues_english(self):
        """Early transition cues tag the paragraph as transition."""
        meta = _single('Furthermore, the cache layer absorbs traffic '
                       'spikes. Requests queue briefly instead of '
                       'failing outright.')
        self.assertEqual(meta['paragraph_roles'][0]['role'], 'transition')
        self.assertEqual(meta['paragraph_roles'][0]['cue'], 'furthermore')

    def test_contrast_cues_english(self):
        """Early contrast cues tag the paragraph as contrast."""
        meta = _single('However, the nightly batch failed twice. '
                       'Operators retried the job after each failure.')
        self.assertEqual(meta['paragraph_roles'][0]['role'], 'contrast')
        self.assertEqual(meta['paragraph_roles'][0]['cue'], 'however')

    def test_conclusion_cues_english(self):
        """Early conclusion cues tag the paragraph as conclusion."""
        meta = _single('In conclusion, the migration met its deadline. '
                       'The legacy system retires this quarter.')
        self.assertEqual(meta['paragraph_roles'][0]['role'], 'conclusion')
        self.assertEqual(meta['paragraph_roles'][0]['cue'],
                         'in conclusion')

    def test_elaboration_example_cues_english(self):
        """Example markers never add score but are reported as the
        elaboration cue."""
        for text, cue in (
            ('The gateway applies several safeguards. It enforces rate '
             'limits, for example rejecting bursts above the threshold.',
             'for example'),
            ('Several storage engines exist. Some favor reads, such as '
             'the columnar ones.', 'such as'),
            ('Costs fell across regions (e.g. compute and storage).',
             'e.g.'),
        ):
            with self.subTest(cue=cue):
                entry = self._entry(text)
                self.assertEqual(entry['role'], 'elaboration')
                self.assertEqual(entry['cue'], cue)

    def test_role_cues_chinese(self):
        """Each Chinese cue phrase drives its role from the paragraph
        opening."""
        for text, role in (
            ('本文将系统介绍该组件的设计。', 'intro'),
            ('此外，服务支持水平扩展。', 'transition'),
            ('然而，线上结果并不理想。', 'contrast'),
            ('总之，项目达成了预期目标。', 'conclusion'),
            ('该模块提供多种能力，例如缓存与重试。', 'elaboration'),
        ):
            with self.subTest(role=role):
                entry = self._entry(text)
                self.assertEqual(entry['role'], role)
        self.assertEqual(self._entry('该模块提供多种能力，例如缓存与重试。')
                         ['cue'], '例如')

    # ========== Early vs anywhere weights ==========

    def test_early_cue_beats_anywhere_cue(self):
        """An early intro cue (weight 2) outranks a single anywhere
        contrast cue (weight 1)."""
        text = ('First of all the study covered three regions however '
                'the data stayed incomplete.')
        entry = self._entry(text)
        self.assertEqual(entry['role'], 'intro')
        self.assertEqual(entry['cue'], 'first of all')

    def test_anywhere_cue_still_detected(self):
        """A cue beyond the early window keeps weight 1 and still wins
        when it is the only cue."""
        text = ('The committee met again on thursday after long debate '
                'however no decision emerged.')
        entry = self._entry(text)
        self.assertEqual(entry['role'], 'contrast')
        self.assertEqual(entry['cue'], 'however')

    def test_early_window_is_eight_words(self):
        """A cue starting at the 8th word unit is early (weight 2);
        starting at the 9th it is anywhere (weight 1)."""
        inside = ('one two three four five six seven however nine ten '
                  'eleven twelve')
        outside = ('one two three four five six seven eight however '
                   'nine ten eleven')
        # Middle paragraph (index 1 of 3): no positional bonuses.
        self.assertEqual(
            self.tagger._role_scores(inside, 1, 3)['contrast'], 2.0)
        self.assertEqual(
            self.tagger._role_scores(outside, 1, 3)['contrast'], 1.0)

    def test_early_window_configurable(self):
        """early_words narrows or widens the window: with a two-word
        window the 8th-word cue loses its early weight."""
        inside = ('one two three four five six seven however nine ten '
                  'eleven twelve')
        self.assertEqual(
            self.tagger._role_scores(inside, 1, 3)['contrast'], 2.0)
        self.tagger.early_words = 2
        self.assertEqual(
            self.tagger._role_scores(inside, 1, 3)['contrast'], 1.0)

    def test_early_window_counts_cjk_characters_individually(self):
        """For Chinese text each ideograph is a word unit, so a cue
        nine characters in is beyond the default eight-unit window."""
        early = '然而，性能问题仍然突出。'
        late = '系统架构经过多轮评审与讨论然而性能问题仍然突出。'
        self.assertEqual(
            self.tagger._role_scores(early, 1, 3)['contrast'], 2.0)
        self.assertEqual(
            self.tagger._role_scores(late, 1, 3)['contrast'], 1.0)

    # ========== Tie priority ==========

    def test_tie_priority_contrast_over_conclusion(self):
        """Two anywhere cues with equal weight resolve to contrast."""
        text = ('The committee reviewed all of the submitted evidence '
                'before it finally voted, however the audit later '
                'disagreed.')
        entry = self._middle_entry(text)
        self.assertEqual(entry['role'], 'contrast')
        self.assertEqual(entry['cue'], 'however')

    def test_tie_priority_full_chain(self):
        """conclusion beats transition; transition beats intro; a
        four-way tie resolves to contrast. The paragraphs sit in the
        middle of narrative documents so no positional bonus applies."""
        conclusion_vs_transition = (
            'Analysts studied the regional quarterly figures for '
            'several weeks moreover in summary the outlook improved.')
        transition_vs_intro = (
            'The research team compiled its findings across two '
            'continents we will moreover present the dataset.')
        four_way = (
            'After several months of quiet preparation the committee '
            'however in summary moreover we will publish the findings.')
        self.assertEqual(
            self._middle_entry(conclusion_vs_transition)['role'],
            'conclusion')
        self.assertEqual(
            self._middle_entry(conclusion_vs_transition)['cue'],
            'in summary')
        self.assertEqual(self._middle_entry(transition_vs_intro)['role'],
                         'transition')
        self.assertEqual(self._middle_entry(transition_vs_intro)['cue'],
                         'moreover')
        self.assertEqual(self._middle_entry(four_way)['role'], 'contrast')
        self.assertEqual(self._middle_entry(four_way)['cue'], 'however')

    # ========== Positional bonuses ==========

    def test_first_paragraph_intro_bonus(self):
        """An anywhere intro cue plus the first-paragraph bonus (1.5)
        beats an anywhere contrast cue (1); without the bonus (middle
        paragraph) the same text resolves to contrast."""
        text = ('The draft opens with background sections before the '
                'authors write we will revisit the methods, however '
                'the appendix omits them.')
        meta = _single(f'{text}\n\nLater reviews trimmed the appendix.')
        self.assertEqual(meta['paragraph_roles'][0]['role'], 'intro')
        self.assertEqual(meta['paragraph_roles'][0]['cue'], 'we will')

        meta = _single(f'{NARRATIVE_A}\n\n{text}\n\n{NARRATIVE_C}')
        self.assertEqual(meta['paragraph_roles'][1]['role'], 'contrast')
        self.assertEqual(meta['paragraph_roles'][1]['cue'], 'however')

    def test_last_paragraph_conclusion_bonus(self):
        """An anywhere conclusion cue plus the last-paragraph bonus
        (1.5) beats an anywhere contrast cue (1); as a middle paragraph
        the same text ties and resolves to contrast."""
        text = ('The closing section of the long chapter concedes '
                'however that the data stayed thin, in summary the '
                'model still holds.')
        meta = _single(f'The chapter reviews earlier trials.\n\n{text}')
        self.assertEqual(meta['paragraph_roles'][1]['role'], 'conclusion')
        self.assertEqual(meta['paragraph_roles'][1]['cue'], 'in summary')

        meta = _single(f'{NARRATIVE_A}\n\n{text}\n\n{NARRATIVE_C}')
        self.assertEqual(meta['paragraph_roles'][1]['role'], 'contrast')
        self.assertEqual(meta['paragraph_roles'][1]['cue'], 'however')

    def test_single_paragraph_receives_both_bonuses(self):
        """A lone paragraph is both first and last: intro and conclusion
        tie at 1.5 and the documented priority awards conclusion."""
        meta = _single('After the very long review the committee wrote '
                       'we will however in summary deliver the plan.')
        self.assertEqual(meta['paragraph_roles'][0]['role'], 'conclusion')
        self.assertEqual(meta['paragraph_roles'][0]['cue'], 'in summary')

    def test_positional_bonus_requires_cue(self):
        """Cue-free boundary paragraphs keep the elaboration default:
        the bonus only nudges roles that already matched a cue."""
        meta = _single(f'{NARRATIVE_A}\n\n{NARRATIVE_B}\n\n{NARRATIVE_C}')
        roles = [e['role'] for e in meta['paragraph_roles']]
        self.assertEqual(roles, ['elaboration'] * 3)

    # ========== Elaboration default ==========

    def test_elaboration_colon_list(self):
        """A colon-list marks the paragraph as elaboration evidence with
        no phrase cue to report."""
        text = 'The deployment offers three modes: strict, relaxed and audit.'
        self.assertTrue(ParagraphRoleTagger._has_colon_list(text))
        entry = self._entry(text)
        self.assertEqual(entry['role'], 'elaboration')
        self.assertIsNone(entry['cue'])

    def test_no_cue_pure_narrative_all_elaboration(self):
        """A pure narrative document comes out uniformly elaboration
        with null cues — the documented default."""
        meta = _single(f'{NARRATIVE_A}\n\n{NARRATIVE_B}\n\n{NARRATIVE_C}')
        self.assertEqual(meta['role_counts'],
                         {'intro': 0, 'transition': 0, 'contrast': 0,
                          'conclusion': 0, 'elaboration': 3})
        self.assertTrue(all(e['role'] == 'elaboration'
                            for e in meta['paragraph_roles']))
        self.assertTrue(all(e['cue'] is None
                            for e in meta['paragraph_roles']))
        self.assertEqual(meta['dominant_pattern'], 'elaboration-heavy')

    # ========== Counts and dominant pattern ==========

    def test_dominant_pattern_balanced_at_half(self):
        """Exactly half of one role counts as balanced, never heavy."""
        meta = _single('First of all we calibrate the sensor.'
                       f'\n\n{NARRATIVE_A}')
        self.assertEqual(meta['dominant_pattern'], 'balanced')

        text = '\n\n'.join(['However the pilot succeeded.',
                            'However the pilot succeeded.',
                            NARRATIVE_A, NARRATIVE_B])
        self.assertEqual(_single(text)['dominant_pattern'], 'balanced')

    def test_dominant_pattern_heavy_above_half(self):
        """Strictly more than half of one role yields '<role>-heavy'."""
        meta = _single('First of all we calibrate the sensor.'
                       f'\n\nFirst of all we align the optics.')
        self.assertEqual(meta['dominant_pattern'], 'intro-heavy')

        text = '\n\n'.join(['However the pilot succeeded.',
                            'However the pilot succeeded.', NARRATIVE_A])
        self.assertEqual(_single(text)['dominant_pattern'],
                         'contrast-heavy')

    def test_role_counts_cover_paragraphs_beyond_cap(self):
        """The entry list caps at max_role_entries while counts keep
        covering every paragraph and indices stay true."""
        paragraphs = [f'stock number {i} closed flat during the session'
                      for i in range(60)]
        text = '\n\n'.join(paragraphs)
        meta = _single(text)
        self.assertEqual(len(meta['paragraph_roles']), 50)
        self.assertEqual(meta['role_counts']['elaboration'], 60)
        self.assertEqual([e['paragraph_index']
                          for e in meta['paragraph_roles']],
                         list(range(50)))
        self.assertLess(meta['paragraph_roles'][-1]['span'][1],
                        len(text))

    def test_max_role_entries_configurable(self):
        """The cap follows the configured value."""
        self.tagger.max_role_entries = 2
        result = self.tagger.process_docs(
            [_doc(f'{NARRATIVE_A}\n\n{NARRATIVE_B}\n\n{NARRATIVE_C}')],
            self.query)
        meta = result[0].metadata
        self.assertEqual(len(meta['paragraph_roles']), 2)
        self.assertEqual(meta['role_counts']['elaboration'], 3)

    # ========== Paragraph structure and spans ==========

    def test_span_offsets_map_to_original_text(self):
        """Spans are [start, end) ranges of the stripped paragraph
        contents inside the original text, with blank-line runs and
        CRLF separators both respected."""
        text = ('  Alpha para one.  \n\n\n Beta para two \r\n\r\n'
                'Gamma.')
        meta = _single(text)
        entries = meta['paragraph_roles']
        self.assertEqual(len(entries), 3)
        for entry, expected in zip(entries, ('Alpha para one.',
                                             'Beta para two',
                                             'Gamma.')):
            start, end = entry['span']
            self.assertEqual(text[start:end], expected)

    def test_blank_line_blocks_and_soft_wraps(self):
        """Single newlines keep a block together; only blank lines
        split paragraphs."""
        text = 'Alpha wraps\nonto two lines.\n\nBeta follows.'
        entries = _single(text)['paragraph_roles']
        self.assertEqual(len(entries), 2)
        start, end = entries[0]['span']
        self.assertEqual(text[start:end], 'Alpha wraps\nonto two lines.')

    def test_single_paragraph_document(self):
        """A one-paragraph document yields exactly one entry whose span
        covers the stripped content."""
        text = '  However the pilot succeeded.  '
        meta = _single(text)
        self.assertEqual(len(meta['paragraph_roles']), 1)
        entry = meta['paragraph_roles'][0]
        self.assertEqual(text[entry['span'][0]:entry['span'][1]],
                         'However the pilot succeeded.')
        self.assertEqual(meta['role_counts']['contrast'], 1)

    def test_empty_and_blank_documents(self):
        """Empty input, empty text, None text and whitespace-only text
        produce zeroed counts, an empty list and 'balanced'."""
        self.assertEqual(
            ParagraphRoleTagger().process_docs([], self.query), [])
        for text in ('', ' \n\n \t '):
            meta = _single(text)
            self.assertEqual(meta['paragraph_roles'], [])
            self.assertEqual(meta['role_counts'],
                             {'intro': 0, 'transition': 0, 'contrast': 0,
                              'conclusion': 0, 'elaboration': 0})
            self.assertEqual(meta['dominant_pattern'], 'balanced')
        # None text is tolerated at processing time (the Document
        # constructor itself rejects building one from scratch).
        none_doc = Document(text='')
        none_doc.text = None
        meta = self.tagger.process_docs([none_doc], self.query) \
            [0].metadata
        self.assertEqual(meta['paragraph_roles'], [])
        self.assertEqual(meta['dominant_pattern'], 'balanced')

    # ========== Word-boundary and sentence-start traps ==========

    def test_word_boundary_traps(self):
        """English cues fire only on word boundaries."""
        for text in (
            'Secondhand parts kept the fleet alive.',
            'The nextdoor neighbours stayed quiet.',
            'The crew will depart at dawn.',
        ):
            with self.subTest(text=text):
                entry = self._entry(text)
                self.assertEqual(entry['role'], 'elaboration')
                self.assertIsNone(entry['cue'])

    def test_but_requires_sentence_start(self):
        """'But' counts only at a sentence start: mid-sentence 'but' and
        the prefix of 'Butter' are ignored, sentence-initial 'But'
        marks contrast."""
        entry = self._entry('Butter was invented long before margarine.')
        self.assertEqual(entry['role'], 'elaboration')
        self.assertIsNone(entry['cue'])

        entry = self._entry('The team tried but missed the deadline.')
        self.assertEqual(entry['role'], 'elaboration')

        entry = self._entry('We tried hard. But it failed.')
        self.assertEqual(entry['role'], 'contrast')
        self.assertEqual(entry['cue'], 'but')

    # ========== Pipeline-shape and metadata tests ==========

    def test_documents_returned_unchanged_in_order(self):
        """Every document object passes through in order with text and
        id untouched."""
        doc_a = _doc(f'{NARRATIVE_A}', source='a')
        doc_b = _doc('However the pilot succeeded.', source='b')
        result = self.tagger.process_docs([doc_a, doc_b], self.query)
        self.assertEqual(result, [doc_a, doc_b])
        self.assertEqual(doc_a.text, NARRATIVE_A)
        self.assertEqual(doc_b.id, doc_b.id)
        self.assertEqual(doc_a.metadata['source'], 'a')

    def test_metadata_copied_before_mutation(self):
        """Pre-existing metadata survives, and the stamp goes through a
        copied mapping so the caller's original dict never gains the new
        keys in place."""
        doc = _doc('However the pilot succeeded.', source='wire', rank=1)
        original_meta = doc.metadata
        self.tagger.process_docs([doc], self.query)
        self.assertEqual(doc.metadata['source'], 'wire')
        self.assertEqual(doc.metadata['rank'], 1)
        for key in ('paragraph_roles', 'role_counts', 'dominant_pattern'):
            self.assertIn(key, doc.metadata)
        self.assertNotIn('paragraph_roles', original_meta)
        self.assertIsNot(doc.metadata, original_meta)

    def test_disabled_keys_stamp_nothing(self):
        """Empty metadata keys disable every stamp."""
        self.tagger.roles_key = ''
        self.tagger.counts_key = ''
        self.tagger.pattern_key = ''
        doc = _doc('However the pilot succeeded.', source='wire')
        self.tagger.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {'source': 'wire'})

    def test_determinism(self):
        """Repeated runs over the same input produce identical
        metadata."""
        text = ('First of all we calibrate the sensor.\n\n'
                f'{NARRATIVE_A}\n\nIn addition the housing isolates '
                'vibration, however the cable still hums.\n\n'
                'In summary the rig performs.')
        first = ParagraphRoleTagger().process_docs([_doc(text)], None)
        second = ParagraphRoleTagger().process_docs([_doc(text)], None)
        self.assertEqual(first[0].metadata, second[0].metadata)
        roles = [e['role'] for e in first[0].metadata['paragraph_roles']]
        self.assertEqual(roles, ['intro', 'elaboration', 'contrast',
                                 'conclusion'])

    def test_has_colon_list_edge_cases(self):
        """A colon without following separators is not a colon-list; a
        fullwidth colon with enumeration commas is."""
        self.assertFalse(
            ParagraphRoleTagger._has_colon_list('See the manual: page 9.'))
        self.assertTrue(ParagraphRoleTagger._has_colon_list(
            '该方案覆盖三个阶段：设计、验证与发布。'))


if __name__ == '__main__':
    unittest.main()

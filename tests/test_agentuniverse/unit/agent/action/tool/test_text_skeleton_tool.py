# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20 10:00
# @Author  : 123123213weqw
# @Email   :
# @FileName: test_text_skeleton_tool.py

import asyncio
import json
import unittest

from agentuniverse.agent.action.tool.common_tool.text_skeleton_tool import (
    TextSkeletonTool,
)

# ---------------------------------------------------------------------------
# Fixtures with hand-extracted ground truths.
# ---------------------------------------------------------------------------
PARA_1 = ('Dr. Smith studied physics at Stanford University. '
          'He published his first paper in 2015, and it covered quantum computing. '
          'The paper was cited thousands of times.')
P1_S1 = 'Dr. Smith studied physics at Stanford University.'
P1_S2 = ('He published his first paper in 2015, '
         'and it covered quantum computing.')
P1_S3 = 'The paper was cited thousands of times.'

PARA_2 = ('The tool supports several modes, e.g. skeleton, digest, and outline '
          'extraction. Configuration is minimal; sensible defaults are '
          'provided, etc. Users can extend it easily.')
P2_S1 = ('The tool supports several modes, e.g. skeleton, digest, and '
         'outline extraction.')
P2_S2 = ('Configuration is minimal; sensible defaults are provided, etc. '
         'Users can extend it easily.')

PARA_3 = 'A single-sentence paragraph stands alone.'
P3_S1 = 'A single-sentence paragraph stands alone.'

FIXTURE = PARA_1 + '\n\n' + PARA_2 + '\n\n' + PARA_3

CJK_TEXT = ('机器学习发展迅速。深度学习改变了自然语言处理。'
            '大语言模型正在涌现。')
CJK_S1 = '机器学习发展迅速。'
CJK_S3 = '大语言模型正在涌现。'

ELLIPSIS = '\u2026'


class TextSkeletonToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = TextSkeletonTool()

    # -- helpers -------------------------------------------------------------
    def _run(self, **kwargs):
        return json.loads(self.tool.execute(**kwargs))

    # -- skeleton mode: ground truth first/last sentences + abbreviations ----
    def test_skeleton_ground_truth_sentences(self):
        result = self._run(text=FIXTURE, mode='skeleton', n=500)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['mode'], 'skeleton')
        self.assertEqual(result['paragraph_count'], 3)
        skeletons = result['skeletons']
        self.assertEqual(len(skeletons), 3)

        # n=500 exceeds every paragraph length: leads are untruncated.
        self.assertEqual(skeletons[0]['skeleton'],
                         f'{P1_S1} | {PARA_1} | {P1_S3}')
        self.assertEqual(skeletons[1]['skeleton'],
                         f'{P2_S1} | {PARA_2} | {P2_S2}')
        # Single-sentence paragraph: last sentence duplicates the first and
        # is omitted, and the lead is not truncated (no ellipsis).
        self.assertEqual(skeletons[2]['skeleton'],
                         f'{P3_S1} | {PARA_3}')

    def test_skeleton_truncated_lead_ellipses(self):
        result = self._run(text=FIXTURE, mode='skeleton', n=10)
        lead_1 = PARA_1[:10] + ELLIPSIS
        lead_3 = PARA_3[:10] + ELLIPSIS
        skeletons = result['skeletons']
        self.assertEqual(skeletons[0]['skeleton'],
                         f'{P1_S1} | {lead_1} | {P1_S3}')
        self.assertEqual(skeletons[2]['skeleton'],
                         f'{P3_S1} | {lead_3}')
        self.assertEqual(len(skeletons[1]['skeleton'].split(' | ')[1]),
                         11)  # n chars + one ellipsis code point

    def test_skeleton_exact_boundary_n_equals_paragraph_length(self):
        # n == len(PARA_3): nothing is omitted, so no ellipsis.
        result = self._run(text=PARA_3, mode='skeleton', n=len(PARA_3))
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['skeletons'][0]['skeleton'],
                         f'{P3_S1} | {PARA_3}')

    def test_skeleton_one_below_boundary_truncates(self):
        n = len(PARA_3) - 1
        result = self._run(text=PARA_3, mode='skeleton', n=n)
        self.assertEqual(result['skeletons'][0]['skeleton'],
                         f'{P3_S1} | {PARA_3[:n]}{ELLIPSIS}')

    def test_skeleton_component_toggles(self):
        base = dict(text=FIXTURE, mode='skeleton', n=20)

        result = self._run(**base, include_first_sentence=False,
                           include_last_sentence=False)
        self.assertEqual([s['skeleton'] for s in result['skeletons']],
                         [PARA_1[:20] + ELLIPSIS,
                          PARA_2[:20] + ELLIPSIS,
                          PARA_3[:20] + ELLIPSIS])

        result = self._run(**base, include_lead_chars=False,
                           include_last_sentence=False)
        self.assertEqual([s['skeleton'] for s in result['skeletons']],
                         [P1_S1, P2_S1, P3_S1])

        result = self._run(**base, include_first_sentence=False,
                           include_lead_chars=False)
        # Last sentence per paragraph; a single-sentence paragraph still
        # reports its only sentence when the first-sentence toggle is off.
        self.assertEqual([s['skeleton'] for s in result['skeletons']],
                         [P1_S3, P2_S2, P3_S1])

    def test_skeleton_paragraph_index_and_char_span(self):
        text = 'Para one here.\n\nSecond para here.\n\n\n   Third para.  \n'
        result = self._run(text=text, mode='skeleton', n=50,
                           include_paragraph_index=True,
                           include_char_span=True)
        self.assertEqual(result['status'], 'success')
        items = result['skeletons']
        self.assertEqual([i['paragraph_index'] for i in items], [0, 1, 2])
        # Hand-computed code-point spans of the trimmed paragraphs.
        self.assertEqual([i['char_span'] for i in items],
                         [[0, 14], [16, 33], [39, 50]])
        # Spans address the original text exactly.
        self.assertEqual(text[0:14], 'Para one here.')
        self.assertEqual(text[16:33], 'Second para here.')
        self.assertEqual(text[39:50], 'Third para.')
        self.assertEqual([i['skeleton'] for i in items],
                         ['Para one here. | Para one here.',
                          'Second para here. | Second para here.',
                          'Third para. | Third para.'])

    def test_skeleton_multiline_paragraph(self):
        text = 'Line one continues\nline two here. More text follows.'
        result = self._run(text=text, mode='skeleton', n=60)
        self.assertEqual(result['paragraph_count'], 1)
        self.assertEqual(
            result['skeletons'][0]['skeleton'],
            'Line one continues\nline two here. | '
            'Line one continues\nline two here. More text follows. | '
            'More text follows.')

    # -- digest mode ----------------------------------------------------------
    def test_digest_joins_first_and_last_paragraph_first_sentences(self):
        result = self._run(text=FIXTURE, mode='digest')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['mode'], 'digest')
        self.assertEqual(result['paragraph_count'], 3)
        self.assertEqual(result['sentence_count'], 6)  # 3 + 2 + 1
        self.assertEqual(result['char_count'], len(FIXTURE))
        self.assertEqual(result['digest'],
                         f'{P1_S1} {ELLIPSIS} {P3_S1}')

    def test_digest_single_paragraph_no_joiner(self):
        result = self._run(text=PARA_1, mode='digest')
        self.assertEqual(result['digest'], P1_S1)
        self.assertEqual(result['paragraph_count'], 1)
        self.assertEqual(result['sentence_count'], 3)

    def test_digest_stats_with_capped_paragraphs(self):
        result = self._run(text=FIXTURE, mode='digest', max_paragraphs=2)
        self.assertEqual(result['paragraph_count'], 3)
        self.assertEqual(result['paragraphs_omitted'], 1)
        # The last processed paragraph is now PARA_2.
        self.assertEqual(result['digest'], f'{P1_S1} {ELLIPSIS} {P2_S1}')

    # -- first_sentences mode -------------------------------------------------
    def test_first_sentences_outline(self):
        result = self._run(text=FIXTURE, mode='first_sentences')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['mode'], 'first_sentences')
        self.assertEqual(result['first_sentences'], [P1_S1, P2_S1, P3_S1])
        self.assertEqual(result['paragraph_count'], 3)

    def test_first_sentences_conservative_guards(self):
        # '.' followed by a lowercase word does not split (conservative rule).
        text = 'We tried many options, e.g. retry and backoff. nothing changed.'
        result = self._run(text=text, mode='first_sentences')
        self.assertEqual(result['first_sentences'], [text])

        # Decimals and filenames never split.
        result = self._run(text='Version 2.0 shipped in config.yaml today.',
                           mode='first_sentences')
        self.assertEqual(result['first_sentences'],
                         ['Version 2.0 shipped in config.yaml today.'])

        # '!' and '?' split regardless of the next word's case.
        result = self._run(text='Is this ready? Yes! great.', mode='skeleton',
                           n=100)
        self.assertEqual(result['skeletons'][0]['skeleton'],
                         'Is this ready? | Is this ready? Yes! great. | great.')

    # -- lead_chars mode --------------------------------------------------------
    def test_lead_chars_mode(self):
        result = self._run(text=FIXTURE, mode='lead_chars', n=10)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['mode'], 'lead_chars')
        self.assertEqual(result['n'], 10)
        self.assertEqual(result['leads'],
                         [PARA_1[:10] + ELLIPSIS,
                          PARA_2[:10] + ELLIPSIS,
                          PARA_3[:10] + ELLIPSIS])

    def test_lead_chars_exact_boundary(self):
        result = self._run(text=PARA_2, mode='lead_chars', n=len(PARA_2))
        self.assertEqual(result['leads'], [PARA_2])

    # -- CJK safety -------------------------------------------------------------
    def test_cjk_paragraphs(self):
        result = self._run(text=CJK_TEXT, mode='first_sentences')
        self.assertEqual(result['first_sentences'], [CJK_S1])

        result = self._run(text=CJK_TEXT, mode='lead_chars', n=10)
        self.assertEqual(result['leads'],
                         ['机器学习发展迅速。深' + ELLIPSIS])

        result = self._run(text=CJK_TEXT, mode='skeleton', n=60)
        # len(CJK_TEXT) == 33 <= 60: no truncation ellipsis.
        self.assertEqual(result['skeletons'][0]['skeleton'],
                         f'{CJK_S1} | {CJK_TEXT} | {CJK_S3}')

    def test_cjk_digest(self):
        result = self._run(text=CJK_TEXT, mode='digest')
        self.assertEqual(result['sentence_count'], 3)
        self.assertEqual(result['char_count'], len(CJK_TEXT))
        self.assertEqual(result['digest'], CJK_S1)

    # -- caps and determinism ---------------------------------------------------
    def test_max_paragraphs_cap(self):
        result = self._run(text=FIXTURE, mode='skeleton', n=20,
                           max_paragraphs=2)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['paragraph_count'], 3)
        self.assertEqual(len(result['skeletons']), 2)
        self.assertEqual(result['paragraphs_omitted'], 1)

    def test_deterministic_output(self):
        a = self.tool.execute(text=FIXTURE, mode='skeleton', n=25)
        b = self.tool.execute(text=FIXTURE, mode='skeleton', n=25)
        self.assertEqual(a, b)

    # -- async execution ----------------------------------------------------------
    def test_async_execute(self):
        raw = asyncio.run(
            self.tool.async_execute(text=FIXTURE, mode='digest'))
        result = json.loads(raw)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['digest'], f'{P1_S1} {ELLIPSIS} {P3_S1}')

    # -- error matrix ---------------------------------------------------------------
    def test_error_text_not_a_string(self):
        for bad in (None, 123, ['text']):
            result = self._run(text=bad, mode='skeleton')
            self.assertEqual(result['status'], 'error')
            self.assertIn('text must be a string', result['error'])

    def test_error_empty_text(self):
        for bad in ('', '   ', ' \n\t\n '):
            result = self._run(text=bad, mode='skeleton')
            self.assertEqual(result['status'], 'error')
            self.assertIn('empty', result['error'])

    def test_error_invalid_mode(self):
        result = self._run(text=FIXTURE, mode='outline')
        self.assertEqual(result['status'], 'error')
        self.assertIn('Invalid mode', result['error'])
        for valid in ('skeleton', 'digest', 'first_sentences', 'lead_chars'):
            self.assertIn(valid, result['error'])

    def test_error_n_bounds_and_type(self):
        for bad in (9, 501, -10, '60', 60.0, True):
            result = self._run(text=FIXTURE, mode='lead_chars', n=bad)
            self.assertEqual(result['status'], 'error', f'n={bad!r}')
        for good in (10, 60, 500):
            result = self._run(text=FIXTURE, mode='lead_chars', n=good)
            self.assertEqual(result['status'], 'success', f'n={good!r}')

    def test_error_no_skeleton_component_enabled(self):
        result = self._run(text=FIXTURE, mode='skeleton',
                           include_first_sentence=False,
                           include_lead_chars=False,
                           include_last_sentence=False)
        self.assertEqual(result['status'], 'error')
        self.assertIn('At least one skeleton component', result['error'])
        # Other modes ignore the component toggles entirely.
        result = self._run(text=FIXTURE, mode='first_sentences',
                           include_first_sentence=False,
                           include_lead_chars=False,
                           include_last_sentence=False)
        self.assertEqual(result['status'], 'success')

    def test_error_toggle_type_validation(self):
        result = self._run(text=FIXTURE, mode='skeleton',
                           include_first_sentence='yes')
        self.assertEqual(result['status'], 'error')
        self.assertIn('include_first_sentence must be a boolean',
                      result['error'])
        result = self._run(text=FIXTURE, mode='digest',
                           include_char_span=1)
        self.assertEqual(result['status'], 'error')
        self.assertIn('include_char_span must be a boolean', result['error'])

    def test_error_max_paragraphs_bounds_and_type(self):
        for bad in (0, 1001, '10', 2.5, True):
            result = self._run(text=FIXTURE, mode='digest',
                               max_paragraphs=bad)
            self.assertEqual(result['status'], 'error', f'bad={bad!r}')
        for good in (1, 200, 1000):
            result = self._run(text=FIXTURE, mode='digest',
                               max_paragraphs=good)
            self.assertEqual(result['status'], 'success', f'good={good!r}')


if __name__ == '__main__':
    unittest.main()

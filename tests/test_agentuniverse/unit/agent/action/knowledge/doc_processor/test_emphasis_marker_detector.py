# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_emphasis_marker_detector.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.emphasis_marker_detector import \
    EmphasisMarkerDetector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestEmphasisMarkerDetector(unittest.TestCase):
    """Comprehensive test suite for EmphasisMarkerDetector."""

    def setUp(self):
        self.detector = EmphasisMarkerDetector()
        self.query = Query(query_str="emphasis")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _hits(self, text: str):
        """Scan one text and return the raw hit list."""
        return self.detector._scan(text)

    def _kinds(self, text: str):
        return [h['kind'] for h in self._hits(text)]

    def _texts(self, text: str):
        return [h['text'] for h in self._hits(text)]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: empty allowlist, 100 hits / 20 terms caps, standard
        metadata keys."""
        d = EmphasisMarkerDetector()
        self.assertEqual(d.caps_allowlist, [])
        self.assertEqual(d.max_hits, 100)
        self.assertEqual(d.max_terms, 20)
        self.assertEqual(d.emphasis_key, 'emphasis')
        self.assertEqual(d.counts_key, 'emphasis_counts')
        self.assertEqual(d.terms_key, 'emphasis_terms')

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'emphasis_marker_detector',
            'description': 'emphasis detector',
            'caps_allowlist': ['NASA', 'gdpr'],
            'max_hits': 7,
            'max_terms': 3,
            'emphasis_key': 'em',
            'counts_key': 'em_counts',
            'terms_key': 'em_terms',
        })
        d = EmphasisMarkerDetector()
        d._initialize_by_component_configer(configer)
        self.assertEqual(d.caps_allowlist, ['NASA', 'GDPR'])
        self.assertEqual(d.max_hits, 7)
        self.assertEqual(d.max_terms, 3)
        self.assertEqual(d.emphasis_key, 'em')
        self.assertEqual(d.counts_key, 'em_counts')
        self.assertEqual(d.terms_key, 'em_terms')
        self.assertEqual(d.name, 'emphasis_marker_detector')

    def test_invalid_configuration_raises(self):
        """Non-list allowlists, non-string / empty entries, bad caps and
        non-string metadata keys all fail at load time."""
        base = {
            'name': 'd', 'description': 'd',
            'caps_allowlist': [], 'max_hits': 10, 'max_terms': 5,
            'emphasis_key': 'emphasis', 'counts_key': 'c',
            'terms_key': 't',
        }
        for key, value in (
            ('caps_allowlist', 'NASA'),
            ('caps_allowlist', 5),
            ('caps_allowlist', ['OK', 42]),
            ('caps_allowlist', ['OK', '   ']),
            ('max_hits', 0),
            ('max_hits', -3),
            ('max_hits', 2.5),
            ('max_hits', True),
            ('max_terms', 0),
            ('max_terms', 1.5),
            ('emphasis_key', 7),
            ('counts_key', ['x']),
            ('terms_key', object()),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                EmphasisMarkerDetector()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Bold ground truths ==========

    def test_double_asterisk_bold(self):
        """**run** mid-sentence yields one bold hit with inner text and
        full-construct span."""
        text = "The **launch date** is fixed."
        hits = self._hits(text)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]['kind'], 'bold')
        self.assertEqual(hits[0]['text'], 'launch date')
        self.assertEqual(text[hits[0]['span'][0]:hits[0]['span'][1]],
                         '**launch date**')

    def test_double_underscore_bold(self):
        """__run__ (the underline spelling) reports kind bold."""
        text = "The __launch date__ is fixed."
        hits = self._hits(text)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]['kind'], 'bold')
        self.assertEqual(hits[0]['text'], 'launch date')
        self.assertEqual(text[hits[0]['span'][0]:hits[0]['span'][1]],
                         '__launch date__')

    def test_both_bold_markers_on_one_line(self):
        """Asterisk and underscore bold on one line are two distinct
        hits with disjoint, correct spans."""
        text = "both **ast** and __und__ count"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'ast'), ('bold', 'und')])
        self.assertEqual(text[hits[0]['span'][0]:hits[0]['span'][1]],
                         '**ast**')
        self.assertEqual(text[hits[1]['span'][0]:hits[1]['span'][1]],
                         '__und__')

    def test_bold_at_line_boundaries(self):
        """Constructs touching start and end of the line still parse."""
        text = "**whole line**"
        hits = self._hits(text)
        self.assertEqual(len(hits), 1)
        self.assertEqual((hits[0]['kind'], hits[0]['text']),
                         ('bold', 'whole line'))
        self.assertEqual(hits[0]['span'], [0, len(text)])

    def test_bold_edge_whitespace_never_matches(self):
        """** padded ** is not emphasis per the simplified flanking
        rule; unclosed markers report nothing."""
        self.assertEqual(self._hits("** padded **"), [])
        self.assertEqual(self._hits("**unclosed"), [])
        self.assertEqual(self._hits("closing only **"), [])

    def test_dunder_names_parse_as_bold(self):
        """'__init__' at word boundaries is markdown-bold exactly as
        CommonMark renders it; the intraword guard does not apply
        because the outer flanks are not word characters."""
        hits = self._hits("the __init__ method")
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'init')])
        # ... but a dunder glued into a longer identifier stays inert.
        self.assertEqual(self._hits("call obj.__init__(self) now")[0]
                         ['text'], 'init')

    # ========== ** versus * disambiguation ==========

    def test_single_asterisk_runs_do_not_break_bold(self):
        """A lone '*' inside a '**' run cannot close the bold, so the
        whole construct stays one bold hit."""
        text = "**a*b**"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'a*b')])
        self.assertEqual(text[hits[0]['span'][0]:hits[0]['span'][1]],
                         '**a*b**')

    def test_single_asterisk_italic(self):
        text = "an *italic term* here"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('italic', 'italic term')])
        self.assertEqual(text[hits[0]['span'][0]:hits[0]['span'][1]],
                         '*italic term*')

    def test_runs_of_three_or_more_markers_are_skipped(self):
        """'***compound***' is skipped whole rather than guessed at
        (documented simplification), and '=' runs != 2 never pair."""
        self.assertEqual(self._hits("***x***"), [])
        self.assertEqual(self._hits("___x___"), [])
        self.assertEqual(self._hits("a === b"), [])
        self.assertEqual(self._hits("2 = 2"), [])

    def test_lone_marker_never_closes_double_run(self):
        """'*a**b*' has no length-matched pair: the single runs pair
        together, the double opener finds no double closer."""
        text = "*a**b*"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('italic', 'a**b')])
        self.assertEqual(text[hits[0]['span'][0]:hits[0]['span'][1]],
                         '*a**b*')

    def test_nested_bold_containing_italic(self):
        """Inner italic emitted alongside the wrapping bold in document
        (span-start) order; the bold text keeps the inner markers as
        content."""
        text = "**a *b* c**"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'a *b* c'), ('italic', 'b')])
        self.assertEqual(text[hits[0]['span'][0]:hits[0]['span'][1]],
                         '**a *b* c**')
        self.assertEqual(text[hits[1]['span'][0]:hits[1]['span'][1]], '*b*')

    # ========== Italic and the intraword underscore guard ==========

    def test_single_underscore_italic(self):
        text = "an _italic term_ here"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('italic', 'italic term')])

    def test_snake_case_identifiers_are_not_italic(self):
        """Underscores flanked by word characters never open or close
        emphasis (CommonMark intraword rule)."""
        for text in (
            "the snake_case_name variable",
            "foo_bar",
            "a_file_name_here",
            "x_1_y",
        ):
            self.assertEqual(self._hits(text), [], text)

    def test_unicode_intraword_underscore_inert(self):
        """Word characters are Unicode alphanumerics, so underscores
        inside CJK or Cyrillic word chains stay inert exactly as
        CommonMark renders them (regression: ASCII-only word chars
        used to false-positive here)."""
        for text in (
            "中文_斜体_中文",
            "参数_说明_结束",
            "прилив_и_отлив",
            "中文__提示__中文",
            "数据_value_结束",
        ):
            with self.subTest(text=text):
                self.assertEqual(
                    [h for h in self._hits(text)
                     if h['kind'] in ('bold', 'italic')], [], text)

    def test_cjk_boundary_underscore_still_emphasizes(self):
        """Underscores at real boundaries (whitespace or punctuation on
        the outer flank) still pair even with CJK content inside."""
        hits = self._hits("说明 _重要_ 内容")
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('italic', '重要')])
        hits = self._hits("（__重要__）")
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', '重要')])

    def test_intraword_underscore_partial_cases(self):
        """'_a_b' cannot close on the intraword flank; nothing pairs."""
        self.assertEqual(self._hits("_a_b"), [])
        self.assertEqual(self._hits("a_b_c"), [])

    def test_underscore_and_asterisk_do_not_cross_pair(self):
        """Delimiters only pair within the same marker character."""
        self.assertEqual(self._hits("*a_b_"), [])
        self.assertEqual(
            [(h['kind'], h['text']) for h in self._hits("_a*b*")],
            [('italic', 'b')])

    def test_multiple_italics_pair_innermost_first(self):
        """Delimiters pair LIFO, but hits are reported in document
        order (the outer construct starts first)."""
        text = "*a *b* c*"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('italic', 'a *b* c'), ('italic', 'b')])

    def test_documented_commonmark_deviations_frozen(self):
        """The docstring's four documented deviations from full
        CommonMark rendering stay exactly as documented."""
        # 1. punctuation-only flanking still opens/closes
        self.assertEqual([(h['kind'], h['text']) for h in
                          self._hits("a*(foo)*")],
                         [('italic', '(foo)')])
        self.assertEqual([(h['kind'], h['text']) for h in
                          self._hits("bar**=== word**")],
                         [('bold', '=== word')])
        # 2. backslash escapes are not honored: the backslash before the
        #    opener stays outside the span, the one before the closer
        #    stays inside the text
        self.assertEqual([(h['kind'], h['text']) for h in
                          self._hits("\\*foo\\*")],
                         [('italic', 'foo\\')])
        # 3. pairing is length-matched, not CommonMark cross-length
        self.assertEqual([(h['kind'], h['text']) for h in
                          self._hits("___ _world)__")], [])
        self.assertEqual([(h['kind'], h['text']) for h in
                          self._hits("**a *b**")],
                         [('bold', 'a *b')])
        # 4. runs of three or more markers are skipped (frozen above)

    def test_link_inside_bold_keeps_link_syntax_as_content(self):
        """Emphasis wrapping a markdown link reports the raw link text
        as content: only emphasis markers are stripped, not inline
        markup."""
        self.assertEqual(
            [(h['kind'], h['text']) for h in self._hits("**[x](y)**")],
            [('bold', '[x](y)')])

    # ========== Code fence immunity ==========

    def test_backtick_fence_immunity(self):
        """Marker constructs inside a fenced code block are invisible;
        detection resumes after the fence."""
        text = ("Some **bold** text.\n"
                "```python\n"
                "**not bold** and *not italic* and ==not hl== and NOTCAPS\n"
                "```\n"
                "More *italic* here.")
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'bold'), ('italic', 'italic')])

    def test_tilde_fence_immunity(self):
        text = "~~strike~~ outside\n~~~\n**hidden**\n~~~\n__after__"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'after')])

    def test_fence_info_string_and_longer_opener(self):
        """Fences with language tags and longer fence runs close on a
        run of at least the opening length."""
        text = ("```yaml\n"
                "key: **value**\n"
                "````\n"
                "visible *em*\n")
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('italic', 'em')])

    def test_unclosed_fence_immunizes_the_rest(self):
        text = "before **ok**\n```\n**lost** and *lost*"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'ok')])

    def test_indented_fence_counts(self):
        text = "    ```\n    **hidden**\n    ```\n**shown**"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'shown')])

    def test_inline_backticks_are_not_fences(self):
        """Only fence lines immunize; inline code spans are scanned
        (documented simplification)."""
        hits = self._hits("use `**nice**` inline")
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'nice')])

    # ========== CAPS runs ==========

    def test_caps_runs_detected(self):
        """Fully-uppercase tokens of >= 3 letters are caps hits with
        exact-token spans."""
        text = "the FAA and the ABC committee met NASA"
        hits = [h for h in self._hits(text) if h['kind'] == 'caps']
        self.assertEqual([h['text'] for h in hits], ['FAA', 'ABC', 'NASA'])
        for hit in hits:
            self.assertEqual(text[hit['span'][0]:hit['span'][1]],
                             hit['text'])

    def test_caps_boundaries(self):
        """Two-letter tokens, digit-dominated tokens and lowercase /
        mixed-case words never count; caps inside bold still do."""
        for text in ("AB ok", "A1B2 ok", "Abc ok", "aBc ok", "MP4 ok"):
            self.assertNotIn('caps', self._kinds(text), text)
        for text in ("ABC", "AB12C", "COVID19"):
            self.assertIn('caps', self._kinds(text), text)

    def test_caps_embedded_in_cjk_and_words(self):
        """The 'SAPP' inside 'iOSAPP' is not a caps run (no word
        boundary), and CJK text around a caps token does not hide it."""
        self.assertEqual(self._kinds("iOSAPP"), [])
        hits = [h for h in self._hits("很重要ABC的内容") if h['kind'] == 'caps']
        self.assertEqual([h['text'] for h in hits], ['ABC'])

    def test_caps_allowlist_filters(self):
        """Default empty allowlist reports everything; configured
        entries (case-insensitive) are exempt."""
        text = "NASA and the FAA use GPS"
        self.assertEqual(
            [h['text'] for h in self._hits(text) if h['kind'] == 'caps'],
            ['NASA', 'FAA', 'GPS'])

        self.detector.caps_allowlist = ['NASA', 'gps']
        self.assertEqual(
            [h['text'] for h in self._hits(text) if h['kind'] == 'caps'],
            ['FAA'])

    def test_caps_allowlist_case_insensitive_via_process_docs(self):
        """Entries set directly on the attribute (not only via the
        configer) are normalized case-insensitively on the public
        process path too (regression: they used to match
        case-sensitively there)."""
        text = "NASA and GPS and FAA met"
        detector = EmphasisMarkerDetector()
        detector.caps_allowlist = ['nasa', 'Gps']
        doc = _doc(text)
        detector.process_docs([doc], self.query)
        self.assertEqual(
            [h['text'] for h in doc.metadata['emphasis']
             if h['kind'] == 'caps'],
            ['FAA'])
        self.assertEqual(doc.metadata['emphasis_counts']['caps'], 1)

    def test_caps_underscore_boundaries_report_both_fragments(self):
        """Underscores act as token boundaries for caps detection, so
        both fragments of 'FOO_BAR' report, and the caps run inside
        '__IMPORTANT__' overlaps its bold hit exactly as the asterisk
        spelling does (regression: '_' used to silence the adjacent
        token)."""
        self.assertEqual(
            [(h['kind'], h['text']) for h in self._hits("FOO_BAR")],
            [('caps', 'FOO'), ('caps', 'BAR')])
        self.assertEqual(
            [(h['kind'], h['text']) for h in self._hits("__IMPORTANT__")],
            [('bold', 'IMPORTANT'), ('caps', 'IMPORTANT')])

    def test_caps_overlaps_marker_hits(self):
        """**IMPORTANT** yields both a bold hit and a caps hit."""
        hits = self._hits("**IMPORTANT**")
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', 'IMPORTANT'), ('caps', 'IMPORTANT')])

    # ========== Highlight ==========

    def test_double_equals_highlight(self):
        text = "this is ==very important== indeed"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('highlight', 'very important')])
        self.assertEqual(text[hits[0]['span'][0]:hits[0]['span'][1]],
                         '==very important==')

    def test_highlight_intraword_and_padding(self):
        """'=' has no intraword guard (like '*'), and padded '== x =='
        never matches."""
        hits = self._hits("x==y==z")
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('highlight', 'y')])
        self.assertEqual(self._hits("== padded =="), [])

    # ========== Span invariants ==========

    def test_span_invariants_on_composite_document(self):
        """For every hit of a composite document the span reconstructs
        the construct: markers + text + markers for marker kinds, the
        exact token for caps; spans are sorted and stay in bounds."""
        text = ("# Notes\n"
                "The **launch date** and *budget* are ==final==.\n"
                "FYI the FAA and NASA approved Q3.\n"
                "```txt\n"
                "**ignored** IGNORED\n"
                "```\n"
                "_lastly_ snake_case_stays_plain __init__ too\n")
        hits = self._hits(text)
        self.assertGreater(len(hits), 5)
        last_start = -1
        for hit in hits:
            start, end = hit['span']
            self.assertTrue(0 <= start < end <= len(text), hit)
            self.assertGreaterEqual(start, last_start)
            last_start = start
            raw = text[start:end]
            if hit['kind'] == 'caps':
                self.assertEqual(raw, hit['text'])
                continue
            width = 1 if hit['kind'] == 'italic' else 2
            self.assertEqual(raw[width:-width], hit['text'])
            if hit['kind'] == 'bold':
                self.assertIn(raw[:2], ('**', '__'))
                self.assertEqual(raw[:2], raw[-2:])
            elif hit['kind'] == 'highlight':
                self.assertEqual(raw[:2], '==')
            else:  # italic: single-character markers
                self.assertIn(raw[0], '*_')
                self.assertEqual(raw[0], raw[-1])
                self.assertNotIn(raw[:2], ('**', '__'))

    # ========== Metadata stamping ==========

    def test_metadata_stamped_with_hits_counts_terms(self):
        """One document collects the hit list, per-kind counts and the
        deduplicated first-occurrence terms."""
        text = ("**alpha** then *beta* then **alpha** then ==gamma== "
                "then BOLDNESS then **alpha**")
        doc = _doc(text)
        result = self.detector.process_docs([doc], self.query)

        self.assertIs(result[0], doc)
        emphasis = doc.metadata['emphasis']
        self.assertTrue(all(
            set(h) == {'kind', 'text', 'span'} for h in emphasis))
        self.assertEqual([h['text'] for h in emphasis],
                         ['alpha', 'beta', 'alpha', 'gamma', 'BOLDNESS',
                          'alpha'])
        self.assertEqual(doc.metadata['emphasis_counts'],
                         {'bold': 3, 'italic': 1, 'highlight': 1,
                          'caps': 1})
        self.assertEqual(doc.metadata['emphasis_terms'],
                         ['alpha', 'beta', 'gamma', 'BOLDNESS'])

    def test_counts_only_include_kinds_present(self):
        doc = _doc("just *one* italic")
        self.detector.process_docs([doc], self.query)
        self.assertEqual(doc.metadata['emphasis_counts'], {'italic': 1})

    def test_capping_behavior(self):
        """150 constructs stamp exactly max_hits hits, counts derived
        from the capped list, and terms capped at max_terms."""
        text = " ".join("**term%d**" % i for i in range(150))
        doc = _doc(text)
        self.detector.process_docs([doc], self.query)

        self.assertEqual(len(doc.metadata['emphasis']), 100)
        self.assertEqual(doc.metadata['emphasis_counts'], {'bold': 100})
        self.assertEqual(len(doc.metadata['emphasis_terms']), 20)
        # The kept hits are the span-first 100 bold constructs.
        self.assertEqual(doc.metadata['emphasis'][0]['text'], 'term0')
        self.assertEqual(doc.metadata['emphasis'][-1]['text'], 'term99')
        self.assertEqual(doc.metadata['emphasis_terms'][0], 'term0')
        self.assertEqual(doc.metadata['emphasis_terms'][-1], 'term19')

    def test_custom_caps_agree_with_hits(self):
        """max_hits/max_terms are real knobs and keep the three stamps
        consistent with each other."""
        text = "**one** *two* ==three== FOUR **five**"
        self.detector.max_hits = 2
        self.detector.max_terms = 1
        doc = _doc(text)
        self.detector.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata['emphasis']), 2)
        self.assertEqual(doc.metadata['emphasis_counts'],
                         {'bold': 1, 'italic': 1})
        self.assertEqual(doc.metadata['emphasis_terms'], ['one'])

    def test_disabled_keys_stamp_nothing(self):
        """Empty key strings disable the individual stamps."""
        text = "**kept or not**"
        self.detector.emphasis_key = ''
        self.detector.counts_key = ''
        self.detector.terms_key = ''
        doc = _doc(text, source="wire")
        self.detector.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {"source": "wire"})

    def test_no_emphasis_passthrough(self):
        """Plain documents come back untouched: metadata stays None,
        text and id intact, order preserved; empty batch in, empty out."""
        plain = _doc("just a plain sentence with nothing to see")
        other = _doc("also plain", rank=2)
        self.assertEqual(self.detector.process_docs([], self.query), [])

        result = self.detector.process_docs([plain, other], self.query)
        self.assertEqual([d.text for d in result], [plain.text, other.text])
        self.assertIs(result[0], plain)
        self.assertIsNone(plain.metadata)
        self.assertEqual(other.metadata, {"rank": 2})

    def test_input_documents_not_corrupted(self):
        """Text/id untouched; pre-existing metadata survives; stamping
        writes through a copy rather than mutating the original
        mapping."""
        doc = _doc("**bold** plus CAPS", source="wire", rank=1)
        meta_ref = doc.metadata
        result = self.detector.process_docs([doc], self.query)

        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, "**bold** plus CAPS")
        self.assertEqual(doc.id, _doc("**bold** plus CAPS").id)
        self.assertEqual(doc.metadata["source"], "wire")
        self.assertEqual(doc.metadata["rank"], 1)
        self.assertNotIn("emphasis", meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_each_document_in_batch_scanned_independently(self):
        """A batch of mixed documents is stamped per document in order;
        blank / None texts are tolerated."""
        docs = [
            _doc("**first**"),
            _doc("plain"),
            _doc("*third* and ==fourth=="),
            _doc(""),
            Document(id='none-text', text=None),
        ]
        result = self.detector.process_docs(docs, self.query)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].metadata['emphasis_terms'], ['first'])
        self.assertEqual(result[1].metadata, None)
        self.assertEqual(result[2].metadata['emphasis_counts'],
                         {'italic': 1, 'highlight': 1})
        self.assertEqual(result[3].metadata, None)
        self.assertEqual(result[4].metadata, None)

    # ========== CJK and determinism ==========

    def test_cjk_emphasis_via_markers(self):
        """Markers apply to CJK text; caps detection is not applicable
        (no case), and CJK boundaries do not hide ASCII caps runs."""
        text = "**重要提示** 和 ==高亮内容== 与 *斜体*"
        hits = self._hits(text)
        self.assertEqual([(h['kind'], h['text']) for h in hits],
                         [('bold', '重要提示'), ('highlight', '高亮内容'),
                          ('italic', '斜体')])
        for hit in hits:
            raw = text[hit['span'][0]:hit['span'][1]]
            self.assertEqual(raw[1:-1] if hit['kind'] == 'italic'
                             else raw[2:-2], hit['text'])

    def test_determinism(self):
        """Repeated scans and repeated batch processing produce
        byte-identical metadata."""
        text = ("**b** *i* ==h== CAPS snake_case `no` [x](y)\n"
                "```py\n**fenced**\n```\n__more b__ WORDS")
        first = EmphasisMarkerDetector()
        second = EmphasisMarkerDetector()
        d1, d2 = _doc(text), _doc(text)
        first.process_docs([d1], self.query)
        second.process_docs([d2], self.query)
        self.assertEqual(d1.metadata, d2.metadata)
        self.assertEqual(self._hits(text), self._hits(text))

    def test_query_is_unused(self):
        """Processing works with and without a query object and gives
        the same stamps."""
        text = "**same** result"
        with_q = _doc(text)
        without_q = _doc(text)
        self.detector.process_docs([with_q], self.query)
        self.detector.process_docs([without_q])
        self.assertEqual(with_q.metadata, without_q.metadata)


if __name__ == '__main__':
    unittest.main()

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2026/10/19
# @FileName: test_text_normalizer.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.text_normalizer import TextNormalizer
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A pure-CJK paragraph without any ASCII/fullwidth-ASCII ambiguity: the
# whitespace operation must return it byte-identical.
CJK_TEXT = (
    "人工智能正在改变世界。机器学习、深度学习与《自然语言处理》等领域的"
    "发展尤为迅速；然而，真正的挑战在于落地。"
)

# A deliberately messy multi-source document exercising every operation
# at once (fullwidth letters/digits/punctuation, a combining accent,
# curly quotes, an em dash, a NUL byte, a non-breaking space, CRLF line
# endings, a run of blank lines, ideographic spaces and two URLs).
KITCHEN_SINK = (
    "ＡＢＣ：ｆｕｌｌｗｉｄｔｈ　１２３\r\n"
    "cafe\u0301 “quoted” — with \x00control\u00a0inside\r\n"
    "\r\n"
    "\r\n"
    "\r\n"
    "See https://example.com/a?b=1, or www.example.org/x.\r\n"
    "　tail　line　\n"
)

# Hand-computed result of running every operation on KITCHEN_SINK with
# lowercase on, url_masking on, max_blank_lines 1 and token '[URL]'
# (lowercased to '[url]' on insertion because lowercase is on).
KITCHEN_SINK_EXPECTED = (
    "abc:fullwidth 123\n"
    "caf\u00e9 \"quoted\" - with control inside\n"
    "\n"
    "see [url], or [url].\n"
    "tail line"
)

# Result of the default configuration (no lowercase, no url_masking).
KITCHEN_SINK_DEFAULT_EXPECTED = (
    "ABC:fullwidth 123\n"
    "caf\u00e9 \"quoted\" - with control inside\n"
    "\n"
    "See https://example.com/a?b=1, or www.example.org/x.\n"
    "tail line"
)


def _doc(text, **metadata):
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _configer(config_dict):
    """Create a ComponentConfiger from a plain dictionary."""
    cfg = Configer()
    cfg.value = config_dict
    configer = ComponentConfiger()
    configer.load_by_configer(cfg)
    return configer


def _make(**overrides):
    """Build a TextNormalizer with only the given operations enabled.

    All operations are disabled first so each test pins exactly one
    behavior; `unicode_normalization` is disabled via the empty string.
    """
    normalizer = TextNormalizer()
    normalizer.unicode_normalization = ''
    normalizer.fullwidth_to_ascii = False
    normalizer.smart_quotes = False
    normalizer.strip_control_chars = False
    normalizer.whitespace = False
    normalizer.lowercase = False
    normalizer.url_masking = False
    for key, value in overrides.items():
        setattr(normalizer, key, value)
    return normalizer


class TestTextNormalizer(unittest.TestCase):
    """Comprehensive offline test suite for TextNormalizer."""

    def setUp(self):
        self.normalizer = TextNormalizer()
        self.query = Query(query_str="normalization")

    def _one(self, text, **overrides):
        docs = _make(**overrides).process_docs([_doc(text)], self.query)
        return docs[0].text

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: NFC form; width/quotes/controls/whitespace on;
        case and URL masking off; one blank line; '[URL]' token;
        'normalization_applied' metadata key."""
        n = TextNormalizer()
        self.assertEqual(n.unicode_normalization, 'NFC')
        self.assertTrue(n.fullwidth_to_ascii)
        self.assertTrue(n.smart_quotes)
        self.assertTrue(n.strip_control_chars)
        self.assertTrue(n.whitespace)
        self.assertEqual(n.max_blank_lines, 1)
        self.assertFalse(n.lowercase)
        self.assertFalse(n.url_masking)
        self.assertEqual(n.url_mask_token, '[URL]')
        self.assertEqual(n.applied_key, 'normalization_applied')

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        n = TextNormalizer()
        n._initialize_by_component_configer(_configer({
            'name': 'text_normalizer',
            'description': 'text normalizer',
            'unicode_normalization': 'NFKC',
            'fullwidth_to_ascii': False,
            'smart_quotes': False,
            'strip_control_chars': False,
            'whitespace': False,
            'max_blank_lines': 2,
            'lowercase': True,
            'url_masking': True,
            'url_mask_token': '<LINK>',
            'applied_key': 'ops',
        }))
        self.assertEqual(n.unicode_normalization, 'NFKC')
        self.assertFalse(n.fullwidth_to_ascii)
        self.assertFalse(n.smart_quotes)
        self.assertFalse(n.strip_control_chars)
        self.assertFalse(n.whitespace)
        self.assertEqual(n.max_blank_lines, 2)
        self.assertTrue(n.lowercase)
        self.assertTrue(n.url_masking)
        self.assertEqual(n.url_mask_token, '<LINK>')
        self.assertEqual(n.applied_key, 'ops')
        self.assertEqual(n.name, 'text_normalizer')

    def test_unicode_normalization_case_insensitive_and_empty(self):
        """Lower-case forms are canonicalized; '' disables; None keeps
        the default."""
        n = TextNormalizer()
        n._initialize_by_component_configer(_configer({
            'name': 'n', 'description': 'd',
            'unicode_normalization': ' nfc ',
        }))
        self.assertEqual(n.unicode_normalization, 'NFC')

        n._initialize_by_component_configer(_configer({
            'name': 'n', 'description': 'd',
            'unicode_normalization': '',
        }))
        self.assertEqual(n.unicode_normalization, '')

        # An absent key leaves a fresh instance's default untouched.
        fresh = TextNormalizer()
        fresh._initialize_by_component_configer(_configer({
            'name': 'n', 'description': 'd',
        }))
        self.assertEqual(fresh.unicode_normalization, 'NFC')

    def test_invalid_configuration_raises(self):
        """Bad normalization forms, negative/non-integer blank-line
        limits, empty/non-string URL tokens and non-string applied keys
        all fail at load time."""
        base = {
            'name': 'n', 'description': 'd',
            'unicode_normalization': 'NFC', 'max_blank_lines': 1,
            'url_mask_token': '[URL]', 'applied_key': 'applied',
        }
        for key, value in (
            ('unicode_normalization', 'NFK'),
            ('unicode_normalization', 'nonsense'),
            ('unicode_normalization', 5),
            ('max_blank_lines', -1),
            ('max_blank_lines', 1.5),
            ('max_blank_lines', True),
            ('url_mask_token', ''),
            ('url_mask_token', 7),
            ('applied_key', ['k']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                TextNormalizer()._initialize_by_component_configer(
                    _configer(config))

    # ========== unicode_normalization tests ==========

    def test_nfc_folds_combining_characters(self):
        """NFC composes `e` + U+0301 into the precomposed `é`."""
        self.assertEqual(self._one("cafe\u0301",
                                   unicode_normalization='NFC'),
                         "caf\u00e9")
        self.assertNotIn('\u0301',
                         self._one("cafe\u0301",
                                   unicode_normalization='NFC'))

    def test_nfd_decomposes_precomposed_characters(self):
        """NFD splits `é` back into `e` + U+0301 (length grows by 1)."""
        self.assertEqual(self._one("caf\u00e9",
                                   unicode_normalization='NFD'),
                         "cafe\u0301")

    def test_nfkc_folds_compatibility_forms(self):
        """NFKC folds ligatures, circled digits and roman numerals."""
        out = self._one("\ufb01nish ① Ⅻ", unicode_normalization='NFKC')
        self.assertEqual(out, "finish 1 XII")

    def test_normalization_disabled_leaves_decomposed_text(self):
        """An empty form leaves combining sequences untouched."""
        text = "cafe\u0301"
        self.assertEqual(self._one(text, unicode_normalization=''),
                         text)

    def test_cjk_text_unchanged_by_nfc(self):
        """NFC is a no-op for (already composed) CJK text."""
        self.assertEqual(self._one(CJK_TEXT, unicode_normalization='NFC'),
                         CJK_TEXT)

    # ========== fullwidth_to_ascii tests ==========

    def test_fullwidth_ascii_letters_and_digits_folded(self):
        """ＡＢＣ１２３ fold onto ABC123."""
        self.assertEqual(self._one("ＡＢＣ　１２３",
                                   fullwidth_to_ascii=True),
                         "ABC 123")

    def test_fullwidth_punctuation_folded(self):
        """Fullwidth ：，！？～ map onto their ASCII counterparts."""
        self.assertEqual(self._one("Ａ：Ｂ，Ｃ！Ｄ？Ｅ～",
                                   fullwidth_to_ascii=True),
                         "A:B,C!D?E~")

    def test_fullwidth_mixed_cjk_latin(self):
        """A mixed Chinese sentence keeps its CJK ideographs while the
        embedded fullwidth Latin/digits fold."""
        self.assertEqual(self._one("第１章　Ｓｔａｒｔ",
                                   fullwidth_to_ascii=True),
                         "第1章 Start")

    def test_cjk_ideographs_and_punctuation_survive_fullwidth_folding(self):
        """。、《》 and CJK ideographs have no ASCII counterpart and are
        untouched; halfwidth katakana are likewise preserved."""
        text = "你好。、《》ｱｲｳ"
        self.assertEqual(self._one(text, fullwidth_to_ascii=True), text)

    def test_ideographic_space_becomes_plain_space(self):
        """U+3000 folds to a plain space even with whitespace off."""
        self.assertEqual(self._one("ａ\u3000ｂ", fullwidth_to_ascii=True),
                         "a b")

    # ========== smart_quotes tests ==========

    def test_smart_quote_and_dash_variants_replaced(self):
        """Every mapped curly quote / low quote / dash goes ASCII."""
        self.assertEqual(
            self._one("“a” ‘b’ ‚c ‛d „e ‟f –g—h―i",
                      smart_quotes=True),
            '"a" \'b\' ,c \'d "e "f -g-h-i')

    def test_minus_sign_and_ellipsis_preserved(self):
        """U+2212 (minus) and U+2026 (ellipsis) are deliberately not
        folded — formulas and prose must survive."""
        text = "3 − 2 = 1 … and more"
        self.assertEqual(self._one(text, smart_quotes=True), text)

    def test_smart_quotes_do_not_touch_cjk(self):
        """CJK text (which uses 「」‘’ legitimately) — the mapped code
        points are absent from pure CJK prose, so it round-trips."""
        self.assertEqual(self._one(CJK_TEXT, smart_quotes=True), CJK_TEXT)

    # ========== strip_control_chars tests ==========

    def test_control_characters_removed(self):
        """NUL, other C0 bytes, DEL and C1 bytes disappear."""
        self.assertEqual(
            self._one("a\x00b\x01c\x1fd\x7fe\x80f\x9fg",
                      strip_control_chars=True),
            "abcdefg")

    def test_newline_and_tab_survive(self):
        """\\n and \\t are exempt from control stripping."""
        self.assertEqual(self._one("a\nb\tc", strip_control_chars=True),
                         "a\nb\tc")

    def test_carriage_return_removed_from_crlf(self):
        """\\r is Cc and removed, so CRLF collapses to LF even when the
        whitespace operation is disabled."""
        self.assertEqual(self._one("x\r\ny\rz", strip_control_chars=True),
                         "x\nyz")

    def test_control_char_inside_word(self):
        """A NUL splitting a word is silently dropped."""
        self.assertEqual(self._one("co\x00ntrol", strip_control_chars=True),
                         "control")

    # ========== whitespace tests ==========

    def test_space_runs_collapse(self):
        """Runs of spaces collapse to a single space."""
        self.assertEqual(self._one("a  b   c    d", whitespace=True),
                         "a b c d")

    def test_line_edges_stripped(self):
        """Leading/trailing spaces vanish per line."""
        self.assertEqual(self._one("  a  \n  b  ", whitespace=True),
                         "a\nb")

    def test_blank_line_runs_capped_by_default(self):
        """Three blank lines collapse to one under max_blank_lines=1."""
        self.assertEqual(self._one("a\n\n\n\nb", whitespace=True),
                         "a\n\nb")

    def test_max_blank_lines_zero_and_custom(self):
        """0 removes blank lines entirely; 2 keeps up to two."""
        self.assertEqual(
            self._one("a\n\n\n\n\nb", whitespace=True, max_blank_lines=0),
            "a\nb")
        self.assertEqual(
            self._one("a\n\n\n\n\nb", whitespace=True, max_blank_lines=2),
            "a\n\n\nb")

    def test_leading_and_trailing_blank_lines_dropped(self):
        """Whole-document blank margins disappear."""
        self.assertEqual(self._one("\n\n  hi  \n\n", whitespace=True),
                         "hi")

    def test_crlf_and_cr_become_lf(self):
        """CRLF and lone CR both canonicalize to LF."""
        self.assertEqual(self._one("a\r\nb\rc", whitespace=True),
                         "a\nb\nc")

    def test_tabs_and_unicode_spaces_become_plain_spaces(self):
        """Tabs, vertical tab, NBSP and U+3000 become plain spaces and
        collapse; nothing else changes."""
        self.assertEqual(
            self._one("x\t\ty\u00a0\u00a0z\u3000w\u000bv", whitespace=True),
            "x y z w v")

    def test_cjk_text_untouched_by_whitespace(self):
        """Pure CJK prose — ideographs, 。、《》 fullwidth colon and all —
        passes the whitespace operation byte-identical."""
        text = "第一条：本合同自签订之日起生效。第二条、甲方权利：《总则》。"
        self.assertEqual(self._one(text, whitespace=True), text)
        self.assertEqual(self._one(CJK_TEXT, whitespace=True), CJK_TEXT)

    def test_cjk_text_with_spaces_keeps_single_spaces(self):
        """Single intentional spaces between CJK words survive; only
        runs collapse."""
        self.assertEqual(self._one("你好  世界 Ａ Ｂ", whitespace=True),
                         "你好 世界 Ａ Ｂ")

    def test_empty_and_whitespace_only_text(self):
        """Whitespace-only input reduces to the empty string."""
        self.assertEqual(self._one(" \n\t \r\n  ", whitespace=True), "")

    # ========== lowercase tests ==========

    def test_lowercase_folds(self):
        """Lowercase folds Latin including accented code points."""
        self.assertEqual(self._one("Hello WÖRLD École",
                                   lowercase=True),
                         "hello wörld école")

    def test_lowercase_off_by_default(self):
        """Case is preserved unless explicitly enabled."""
        self.assertEqual(self._one("AbC dEf", lowercase=False),
                         "AbC dEf")

    def test_lowercase_leaves_cjk_untouched(self):
        """CJK ideographs have no case and pass through."""
        self.assertEqual(self._one(CJK_TEXT, lowercase=True), CJK_TEXT)

    # ========== url_masking tests ==========

    def test_http_and_www_urls_masked(self):
        """Both scheme and www. forms are replaced by the token."""
        self.assertEqual(
            self._one("Visit https://example.com/a?b=1 for details, "
                      "or see www.example.org/x.",
                      url_masking=True),
            "Visit [URL] for details, or see [URL].")

    def test_trailing_punctuation_preserved_after_token(self):
        """Sentence punctuation clinging to the URL stays outside the
        mask, including closing parens and quotes."""
        self.assertEqual(
            self._one("See (https://x.co/a) now.", url_masking=True),
            "See ([URL]) now.")
        self.assertEqual(
            self._one('Go to "http://a.b/c," ok', url_masking=True),
            'Go to "[URL]," ok')

    def test_bare_domains_and_mailto_untouched(self):
        """Without a scheme or www. host nothing is masked."""
        text = "email me at x@y.z via example.com, not mailto:a@b.c"
        self.assertEqual(self._one(text, url_masking=True), text)

    def test_custom_mask_token(self):
        """The replacement token is configurable."""
        self.assertEqual(
            self._one("go https://a.io/x now", url_masking=True,
                      url_mask_token='<LINK>'),
            "go <LINK> now")

    def test_mask_token_lowercased_when_lowercase_enabled(self):
        """With lowercase on, the token is inserted already lowercased so
        a second normalization pass cannot alter it."""
        self.assertEqual(
            self._one("go https://a.io/x now", url_masking=True,
                      lowercase=True),
            "go [url] now")

    def test_uppercase_scheme_urls_masked(self):
        """Scheme matching is case-insensitive."""
        self.assertEqual(
            self._one("see HTTPS://Example.COM/X.", url_masking=True),
            "see [URL].")

    # ========== operation-order and combination tests ==========

    def test_fullwidth_folding_precedes_url_masking(self):
        """A fullwidth-spelled URL is folded before masking, so it is
        still recognized."""
        self.assertEqual(
            self._one("ｈｔｔｐｓ://ｅｘａｍｐｌｅ.ｃｏｍ/ａ.",
                      fullwidth_to_ascii=True, url_masking=True),
            "[URL].")

    def test_control_stripping_precedes_url_masking(self):
        """A NUL inside a URL is stripped before masking, so the URL is
        still recognized."""
        self.assertEqual(
            self._one("go https://exa\x00mple.com/x now",
                      strip_control_chars=True, url_masking=True),
            "go [URL] now")

    def test_normalization_precedes_smart_quotes(self):
        """NFC first composes accents; quote replacement afterwards
        leaves them intact — the two steps compose cleanly."""
        self.assertEqual(
            self._one("caf\u00e9 “x”", unicode_normalization='NFC',
                      smart_quotes=True),
            'caf\u00e9 "x"')

    def test_all_operations_combined_kitchen_sink(self):
        """Every operation on the messy multi-source document produces
        the hand-computed canonical text."""
        out = self._one(KITCHEN_SINK, unicode_normalization='NFC',
                        fullwidth_to_ascii=True, smart_quotes=True,
                        strip_control_chars=True, whitespace=True,
                        max_blank_lines=1, lowercase=True,
                        url_masking=True)
        self.assertEqual(out, KITCHEN_SINK_EXPECTED)

    def test_default_operations_combined_kitchen_sink(self):
        """The default configuration (no case folding, no URL masking)
        yields the same canonical shape minus those two steps."""
        doc = _doc(KITCHEN_SINK)
        result = TextNormalizer().process_docs([doc], self.query)
        self.assertEqual(result[0].text, KITCHEN_SINK_DEFAULT_EXPECTED)

    def test_processing_is_idempotent(self):
        """Normalizing already-normalized text returns it unchanged."""
        normalizer = _make(unicode_normalization='NFC',
                           fullwidth_to_ascii=True, smart_quotes=True,
                           strip_control_chars=True, whitespace=True,
                           lowercase=True, url_masking=True)
        once = normalizer.process_docs([_doc(KITCHEN_SINK)], self.query)
        # Snapshot before the second pass: the same document objects are
        # normalized in place again below.
        first_pass_text = once[0].text
        self.assertEqual(first_pass_text, KITCHEN_SINK_EXPECTED)
        twice = normalizer.process_docs(once, self.query)
        self.assertEqual(twice[0].text, KITCHEN_SINK_EXPECTED)

    # ========== no-op configuration ==========

    def test_no_ops_leave_text_byte_identical(self):
        """With every operation disabled, even the messiest text comes
        back unchanged and the applied list is empty."""
        normalizer = _make()
        doc = _doc(KITCHEN_SINK)
        result = normalizer.process_docs([doc], self.query)
        self.assertEqual(result[0].text, KITCHEN_SINK)
        self.assertEqual(doc.metadata['normalization_applied'], [])

    def test_clean_text_unchanged_by_defaults(self):
        """Text that is already canonical is a byte-identical no-op
        under the default configuration (applied ops still recorded)."""
        clean = ("First paragraph.\n\n"
                 "Second paragraph with 3 − 2 = 1 … done.")
        doc = _doc(clean)
        result = TextNormalizer().process_docs([doc], self.query)
        self.assertEqual(result[0].text, clean)
        self.assertEqual(doc.metadata['normalization_applied'],
                         ['unicode_normalization', 'fullwidth_to_ascii',
                          'smart_quotes', 'strip_control_chars',
                          'whitespace'])

    # ========== metadata bookkeeping tests ==========

    def test_applied_operations_recorded_in_execution_order(self):
        """metadata[normalization_applied] lists exactly the enabled
        operations in pipeline order."""
        normalizer = _make(lowercase=True, url_masking=True,
                           whitespace=True)
        doc = _doc("Hello https://a.io/x")
        normalizer.process_docs([doc], self.query)
        self.assertEqual(doc.metadata['normalization_applied'],
                         ['whitespace', 'lowercase', 'url_masking'])

    def test_custom_and_disabled_applied_key(self):
        """The stamp key is configurable; an empty key disables
        stamping entirely."""
        normalizer = _make(whitespace=True, applied_key='ops')
        doc = _doc("a  b")
        normalizer.process_docs([doc], self.query)
        self.assertEqual(doc.metadata['ops'], ['whitespace'])

        normalizer.applied_key = ''
        doc = _doc("a  b")
        normalizer.process_docs([doc], self.query)
        self.assertEqual(doc.text, "a b")
        self.assertIsNone(doc.metadata)

    def test_existing_metadata_preserved_and_not_mutated_in_place(self):
        """Pre-existing metadata survives stamping; the stamp goes
        through a copied mapping, so the caller's dict object is never
        edited in place."""
        normalizer = _make(whitespace=True)
        doc = _doc("a  b", source="pdf", page=3)
        meta_ref = doc.metadata
        normalizer.process_docs([doc], self.query)
        self.assertEqual(doc.metadata['source'], "pdf")
        self.assertEqual(doc.metadata['page'], 3)
        self.assertEqual(doc.metadata['normalization_applied'],
                         ['whitespace'])
        self.assertNotIn('normalization_applied', meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_id_preserved_and_documents_returned_in_order(self):
        """Ids are untouched; the same document objects come back in
        batch order."""
        docs = [_doc("a  b"), _doc("Ｃ"), _doc("x\n\n\n\ny")]
        result = TextNormalizer().process_docs(docs, self.query)
        self.assertEqual([d.id for d in result], [d.id for d in docs])
        self.assertIs(result[1], docs[1])
        self.assertEqual([d.text for d in result],
                         ["a b", "C", "x\n\ny"])

    # ========== pipeline-shape tests ==========

    def test_empty_document_list(self):
        """An empty batch yields an empty result."""
        self.assertEqual(
            TextNormalizer().process_docs([], self.query), [])

    def test_empty_and_none_text_documents(self):
        """Empty and None texts normalize to '' and are still
        stamped."""
        empty = _doc("")
        # Document(text=None) cannot be constructed (its id validator
        # hashes the text), so None is assigned post-construction.
        none_text = Document()
        none_text.text = None
        result = TextNormalizer().process_docs([empty, none_text],
                                               self.query)
        self.assertEqual([d.text for d in result], ['', ''])
        for doc in result:
            self.assertEqual(doc.metadata['normalization_applied'],
                             ['unicode_normalization',
                              'fullwidth_to_ascii', 'smart_quotes',
                              'strip_control_chars', 'whitespace'])

    def test_documents_without_metadata_get_stamped(self):
        """Documents constructed with metadata=None receive a fresh
        mapping from the stamp."""
        doc = _doc("ＡＢＣ")
        self.assertIsNone(doc.metadata)
        TextNormalizer().process_docs([doc], self.query)
        self.assertEqual(doc.text, "ABC")
        self.assertEqual(doc.metadata['normalization_applied'],
                         ['unicode_normalization', 'fullwidth_to_ascii',
                          'smart_quotes', 'strip_control_chars',
                          'whitespace'])

    def test_query_is_accepted_but_unused(self):
        """Processing works with and without a Query object."""
        docs = [_doc("a  b")]
        out = _make(whitespace=True).process_docs(docs)
        self.assertEqual(out[0].text, "a b")


if __name__ == '__main__':
    unittest.main()

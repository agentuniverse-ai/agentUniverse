# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_instruction_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.instruction_extractor import (
    InstructionExtractor, _IMPERATIVE_VERB_LIST, _IMPERATIVE_VERBS)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A realistic how-to document mixing prose, a numbered procedure,
# second-person directives, a Chinese instruction, tables, a question and
# a noun-subject declarative.
MIXED_DOC = (
    "# Installation Guide\n"
    "\n"
    "Read this guide before you install the software.\n"
    "\n"
    "1. Download the archive from the portal.\n"
    "2. Extract the files into /opt.\n"
    "3. Run the installer with sudo.\n"
    "\n"
    "You must back up your data first.\n"
    "请输入管理员密码。\n"
    "| Step | Action |\n"
    "| --- | --- |\n"
    "Did the installer finish?\n"
    "The install completed successfully.\n"
)

# A three-step procedure with a prose continuation line (lazy
# continuation of item 1) that carries no verb evidence of its own.
HOWTO_DOC = (
    "To install the tool:\n"
    "1. Download the archive.\n"
    "The download may take a few minutes.\n"
    "2. Extract the files.\n"
    "3. Run the installer.\n"
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestInstructionExtractor(unittest.TestCase):
    """Comprehensive test suite for InstructionExtractor."""

    def setUp(self):
        self.extractor = InstructionExtractor()
        self.query = Query(query_str="installation instructions")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _hits(self, text):
        """Run the default extractor over one document and return hits."""
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        return doc.metadata["instructions"]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 100, min_words 1, threshold 3 and the three
        metadata keys 'instructions' / 'instruction_count' /
        'has_procedure'."""
        e = InstructionExtractor()
        self.assertEqual(e.max_instructions, 100)
        self.assertEqual(e.min_words, 1)
        self.assertEqual(e.procedure_threshold, 3)
        self.assertEqual(e.instructions_key, "instructions")
        self.assertEqual(e.count_key, "instruction_count")
        self.assertEqual(e.has_procedure_key, "has_procedure")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'instruction_extractor',
            'description': 'instruction extractor',
            'max_instructions': 7,
            'min_words': 2,
            'procedure_threshold': 5,
            'instructions_key': 'actions',
            'count_key': 'action_count',
            'has_procedure_key': 'is_procedure',
        })
        e = InstructionExtractor()
        e._initialize_by_component_configer(configer)
        self.assertEqual(e.max_instructions, 7)
        self.assertEqual(e.min_words, 2)
        self.assertEqual(e.procedure_threshold, 5)
        self.assertEqual(e.instructions_key, "actions")
        self.assertEqual(e.count_key, "action_count")
        self.assertEqual(e.has_procedure_key, "is_procedure")
        self.assertEqual(e.name, "instruction_extractor")

    def test_invalid_configuration_raises(self):
        """Out-of-range / mis-typed parameters fail at load time."""
        base = {
            'name': 'e', 'description': 'd',
            'max_instructions': 10, 'min_words': 1,
            'procedure_threshold': 3, 'instructions_key': 'instructions',
            'count_key': 'instruction_count',
            'has_procedure_key': 'has_procedure',
        }
        for key, value in (
            ('max_instructions', -1),
            ('max_instructions', 2.5),
            ('max_instructions', True),
            ('min_words', 0),
            ('min_words', 1.5),
            ('min_words', True),
            ('procedure_threshold', 0),
            ('procedure_threshold', 2.5),
            ('procedure_threshold', False),
            ('instructions_key', 5),
            ('count_key', ['x']),
            ('has_procedure_key', 3.5),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                InstructionExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Verb list tests ==========

    def test_bundled_verb_list_shape(self):
        """The bundled list holds exactly 120 curated imperative verbs,
        has no duplicates, and deliberately excludes the noun 'note'."""
        self.assertEqual(len(_IMPERATIVE_VERB_LIST), 120)
        self.assertEqual(len(_IMPERATIVE_VERBS), 120)
        self.assertNotIn("note", _IMPERATIVE_VERBS)
        for mandated in ("install", "click", "verify", "ensure", "avoid",
                         "configure", "restart", "scroll", "swipe",
                         "disconnect", "launch", "download"):
            self.assertIn(mandated, _IMPERATIVE_VERBS)

    def test_every_bundled_verb_detected(self):
        """Every verb in the list yields exactly one imperative hit when
        opening a sentence followed by an object."""
        for verb in _IMPERATIVE_VERB_LIST:
            text = f"{verb.capitalize()} the target object."
            hits = self._hits(text)
            self.assertEqual(len(hits), 1, verb)
            self.assertEqual(hits[0]["kind"], "imperative", verb)
            self.assertEqual(hits[0]["verb"], verb)
            self.assertEqual(hits[0]["text"], text, verb)

    def test_imperative_matching_is_case_insensitive(self):
        """'install ...', 'INSTALL ...' and quoted '"Click ...' all match."""
        for text, verb in (("install the package.", "install"),
                           ("INSTALL THE PACKAGE.", "install"),
                           ('"Click OK," he said.', "click")):
            hits = self._hits(text)
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "imperative")
            self.assertEqual(hits[0]["verb"], verb)

    def test_imperative_allows_exclamation_termination(self):
        """'!' terminates a sentence but is a command, not a question."""
        hits = self._hits("Click OK!")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["verb"], "click")

    # ========== Past-tense / husk guard tests ==========

    def test_noun_subject_past_tense_rejected(self):
        """'Install completed successfully.' / 'Update failed ...' use the
        verb-form word as a NOUN subject; the -ed next-word heuristic
        rejects them."""
        for text in ("Install completed successfully.",
                     "Update failed on three nodes.",
                     "Deployment started. Install completed."):
            self.assertEqual(self._hits(text), [], text)

    def test_participle_adjective_over_rejection_is_documented(self):
        """The heuristic also rejects 'Install required packages ...' —
        'required' is an adjective, but rejecting is the conservative
        direction and this pins the documented trade-off."""
        self.assertEqual(
            self._hits("Install required packages before upgrading."), [])

    def test_short_ed_words_pass_the_guard(self):
        """'seed' has only two letters before the final 'ed', below the
        three-letter past-tense stem, so 'Add seed keywords ...' is a
        hit while 'speed' (three-letter stem 'spe') is rejected."""
        hits = self._hits("Add seed keywords to the campaign.")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["verb"], "add")
        self.assertEqual(self._hits("Run speed drills today."), [])

    def test_verb_alone_or_ellipsis_husk_rejected(self):
        """A bare 'Install.' and a 'Click...' before an ellipsis split
        leave the verb with no following word — no hit."""
        self.assertEqual(self._hits("Install."), [])
        self.assertEqual(self._hits("Click... OK."), [])

    # ========== Question guard tests ==========

    def test_questions_never_count(self):
        """Terminal '?' excludes a sentence even when it opens with an
        imperative verb, embeds a directive phrase, sits on a numbered
        line, or is Chinese."""
        for text in ("Install this one?",
                     "What should you click?",
                     "1. Did it work?",
                     "请确认了吗？",
                     '"Are you sure you need to proceed?"'):
            self.assertEqual(self._hits(text), [], text)

    # ========== Chinese imperative tests ==========

    def test_zh_imperative_markers(self):
        """Each marker (请/务必/先/然后/接着) yields a zh_imperative hit."""
        for marker, text in (("请", "请输入用户名。"),
                             ("务必", "务必检查网络连接。"),
                             ("先", "先安装依赖包。"),
                             ("然后", "然后重启服务。"),
                             ("接着", "接着点击确定按钮。")):
            hits = self._hits(text)
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "zh_imperative")
            self.assertIsNone(hits[0]["verb"])
            self.assertEqual(hits[0]["text"], text)

    def test_zh_marker_husk_rejected(self):
        """'请。' has no content after the marker — no hit."""
        self.assertEqual(self._hits("请。"), [])

    # ========== Directive tests ==========

    def test_second_person_directives(self):
        """EN 'you must/should/need to' anywhere and ZH 你需要/你必须
        produce directive hits; weaker 'you may' does not."""
        for text in ("You must back up the database first.",
                     "Before you proceed, you should read the guide.",
                     "You need to register the license key.",
                     "你需要先备份数据。",
                     "你必须修改配置文件。"):
            hits = self._hits(text)
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "directive")
            self.assertIsNone(hits[0]["verb"])
        self.assertEqual(self._hits("You may install it later."), [])
        self.assertEqual(self._hits("系统必须每晚运行。"), [])

    def test_imperative_beats_directive_priority(self):
        """Verb evidence outranks an embedded directive phrase."""
        hits = self._hits("Install the package you need to keep.")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["kind"], "imperative")
        self.assertEqual(hits[0]["verb"], "install")

    # ========== Numbered-step context tests ==========

    def test_numbered_procedure_steps(self):
        """A three-item numbered list: each sentence keeps its imperative
        kind, the marker is excluded from the span, and has_procedure is
        True."""
        doc = _doc("1. Download the archive.\n"
                   "2. Extract the files.\n"
                   "3. Run the installer.\n")
        self.extractor.process_docs([doc], self.query)
        hits = doc.metadata["instructions"]
        self.assertEqual([h["kind"] for h in hits],
                         ["imperative"] * 3)
        self.assertEqual([h["verb"] for h in hits],
                         ["download", "extract", "run"])
        for hit in hits:
            self.assertTrue(hit["text"].startswith(("Download", "Extract",
                                                    "Run")))
            self.assertFalse(hit["text"].startswith("1"))
        self.assertTrue(doc.metadata["has_procedure"])

    def test_context_only_step_kind(self):
        """A prose lazy-continuation line after a numbered item carries
        no verb evidence and is flagged kind=step."""
        doc = _doc("1. Open the file and\n"
                   "change the port value.\n"
                   "2. Restart the service.\n")
        self.extractor.process_docs([doc], self.query)
        hits = doc.metadata["instructions"]
        self.assertEqual([h["kind"] for h in hits],
                         ["imperative", "step", "imperative"])
        self.assertEqual(hits[1]["text"], "change the port value.")

    def test_blank_line_ends_step_context(self):
        """A blank line between the item and the following prose ends the
        numbered context (markdown list termination)."""
        doc = _doc("1. Download the archive.\n"
                   "\n"
                   "The download may take a while.\n")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["instructions"]), 1)
        self.assertFalse(doc.metadata["has_procedure"])

    def test_excluded_line_ends_step_context(self):
        """A heading between the item and following prose also breaks the
        numbered context."""
        doc = _doc("1. Download the archive.\n"
                   "# Notes\n"
                   "The archive is signed.\n")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["instructions"]), 1)
        self.assertFalse(doc.metadata["has_procedure"])

    def test_step_husk_with_min_words(self):
        """'1. Run.' yields a one-word step hit at min_words=1; raising
        min_words to 2 drops the segment entirely."""
        doc = _doc("1. Run.\n")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual([h["kind"] for h in doc.metadata["instructions"]],
                         ["step"])

        self.extractor.min_words = 2
        doc = _doc("1. Run.\n")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["instructions"], [])
        self.assertFalse(doc.metadata["has_procedure"])

    def test_marker_without_space_is_not_an_item(self):
        """'1.Install' lacks the space a markdown item needs: the text is
        still segmented and 'Install ...' is found, but without step
        context (so has_procedure stays False)."""
        doc = _doc("1.Install the tool.\n")
        self.extractor.process_docs([doc], self.query)
        hits = doc.metadata["instructions"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["verb"], "install")
        self.assertFalse(doc.metadata["has_procedure"])

    def test_decimal_at_line_start_is_not_a_marker(self):
        """'3.14 is the value of pi.' must not be read as item 3."""
        doc = _doc("3.14 is the value of pi.\n")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["instructions"], [])
        self.assertFalse(doc.metadata["has_procedure"])

    # ========== Heading / table guard tests ==========

    def test_heading_and_table_fragments_excluded(self):
        """Lines starting with '#' or '|' never yield instructions."""
        for text in ("# Install the package now",
                     "## Setup instructions",
                     "| Click | OK | Continue |",
                     "   # indented comment",
                     "| --- | --- |\n| Open | File |"):
            self.assertEqual(self._hits(text), [], text)

    def test_heading_does_not_leak_into_next_sentence(self):
        """'Click OK.' after a heading line is detected on its own; the
        heading fragment is dropped."""
        hits = self._hits("# Install Guide\nClick OK.")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["verb"], "click")
        self.assertEqual(hits[0]["text"], "Click OK.")

    # ========== Declarative guard tests ==========

    def test_declaratives_and_non_verbs_rejected(self):
        """Plain declaratives, 'Note that ...', plural nouns and commands
        softened by 'Please' are not instructions under the four
        channels."""
        for text in ("The install completed without errors.",
                     "It runs every night.",
                     "Updates are available.",
                     "Note that the service restarts nightly.",
                     "Please install the package.",
                     "The wizard closes and the installation is complete."):
            self.assertEqual(self._hits(text), [], text)

    def test_soft_wrapped_sentence_stays_whole(self):
        """A plain-to-plain line break is a soft wrap: one sentence, one
        hit, span crossing the newline."""
        text = "Install the package and\nverify the checksum offline.\n"
        hits = self._hits(text)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["verb"], "install")
        self.assertIn("\n", hits[0]["text"])

    # ========== Metadata bookkeeping tests ==========

    def test_mixed_document_end_to_end(self):
        """The full MIXED_DOC yields the expected ordered hit list with
        counts and the procedure flag."""
        doc = _doc(MIXED_DOC)
        self.extractor.process_docs([doc], self.query)
        hits = doc.metadata["instructions"]
        self.assertEqual([h["kind"] for h in hits],
                         ["imperative", "imperative", "imperative",
                          "imperative", "directive", "zh_imperative"])
        self.assertEqual([h["verb"] for h in hits],
                         ["read", "download", "extract", "run", None, None])
        self.assertEqual(doc.metadata["instruction_count"], 6)
        self.assertTrue(doc.metadata["has_procedure"])

    def test_howto_document_with_continuation(self):
        """The HOWTO_DOC: imperative + context-only step + two
        imperatives; four numbered sentences make a procedure."""
        doc = _doc(HOWTO_DOC)
        self.extractor.process_docs([doc], self.query)
        hits = doc.metadata["instructions"]
        self.assertEqual([h["kind"] for h in hits],
                         ["imperative", "step", "imperative", "imperative"])
        self.assertEqual(doc.metadata["instruction_count"], 4)
        self.assertTrue(doc.metadata["has_procedure"])

    def test_cap_and_uncapped_count(self):
        """130 instruction sentences: the list is capped at 100 while
        instruction_count reports the true 130."""
        text = " ".join(f"Click the button {i}." for i in range(130))
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["instructions"]), 100)
        self.assertEqual(doc.metadata["instruction_count"], 130)
        self.assertEqual(doc.metadata["instructions"][0]["text"],
                         "Click the button 0.")
        self.assertEqual(doc.metadata["instructions"][-1]["text"],
                         "Click the button 99.")
        self.assertFalse(doc.metadata["has_procedure"])

    def test_has_procedure_arithmetic(self):
        """Two numbered sentences fall short of the threshold of 3; three
        reach it even when every sentence is context-only prose."""
        two = _doc("1. The first screen appears.\n"
                   "2. The license page opens.\n")
        self.extractor.process_docs([two], self.query)
        self.assertEqual([h["kind"] for h in two.metadata["instructions"]],
                         ["step", "step"])
        self.assertFalse(two.metadata["has_procedure"])

        three = _doc("1. The first screen appears.\n"
                     "2. The license page opens.\n"
                     "3. The wizard finishes.\n")
        self.extractor.process_docs([three], self.query)
        self.assertTrue(three.metadata["has_procedure"])

        self.extractor.procedure_threshold = 5
        doc = _doc("1. A.\n2. B.\n3. C.\n")
        self.extractor.process_docs([doc], self.query)
        self.assertFalse(doc.metadata["has_procedure"])

    def test_numbered_questions_count_as_steps(self):
        """A question item is excluded from the hits but still counts as
        a numbered sentence for has_procedure."""
        doc = _doc("1. Did it work?\n"
                   "2. Click OK.\n"
                   "3. Press Enter.\n")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual([h["verb"] for h in doc.metadata["instructions"]],
                         ["click", "press"])
        self.assertTrue(doc.metadata["has_procedure"])

    def test_span_invariants(self):
        """Every hit's span slices the original text exactly, spans are
        ordered and non-overlapping, and numbered markers are excluded."""
        doc = _doc(MIXED_DOC)
        self.extractor.process_docs([doc], self.query)
        previous_end = -1
        for hit in doc.metadata["instructions"]:
            start, end = hit["span"]
            self.assertIsInstance(hit["span"], tuple)
            self.assertGreaterEqual(start, 0)
            self.assertLess(start, end)
            self.assertLessEqual(end, len(MIXED_DOC))
            self.assertEqual(MIXED_DOC[start:end], hit["text"])
            self.assertGreater(start, previous_end)
            previous_end = end

    # ========== Pipeline-shape tests ==========

    def test_no_instruction_passthrough(self):
        """Documents without instructions still pass through and receive
        empty stamps; text and id are untouched."""
        text = "The sun rises in the east. Markets fluctuate daily."
        doc = _doc(text, source="almanac")
        doc_id = doc.id
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, text)
        self.assertEqual(doc.id, doc_id)
        self.assertEqual(doc.metadata["source"], "almanac")
        self.assertEqual(doc.metadata["instructions"], [])
        self.assertEqual(doc.metadata["instruction_count"], 0)
        self.assertFalse(doc.metadata["has_procedure"])

    def test_empty_and_none_inputs(self):
        """Empty batch yields an empty list; empty and None texts get
        empty stamps (the None document carries an explicit id because
        Document's default uuid5 id hashing requires a string)."""
        self.assertEqual(self.extractor.process_docs([], self.query), [])
        for text in ("", "   \n  ", None):
            doc = Document(text=text, id="anonymous")
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["instructions"], [])
            self.assertEqual(doc.metadata["instruction_count"], 0)
            self.assertFalse(doc.metadata["has_procedure"])

    def test_input_documents_not_corrupted(self):
        """Pre-existing metadata survives; stamping writes through a copy
        rather than mutating the original mapping."""
        doc = _doc("Click OK.", source="manual", rank=1)
        meta_ref = doc.metadata
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["source"], "manual")
        self.assertEqual(doc.metadata["rank"], 1)
        self.assertNotIn("instructions", meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_disabled_metadata_keys_stamp_nothing(self):
        """Empty key values disable all three stamps."""
        self.extractor.instructions_key = ""
        self.extractor.count_key = ""
        self.extractor.has_procedure_key = ""
        doc = _doc("Click OK.", source="manual")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {"source": "manual"})

    def test_multiple_documents_processed_independently(self):
        """Each document in the batch is analysed on its own text."""
        docs = [_doc("Click OK."), _doc("请输入密码。"),
                _doc("Nothing to see here.")]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].metadata["instruction_count"], 1)
        self.assertEqual(result[1].metadata["instruction_count"], 1)
        self.assertEqual(result[2].metadata["instruction_count"], 0)
        self.assertEqual(result[1].metadata["instructions"][0]["kind"],
                         "zh_imperative")

    def test_deterministic_across_runs_and_instances(self):
        """Two runs and two instances produce identical metadata."""
        first, second = _doc(MIXED_DOC), _doc(MIXED_DOC)
        self.extractor.process_docs([first], self.query)
        InstructionExtractor().process_docs([second], self.query)
        self.assertEqual(first.metadata["instructions"],
                         second.metadata["instructions"])
        self.assertEqual(first.metadata["instruction_count"],
                         second.metadata["instruction_count"])
        self.assertEqual(first.metadata["has_procedure"],
                         second.metadata["has_procedure"])

    def test_trailing_sentence_without_terminal_punctuation(self):
        """A final sentence with no terminal punctuation is still
        analysed."""
        hits = self._hits("Some introduction text.\nClick OK")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["verb"], "click")
        self.assertEqual(hits[0]["text"], "Click OK")


if __name__ == '__main__':
    unittest.main()

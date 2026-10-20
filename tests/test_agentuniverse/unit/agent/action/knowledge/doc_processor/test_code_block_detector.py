# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_code_block_detector.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.code_block_detector import CodeBlockDetector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# One classic backtick block wrapped in prose: 5 lines, block on lines
# 2-4 (3 lines including fences), language "python".
BACKTACK_DOC = "# Intro\n```python\nx = 1\n```\nOutro."

# A tilde block whose interior contains a backtick fence line: the
# backtick line neither closes nor re-opens anything.
TILDE_DOC = "~~~js\n```\ncode();\n~~~\nafter"

# The reverse nesting: backtick block containing a tilde fence line.
NESTED_BACKTICK_DOC = "```python\n~~~\nx\n```"

# Longer-closer rule: a 4-backtick opener is not closed by a 3-backtick
# line but is closed by another 4-backtick (or longer) line.
LONGER_CLOSER_DOC = "````text\n```\ninner\n````\ntail"
LONGER_THAN_OPENER_DOC = "```py\ncode\n`````\ntail"

# A same-char line carrying info text is not a closing fence.
CLOSER_WITH_INFO_DOC = "```python\nx\n```not-a-closer\n```\ntail"


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestCodeBlockDetector(unittest.TestCase):
    """Comprehensive test suite for CodeBlockDetector."""

    def setUp(self):
        self.detector = CodeBlockDetector()
        self.query = Query(query_str="code blocks")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _summary(self, text: str, detector: CodeBlockDetector = None) -> dict:
        """Run detection over one text document, return the summary."""
        detector = detector or self.detector
        doc = _doc(text)
        detector.process_docs([doc], self.query)
        return doc.metadata["code_blocks"]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: mask off, cap 50, metadata key 'code_blocks'."""
        d = CodeBlockDetector()
        self.assertFalse(d.mask)
        self.assertEqual(d.max_blocks, 50)
        self.assertEqual(d.metadata_key, "code_blocks")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'code_block_detector',
            'description': 'code block detector',
            'mask': True,
            'max_blocks': 10,
            'metadata_key': 'fences',
        })
        d = CodeBlockDetector()
        d._initialize_by_component_configer(configer)
        self.assertTrue(d.mask)
        self.assertEqual(d.max_blocks, 10)
        self.assertEqual(d.metadata_key, "fences")
        self.assertEqual(d.name, "code_block_detector")

    def test_invalid_configuration_raises(self):
        """Non-bool mask, non-int or <1 max_blocks and non-string
        metadata_key all fail at load time."""
        base = {
            'name': 'd', 'description': 'd',
            'mask': False, 'max_blocks': 50,
            'metadata_key': 'code_blocks',
        }
        for key, value in (
            ('mask', 'yes'),
            ('mask', 1),
            ('max_blocks', 0),
            ('max_blocks', -3),
            ('max_blocks', 2.5),
            ('max_blocks', True),
            ('metadata_key', 5),
            ('metadata_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                CodeBlockDetector()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Opener parsing tests ==========

    def test_backtick_block_detected(self):
        """Classic fenced block: language, span, count, aggregates."""
        summary = self._summary(BACKTACK_DOC)
        self.assertEqual(summary["blocks"], [{
            "language": "python", "span": [2, 4], "line_count": 3,
            "unclosed": False, "indent": 0,
        }])
        self.assertEqual(summary["block_count"], 1)
        self.assertEqual(summary["total_code_lines"], 3)
        self.assertEqual(summary["languages"], {"python": 1})
        self.assertEqual(summary["longest_block_lines"], 3)
        self.assertEqual(summary["code_ratio"], 3 / 5)

    def test_tilde_block_and_mixed_fences_do_not_close(self):
        """A backtick fence line inside a tilde block is content; only a
        same-char, long-enough closer ends the block."""
        summary = self._summary(TILDE_DOC)
        self.assertEqual(summary["block_count"], 1)
        self.assertEqual(summary["blocks"][0]["language"], "js")
        self.assertEqual(summary["blocks"][0]["span"], [1, 4])
        self.assertEqual(summary["blocks"][0]["line_count"], 4)

    def test_nested_tilde_inside_backtick_block(self):
        """The reverse nesting: a tilde fence stays inside a backtick
        block."""
        summary = self._summary(NESTED_BACKTICK_DOC)
        self.assertEqual(summary["block_count"], 1)
        self.assertEqual(summary["blocks"][0]["span"], [1, 4])
        self.assertEqual(summary["blocks"][0]["unclosed"], False)

    def test_info_string_parsing(self):
        """Language is the lowercased first word of the info string;
        absent info yields ''."""
        cases = {
            "```Python\nx\n```": "python",
            "```  python  extra words  \nx\n```": "python",
            "```\nx\n```": "",
            "~~~ C++ \nx\n~~~": "c++",
            "```JS\nx\n```": "js",
        }
        for text, language in cases.items():
            summary = self._summary(text)
            self.assertEqual(summary["blocks"][0]["language"], language,
                             text)
            self.assertEqual(summary["block_count"], 1, text)

    def test_backtick_in_backtick_info_string_is_not_a_fence(self):
        """Per CommonMark a backtick opener whose info string contains a
        backtick is plain text, not a fence at all."""
        text = "before\n``` not ```ok\nafter"
        summary = self._summary(text)
        self.assertEqual(summary["block_count"], 0)
        self.assertEqual(summary["blocks"], [])

    def test_short_runs_are_not_fences(self):
        """Runs shorter than 3 characters never open a fence."""
        for text in ("``python\nx", "~~\nx", "before\n`\nafter"):
            summary = self._summary(text)
            self.assertEqual(summary["block_count"], 0, text)

    # ========== Closing rule tests ==========

    def test_longer_opener_requires_equally_long_closer(self):
        """A 4-backtick opener is not closed by a 3-backtick line."""
        summary = self._summary(LONGER_CLOSER_DOC)
        self.assertEqual(summary["block_count"], 1)
        self.assertEqual(summary["blocks"][0]["span"], [1, 4])
        self.assertEqual(summary["blocks"][0]["language"], "text")
        self.assertEqual(summary["total_code_lines"], 4)

    def test_closer_may_be_longer_than_opener(self):
        """A closing fence of 5 backticks closes a 3-backtick block."""
        summary = self._summary(LONGER_THAN_OPENER_DOC)
        self.assertEqual(summary["blocks"][0]["span"], [1, 3])
        self.assertEqual(summary["blocks"][0]["unclosed"], False)

    def test_closer_with_info_text_does_not_close(self):
        """A same-char line carrying info text is content, not a closer."""
        summary = self._summary(CLOSER_WITH_INFO_DOC)
        self.assertEqual(summary["blocks"][0]["span"], [1, 4])

    def test_closer_trailing_spaces_allowed(self):
        """Trailing whitespace after the closing fence run is fine."""
        text = "```python\nx\n```   \ntail"
        summary = self._summary(text)
        self.assertEqual(summary["blocks"][0]["span"], [1, 3])

    # ========== Indentation tests ==========

    def test_indented_fences_supported(self):
        """Openers indented by up to 3 spaces are fences; the indent is
        reported and the closer may carry its own 0-3 space indent."""
        text = "   ```js\nx\n    ```\n~~~\n  ```\nt"
        summary = self._summary(text)
        self.assertEqual(summary["block_count"], 1)
        self.assertEqual(summary["blocks"][0]["indent"], 3)
        self.assertEqual(summary["blocks"][0]["span"], [1, 5])

    def test_four_space_indent_is_not_a_fence(self):
        """4+ spaces of indentation makes a fence line plain content (it
        would be an indented code block in CommonMark, out of scope)."""
        text = "    ```python\nx\n    ```\nafter"
        summary = self._summary(text)
        self.assertEqual(summary["block_count"], 0)

    # ========== Unclosed fences ==========

    def test_unclosed_fence_runs_to_eof(self):
        """A fence left open consumes the rest of the document and is
        flagged unclosed."""
        text = "intro\n```python\nx = 1\ny = 2"
        summary = self._summary(text)
        self.assertEqual(summary["blocks"], [{
            "language": "python", "span": [2, 4], "line_count": 3,
            "unclosed": True, "indent": 0,
        }])
        self.assertEqual(summary["code_ratio"], 3 / 4)

    def test_unclosed_bare_fence_at_eof(self):
        """A lone trailing fence line is a one-line unclosed block."""
        summary = self._summary("```")
        self.assertEqual(summary["blocks"][0]["span"], [1, 1])
        self.assertEqual(summary["blocks"][0]["line_count"], 1)
        self.assertTrue(summary["blocks"][0]["unclosed"])
        self.assertEqual(summary["block_count"], 1)

    def test_unclosed_fence_hides_later_openers(self):
        """Everything after an unclosed opener — including other fence
        lines — is content of the unclosed block."""
        text = "~~~\nx\n```python\ny\n```"
        summary = self._summary(text)
        self.assertEqual(summary["block_count"], 1)
        self.assertTrue(summary["blocks"][0]["unclosed"])
        self.assertEqual(summary["blocks"][0]["span"], [1, 5])

    # ========== Aggregates ==========

    def test_sequential_blocks(self):
        """Two adjacent blocks are reported separately, in order."""
        text = "```a\n```\n```b\n```"
        summary = self._summary(text)
        self.assertEqual([b["language"] for b in summary["blocks"]],
                         ["a", "b"])
        self.assertEqual(summary["block_count"], 2)
        self.assertEqual(summary["total_code_lines"], 4)
        self.assertEqual(summary["code_ratio"], 1.0)

    def test_languages_histogram_ordering(self):
        """The histogram is ordered by descending count, ties broken
        alphabetically; Python dicts preserve that insertion order."""
        text = "\n".join(
            ["```go\n```"] * 1 + ["```python\n```"] * 2 +
            ["```js\n```"] * 2 + ["```ada\n```"] * 1)
        summary = self._summary(text)
        self.assertEqual(summary["block_count"], 6)
        self.assertEqual(list(summary["languages"].keys()),
                         ["js", "python", "ada", "go"])
        self.assertEqual(list(summary["languages"].values()), [2, 2, 1, 1])
        self.assertEqual(summary["code_ratio"], 1.0)

    def test_histogram_ordering_unit(self):
        """Ordering rule checked directly on fabricated blocks."""
        blocks = [{"language": lang, "span": [1, 1], "line_count": 1,
                   "unclosed": False, "indent": 0}
                  for lang in ("python", "js", "python", "ada", "js",
                               "zsh")]
        histogram = self.detector._summarize(blocks, 6)["languages"]
        self.assertEqual(list(histogram.items()),
                         [("js", 2), ("python", 2), ("ada", 1),
                          ("zsh", 1)])

    def test_code_ratio_arithmetic(self):
        """Ratio is code lines over total split-on-newline lines; a
        trailing newline counts as one extra empty line."""
        # 7 pieces after split: 3 prose lines + 3 fence lines + '' tail.
        text = "a\nb\n```js\nx\n```\nc\n"
        summary = self._summary(text)
        self.assertEqual(summary["total_code_lines"], 3)
        self.assertEqual(summary["code_ratio"], 3 / 7)

    def test_longest_block_lines(self):
        """The longest block wins regardless of position."""
        text = "```a\nx\n```\nprose\n```b\nx\ny\nz\n```"
        summary = self._summary(text)
        self.assertEqual(summary["longest_block_lines"], 5)
        self.assertEqual(summary["block_count"], 2)

    def test_empty_and_none_text(self):
        """Empty and None texts yield zero-block summaries without
        raising."""
        docs = [_doc("")]
        none_doc = _doc("placeholder")
        # Documents cannot be constructed with text=None (the id
        # validator needs a string), so assign it after construction.
        none_doc.text = None
        docs.append(none_doc)
        for doc in docs:
            self.detector.process_docs([doc], self.query)
            summary = doc.metadata["code_blocks"]
            self.assertEqual(summary["block_count"], 0)
            self.assertEqual(summary["blocks"], [])
            self.assertEqual(summary["total_code_lines"], 0)
            self.assertEqual(summary["longest_block_lines"], 0)
            self.assertEqual(summary["languages"], {})
            self.assertEqual(summary["code_ratio"], 0.0)

    # ========== Block cap ==========

    def test_blocks_list_capped_but_aggregates_count_all(self):
        """Only max_blocks detail entries are kept; every aggregate still
        covers all blocks."""
        text = "\n".join(["```", "```"] * 60)
        summary = self._summary(text)
        self.assertEqual(summary["block_count"], 60)
        self.assertEqual(len(summary["blocks"]), 50)
        self.assertEqual(summary["total_code_lines"], 120)

        capped = CodeBlockDetector()
        capped._initialize_by_component_configer(self._create_configer({
            'name': 'd', 'description': 'd', 'max_blocks': 5,
        }))
        summary = self._summary(text, capped)
        self.assertEqual(len(summary["blocks"]), 5)
        self.assertEqual(summary["block_count"], 60)
        self.assertEqual(summary["total_code_lines"], 120)
        self.assertEqual(summary["code_ratio"], 1.0)

    # ========== Masking ==========

    def test_mask_replaces_blocks_with_placeholders(self):
        """Masked text keeps all prose and swaps each block for one
        ⟦code:<lang>:<lines>⟧ line."""
        detector = CodeBlockDetector()
        detector._initialize_by_component_configer(self._create_configer({
            'name': 'd', 'description': 'd', 'mask': True,
        }))
        doc = _doc("# T\n```python\nx=1\ny=2\n```\ntail")
        detector.process_docs([doc], self.query)
        self.assertEqual(doc.text, "# T\n⟦code:python:4⟧\ntail")
        self.assertEqual(doc.metadata["code_blocks"]["block_count"], 1)

    def test_mask_placeholder_components(self):
        """The placeholder carries language then line count; an empty
        language renders as an empty field."""
        detector = CodeBlockDetector()
        detector.mask = True
        doc = _doc("```\ncode\n```")
        detector.process_docs([doc], self.query)
        self.assertEqual(doc.text, "⟦code::3⟧")

    def test_mask_is_idempotent_second_pass_noop(self):
        """A second detection pass over masked text finds no fences and
        leaves the text untouched."""
        detector = CodeBlockDetector()
        detector.mask = True
        doc = _doc("a\n```js\nf();\n```\nb\n~~~py\nz\n~~~\nc")
        detector.process_docs([doc], self.query)
        once = doc.text
        self.assertEqual(once, "a\n⟦code:js:3⟧\nb\n⟦code:py:3⟧\nc")
        detector.process_docs([doc], self.query)
        self.assertEqual(doc.text, once)
        self.assertEqual(doc.metadata["code_blocks"]["block_count"], 0)

    def test_mask_preserves_trailing_newline_and_unmasked_regions(self):
        """Masking rebuilds the text exactly outside blocks, including a
        trailing newline and empty lines."""
        detector = CodeBlockDetector()
        detector.mask = True
        doc = _doc("top\n\n```go\nx\n```\n\nend\n")
        detector.process_docs([doc], self.query)
        self.assertEqual(doc.text, "top\n\n⟦code:go:3⟧\n\nend\n")

    def test_mask_masks_blocks_beyond_the_cap(self):
        """Every block is masked, even those past max_blocks whose
        details are dropped from metadata."""
        detector = CodeBlockDetector()
        detector._initialize_by_component_configer(self._create_configer({
            'name': 'd', 'description': 'd', 'mask': True, 'max_blocks': 1,
        }))
        doc = _doc("```a\n```\n```b\n```")
        detector.process_docs([doc], self.query)
        self.assertEqual(doc.text, "⟦code:a:2⟧\n⟦code:b:2⟧")
        self.assertEqual(len(doc.metadata["code_blocks"]["blocks"]), 1)
        self.assertEqual(doc.metadata["code_blocks"]["block_count"], 2)

    # ========== Passthrough and metadata hygiene ==========

    def test_no_fences_passthrough(self):
        """Without fences the text is untouched and a zero summary is
        stamped."""
        doc = _doc("plain text\nno fences here")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(doc.text, "plain text\nno fences here")
        self.assertIs(result[0], doc)
        self.assertEqual(doc.metadata["code_blocks"]["block_count"], 0)

    def test_detection_never_modifies_text(self):
        """With mask off (default) the text is byte-identical after
        processing, fences included."""
        for text in (BACKTACK_DOC, TILDE_DOC, LONGER_CLOSER_DOC,
                     "intro\n```python\nx = 1\ny = 2"):
            doc = _doc(text)
            self.detector.process_docs([doc], self.query)
            self.assertEqual(doc.text, text)

    def test_existing_metadata_preserved(self):
        """Stamping merges into existing metadata instead of replacing
        it."""
        doc = _doc(BACKTACK_DOC, source="readme", lang="en")
        self.detector.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["source"], "readme")
        self.assertEqual(doc.metadata["lang"], "en")
        self.assertIn("code_blocks", doc.metadata)

    def test_empty_metadata_key_disables_stamping(self):
        """metadata_key '' keeps metadata untouched (mask-only use)."""
        detector = CodeBlockDetector()
        detector._initialize_by_component_configer(self._create_configer({
            'name': 'd', 'description': 'd', 'mask': True,
            'metadata_key': '',
        }))
        doc = _doc(BACKTACK_DOC)
        detector.process_docs([doc], self.query)
        self.assertEqual(doc.text, "# Intro\n⟦code:python:3⟧\nOutro.")
        self.assertNotIn("code_blocks", doc.metadata or {})

    def test_batch_processes_every_document_in_order(self):
        """Every document in the batch is stamped; order and identity are
        preserved."""
        docs = [_doc(BACKTACK_DOC, n=1), _doc("no fences", n=2),
                _doc("```js\nf()\n```", n=3)]
        result = self.detector.process_docs(docs, self.query)
        self.assertEqual([d.metadata["n"] for d in result], [1, 2, 3])
        self.assertIs(result[0], docs[0])
        self.assertEqual(result[0].metadata["code_blocks"]["block_count"], 1)
        self.assertEqual(result[1].metadata["code_blocks"]["block_count"], 0)
        self.assertEqual(
            result[2].metadata["code_blocks"]["languages"], {"js": 1})

    # ========== Determinism ==========

    def test_deterministic_across_runs_and_instances(self):
        """Repeated runs, on fresh instances, produce identical metadata
        and identical masked text."""
        text = (BACKTACK_DOC + "\n" + TILDE_DOC + "\n~~~\nunclosed tail")
        summaries, masked = [], []
        for _ in range(3):
            detector = CodeBlockDetector()
            detector.mask = True
            doc = _doc(text)
            detector.process_docs([doc], self.query)
            summaries.append(doc.metadata["code_blocks"])
            masked.append(doc.text)
        self.assertEqual(summaries[0], summaries[1])
        self.assertEqual(summaries[1], summaries[2])
        self.assertEqual(masked[0], masked[1])
        self.assertEqual(masked[1], masked[2])
        self.assertEqual(summaries[0]["block_count"], 3)

    def test_unusual_lines_are_not_fences(self):
        """Tabs after indentation and stray fence characters in prose do
        not open blocks."""
        # A tab before the fence run disqualifies the first line as an
        # opener; the trailing bare ``` then opens an unclosed block.
        summary = self._summary("\t```python\nx\n```")
        self.assertEqual(summary["blocks"], [{
            "language": "", "span": [3, 3], "line_count": 1,
            "unclosed": True, "indent": 0,
        }])

        summary = self._summary("a `inline` b\n```python\nx\n```")
        self.assertEqual(summary["block_count"], 1)
        self.assertEqual(summary["blocks"][0]["span"], [2, 4])

        summary = self._summary("  ~~~java\n  ~~~\ndone")
        self.assertEqual(summary["block_count"], 1)
        self.assertEqual(summary["blocks"][0]["indent"], 2)


if __name__ == "__main__":
    unittest.main()

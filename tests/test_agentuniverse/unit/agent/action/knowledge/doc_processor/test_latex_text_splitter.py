#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for LatexTextSplitter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.latex_text_splitter \
    import LatexTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


SAMPLE_LATEX = r"""
\documentclass{article}
\usepackage{amsmath}

\begin{document}

This is the abstract text. It introduces the topic.

\section{Introduction}

Python is a popular language for data science.

\subsection{History}

Python was created in 1991 by Guido van Rossum.

\subsection{Features}

Dynamic typing and garbage collection are key features.

\section{Conclusion}

Python continues to grow in popularity.

\end{document}
"""

VERBATIM_LATEX = r"""
\section{Code}

Some introductory text.

\begin{verbatim}
\section{This is not a real section}
This is inside verbatim.
\end{verbatim}

After verbatim.

\subsection{Real Subsection}
End of document.
"""


class TestLatexTextSplitter(unittest.TestCase):

    def _split(self, latex, **kwargs):
        proc = LatexTextSplitter(**kwargs)
        return proc.process_docs([Document(text=latex)], None)

    def test_splits_by_sections(self):
        docs = self._split(SAMPLE_LATEX)
        paths = [d.metadata["section_path"] for d in docs]
        self.assertIn("Introduction", paths)
        self.assertIn("Introduction > History", paths)
        self.assertIn("Introduction > Features", paths)
        self.assertIn("Conclusion", paths)

    def test_preamble_stripped(self):
        docs = self._split(SAMPLE_LATEX)
        # The unsectioned chunk should NOT contain documentclass.
        unsectioned = [d for d in docs if d.metadata["section_path"] == ""]
        if unsectioned:
            self.assertNotIn("documentclass", unsectioned[0].text)
            self.assertNotIn("usepackage", unsectioned[0].text)
            self.assertIn("abstract", unsectioned[0].text)

    def test_subsection_under_correct_section(self):
        docs = self._split(SAMPLE_LATEX)
        for d in docs:
            if "History" in d.metadata["section_path"]:
                self.assertIn("Guido van Rossum", d.text)

    def test_section_reset_on_new_section(self):
        docs = self._split(SAMPLE_LATEX)
        conclusion = next(d for d in docs
                          if d.metadata["section_path"] == "Conclusion")
        self.assertIn("continues to grow", conclusion.text)
        # Conclusion should NOT carry History/Features in its path.
        self.assertNotIn("History", conclusion.metadata["section_path"])

    def test_verbatim_not_parsed_as_section(self):
        docs = self._split(VERBATIM_LATEX)
        paths = [d.metadata["section_path"] for d in docs]
        # The fake section inside verbatim should NOT appear.
        self.assertNotIn("This is not a real section", paths)
        self.assertIn("Code", paths)
        self.assertIn("Code > Real Subsection", paths)

    def test_no_sections_returns_single_chunk(self):
        docs = self._split("Just some plain text. No LaTeX commands here.")
        self.assertEqual(len(docs), 1)

    def test_empty_input(self):
        proc = LatexTextSplitter()
        self.assertEqual(proc.process_docs([], None), [])

    def test_include_unsectioned_false(self):
        docs = self._split(SAMPLE_LATEX, include_unsectioned=False)
        unsectioned = [d for d in docs if d.metadata["section_path"] == ""]
        self.assertEqual(len(unsectioned), 0)

    def test_preserves_original_metadata(self):
        doc = Document(text=r"\section{S}" + "\nText.",
                       metadata={"source": "paper.pdf"})
        proc = LatexTextSplitter()
        docs = proc.process_docs([doc], None)
        self.assertEqual(docs[0].metadata["source"], "paper.pdf")

    def test_custom_section_path_key(self):
        docs = self._split(r"\section{X}" + "\nBody.",
                           section_path_key="my_path")
        self.assertIn("my_path", docs[0].metadata)

    def test_chapter_and_part_levels(self):
        latex = r"\part{Part One}" + "\nPart text.\n" + \
                r"\chapter{Chapter 1}" + "\nChapter text.\n" + \
                r"\section{Section A}" + "\nSection text.\n"
        docs = self._split(latex)
        paths = [d.metadata["section_path"] for d in docs]
        self.assertIn("Part One", paths)
        self.assertIn("Part One > Chapter 1", paths)
        self.assertIn("Part One > Chapter 1 > Section A", paths)


if __name__ == "__main__":
    unittest.main(verbosity=2)

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the disease knowledge of the medical consultation app."""

import json

from agentuniverse.agent.action.knowledge.store.document import Document
from examples.third_party_examples.apps.medical_consultation_assistant_app.intelligence.agentic.knowledge.disease_knowledge import (
    DiseaseKnowledge,
)


class TestDiseaseKnowledge:
    SEP = '\n=========================================\n'

    def _make_knowledge(self):
        return DiseaseKnowledge(name='disease_knowledge', description='disease knowledge')

    def test_to_llm_empty_docs_returns_empty_string(self):
        assert self._make_knowledge().to_llm([]) == ''

    def test_to_llm_single_doc_contains_json_payload(self):
        doc = Document(text='fever is a symptom', metadata={'file_name': 'fever.txt'})
        result = self._make_knowledge().to_llm([doc])
        assert json.loads(result) == {'text': 'fever is a symptom', 'from': 'fever.txt'}

    def test_to_llm_multiple_docs_joined_by_separator(self):
        docs = [
            Document(text='fever', metadata={'file_name': 'a.txt'}),
            Document(text='cough', metadata={'file_name': 'b.txt'}),
        ]
        result = self._make_knowledge().to_llm(docs)
        parts = result.split(self.SEP)
        assert len(parts) == 2
        assert json.loads(parts[0]) == {'text': 'fever', 'from': 'a.txt'}
        assert json.loads(parts[1]) == {'text': 'cough', 'from': 'b.txt'}

    def test_to_llm_preserves_file_name_metadata(self):
        docs = [
            Document(text='symptom one', metadata={'file_name': 'guide.txt'}),
            Document(text='symptom two', metadata={'file_name': 'guide.txt'}),
        ]
        result = self._make_knowledge().to_llm(docs)
        assert result.count('"from": "guide.txt"') == 2

    def test_to_llm_keeps_original_text_verbatim(self):
        doc = Document(text='  note with spaces  ', metadata={'file_name': 'raw.txt'})
        result = json.loads(self._make_knowledge().to_llm([doc]))
        assert result['text'] == '  note with spaces  '

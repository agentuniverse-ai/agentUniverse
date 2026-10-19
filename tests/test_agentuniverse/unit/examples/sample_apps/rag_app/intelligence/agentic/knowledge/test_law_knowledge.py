# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_law_knowledge.py

"""Unit tests for LawKnowledge.to_llm formatting."""

import json

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from examples.sample_apps.rag_app.intelligence.agentic.knowledge.law_knowledge import (
    LawKnowledge,
)

SEPARATOR = '\n=========================================\n'


def _make_knowledge():
    return LawKnowledge(name='law_knowledge', description='legal knowledge for tests')


def test_to_llm_formats_single_document():
    doc = Document(text='法律条文内容', metadata={'file_name': 'civil_code.txt'})
    output = _make_knowledge().to_llm([doc])
    assert output == json.dumps({'text': '法律条文内容', 'from': 'civil_code.txt'},
                                ensure_ascii=False)


def test_to_llm_joins_documents_with_separator():
    docs = [Document(text=f'text {i}', metadata={'file_name': f'file_{i}.txt'})
            for i in (1, 2, 3)]
    output = _make_knowledge().to_llm(docs)
    segments = output.split(SEPARATOR)
    assert len(segments) == 3
    assert json.loads(segments[0]) == {'text': 'text 1', 'from': 'file_1.txt'}
    assert json.loads(segments[2]) == {'text': 'text 3', 'from': 'file_3.txt'}


def test_to_llm_keeps_unicode_characters():
    doc = Document(text='肖像权纠纷', metadata={'file_name': 'law.txt'})
    output = _make_knowledge().to_llm([doc])
    assert '肖像权纠纷' in output
    assert '\\u' not in output


def test_to_llm_returns_empty_string_for_no_docs():
    assert _make_knowledge().to_llm([]) == ''


def test_to_llm_requires_file_name_metadata():
    doc = Document(text='no file name metadata')
    with pytest.raises((TypeError, KeyError)):
        _make_knowledge().to_llm([doc])

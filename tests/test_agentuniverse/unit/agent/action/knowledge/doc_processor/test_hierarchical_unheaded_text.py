"""Unheaded source text must survive hierarchical preprocessing."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.hierarchical_regex_text_splitter import HierarchicalRegexTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


def splitter():
    return HierarchicalRegexTextSplitter(hierarchical_index=[
        {'reg_exp': r'^Chapter \d+', 'need_summary': False},
        {'reg_exp': r'^Section \d+', 'need_summary': False},
    ])


@pytest.mark.parametrize('text', ['Plain source text.', '前言内容\n第二行', 'Chapterless text\nMore evidence'])
def test_no_matching_heading_preserves_source(text):
    source = Document(text=text, metadata={'source': 'report', 'nested': {'tags': ['a']}})
    docs = splitter().process_docs([source])
    assert len(docs) == 1
    assert docs[0].text == text
    assert docs[0].metadata['hierarchical_parent'] == 'root'
    assert docs[0].metadata['hierarchical_level'] == 0
    assert docs[0].metadata['source'] == 'report'
    docs[0].metadata['nested']['tags'].append('b')
    assert source.metadata == {'source': 'report', 'nested': {'tags': ['a']}}


def test_preamble_and_heading_tree_are_both_preserved():
    docs = splitter().process_docs([Document(text='Introduction\nScope\nChapter 1\nBody\nSection 1\nDetail')])
    assert len(docs) == 3
    assert docs[0].text == 'Introduction\nScope'
    assert docs[0].metadata['hierarchical_parent'] == 'root'
    assert docs[1].text == 'Chapter 1\nBody\nSection 1\nDetail'
    assert docs[2].metadata['hierarchical_parent'] == docs[1].id


def test_plain_and_structured_documents_in_same_batch():
    docs = splitter().process_docs([Document(text='Standalone facts'), Document(text='Chapter 1\nBody')])
    assert [d.text for d in docs] == ['Standalone facts', 'Chapter 1\nBody']


@pytest.mark.parametrize('text', ['', ' \n\t', 'Chapter 1\nBody'])
def test_empty_or_heading_only_inputs_do_not_add_empty_chunk(text):
    docs = splitter().process_docs([Document(text=text)])
    assert len(docs) == (1 if text.startswith('Chapter') else 0)


def test_unheaded_text_does_not_invoke_summary_agent():
    processor = HierarchicalRegexTextSplitter()  # default headings request summaries
    docs = processor.process_docs([Document(text='No chapter markers here')])
    assert [d.text for d in docs] == ['No chapter markers here']


def test_preamble_keeps_line_normalization():
    docs = splitter().process_docs([Document(text='  Intro  \n\n Scope \n Chapter 1\n Body')])
    assert [d.text for d in docs] == ['Intro\nScope', 'Chapter 1\nBody']


def test_merge_first_preserves_unheaded_inputs():
    processor = splitter()
    processor.merge_first = True
    docs = processor.process_docs([Document(text='First facts'), Document(text='Second facts')])
    assert [d.text for d in docs] == ['First facts\nSecond facts']


def test_summary_is_only_applied_to_heading_chunks(monkeypatch):
    from types import SimpleNamespace
    from agentuniverse.agent.agent_manager import AgentManager

    calls = []

    def run(**kwargs):
        calls.append(kwargs['input'])
        return SimpleNamespace(output='Chapter summary')

    agent = SimpleNamespace(agent_model=SimpleNamespace(profile={}), run=run)
    monkeypatch.setattr(type(AgentManager()), 'get_instance_obj', lambda self, name: agent)
    processor = splitter()
    processor.hierarchical_index[0]['need_summary'] = True
    docs = processor.process_docs([Document(text='Intro\nChapter 1\nBody')])
    assert calls == ['Chapter 1\nBody']
    assert [d.text for d in docs] == ['Intro', 'Chapter summary']

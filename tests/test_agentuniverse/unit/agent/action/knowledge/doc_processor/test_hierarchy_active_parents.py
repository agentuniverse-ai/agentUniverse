"""An active branch cannot retain descendants from an earlier ancestor."""
import pytest
from agentuniverse.agent.action.knowledge.doc_processor.hierarchical_regex_text_splitter import HierarchicalRegexTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('text,expected', [
    ('Chapter A\nSection A1\nItem old\nChapter B\nItem new', ['root', 0, 1, 'root', 3]),
    ('Chapter A\nSection A1\nItem old\nSection A2\nItem new', ['root', 0, 1, 0, 3]),
    ('Item orphan\nbody', ['root']),
])
def test_parent_links_and_ancestor_text_follow_active_branch(text, expected):
    splitter = HierarchicalRegexTextSplitter(hierarchical_index=[
        {'reg_exp': pattern, 'need_summary': False} for pattern in ['Chapter', 'Section', 'Item']
    ])
    docs = splitter.process_docs([Document(text=text)])
    assert len(docs) == len(expected)
    for doc, parent in zip(docs, expected):
        assert doc.metadata['hierarchical_parent'] == ('root' if parent == 'root' else docs[parent].id)
    if len(docs) == 5:
        assert 'Item new' not in docs[1].text
        assert 'Item new' in docs[3].text
        assert docs[-1].metadata['hierarchical_level'] == 2

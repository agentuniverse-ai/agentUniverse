"""An exhausted sentence allowance must never emit extractive source text."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.summarization_processor import SummarizationProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.mark.parametrize('max_sentences', [0, -1, -2])
@pytest.mark.parametrize('text', ['Alpha improves accuracy. Beta reduces cost. Gamma saves time.',
                                 'A. I. X.', '。！？'])
def test_nonpositive_sentence_allowance_emits_no_text(max_sentences, text):
    source = Document(text=text, metadata={'source': 'paper'})
    result = SummarizationProcessor(max_sentences=max_sentences).process_docs(
        [source], Query(query_str='accuracy'))
    assert len(result) == 1
    assert result[0].text == ''
    assert result[0].metadata['summarization_mode'] == 'extractive'
    assert result[0].metadata['source_doc_count'] == 1
    assert source.text == text


@pytest.mark.parametrize('max_sentences', [1, 5])
def test_positive_allowance_keeps_short_source_unchanged(max_sentences):
    result = SummarizationProcessor(max_sentences=max_sentences).process_docs([
        Document(text='A complete source sentence.')])
    assert result[0].text == 'A complete source sentence.'

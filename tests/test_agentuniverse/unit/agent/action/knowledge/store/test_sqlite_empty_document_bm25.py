"""Keyword-tagged empty documents must not make BM25 divide by zero."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.configer import Configer


@pytest.fixture
def store(tmp_path, monkeypatch):
    config = Configer()
    config.value = {'BASE_INFO': {'appname': 'sqlite_empty_corpus'}}
    monkeypatch.setattr(ApplicationConfigManager(), '_ApplicationConfigManager__app_configer',
                        AppConfiger().load_by_configer(config))
    extractor = JiebaKeywordExtractor(name='empty_corpus_keywords')
    manager = DocProcessorManager()
    code = extractor.get_instance_code()
    manager.register(code, extractor)
    instance = SQLiteStore(db_path=str(tmp_path / 'corpus.sqlite'), keyword_extractor=extractor.name)
    instance._new_client()
    try:
        yield instance
    finally:
        instance.conn.close()
        manager.unregister(code)


@pytest.mark.parametrize('count', [1, 2])
@pytest.mark.parametrize('b', [0.0, 0.75, 1.0])
def test_query_tagged_empty_corpus(store, count, b):
    store.b = b
    docs = [Document(id=f'empty-{i}', text='', keywords={'tag'}, metadata={'ordinal': i})
            for i in range(count)]
    store.insert_document(docs)
    assert store._get_all_docs_words_count() == 0
    result = store.query(Query(query_str='tag', keywords={'tag'}))
    assert {doc.id for doc in result} == {doc.id for doc in docs}
    assert all(doc.text == '' for doc in result)
    assert {doc.metadata['ordinal'] for doc in result} == set(range(count))


@pytest.mark.parametrize('b', [0.0, 0.75, 1.0])
def test_mixed_corpus_still_ranks_nonempty_match_first(store, b):
    store.b = b
    store.insert_document([Document(id='empty', text='', keywords={'tag'}),
                           Document(id='match', text='tag', keywords={'tag'})])
    result = store.query(Query(query_str='tag', keywords={'tag'}))
    assert [doc.id for doc in result] == ['match', 'empty']


def test_empty_store_query_stays_empty(store):
    assert store.query(Query(query_str='tag', keywords={'tag'})) == []

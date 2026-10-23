"""Native FAISS recall should preserve stored document keywords."""
import pytest

pytest.importorskip('faiss', reason='Install faiss-cpu to run native FAISS recall tests')

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.faiss_store import FAISSStore
from agentuniverse.agent.action.knowledge.store.query import Query


def create_store(**kwargs):
    store = FAISSStore(**kwargs)
    store._new_client()
    return store


def recall(store, top_k=1):
    return store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=top_k))


@pytest.mark.parametrize('keywords', [set(), {'retrieval'}, {'中文', 'mixed tag'}])
def test_query_retains_keywords_and_existing_fields(keywords):
    store = create_store()
    source = Document(id='one', text='Source facts', embedding=[1.0, 0.0],
                      metadata={'source': 'report'}, keywords=keywords)
    store.insert_document([source])
    result = recall(store)[0]
    assert result.keywords == keywords
    assert result.id == source.id
    assert result.text == source.text
    assert result.embedding == source.embedding
    assert result.metadata == {'source': 'report', 'score': pytest.approx(0.0)}
    assert source.metadata == {'source': 'report'}


def test_ranked_hits_keep_their_own_keywords():
    store = create_store()
    store.insert_document([
        Document(id='far', text='Far facts', embedding=[0.0, 1.0], keywords={'far'}),
        Document(id='near', text='Near facts', embedding=[1.0, 0.0], keywords={'near'}),
    ])
    results = recall(store, top_k=2)
    assert [(doc.id, doc.keywords) for doc in results] == [('near', {'near'}), ('far', {'far'})]


def test_recalled_keywords_do_not_alias_stored_document():
    store = create_store()
    source = Document(id='one', text='Facts', embedding=[1.0, 0.0], keywords={'stored'})
    store.insert_document([source])
    result = recall(store)[0]
    assert result.keywords == {'stored'}
    result.keywords.add('downstream-only')
    assert source.keywords == {'stored'}
    assert recall(store)[0].keywords == {'stored'}


def test_reload_then_query_retains_keywords(tmp_path):
    config = {'index_path': str(tmp_path / 'index.faiss'), 'metadata_path': str(tmp_path / 'metadata.pkl')}
    store = create_store(**config)
    store.insert_document([
        Document(id='persisted', text='Saved facts', embedding=[1.0, 0.0], keywords={'saved', '原文'})])
    reloaded = create_store(**config)
    assert reloaded.get_document_by_id('persisted').keywords == {'saved', '原文'}
    assert recall(reloaded)[0].keywords == {'saved', '原文'}

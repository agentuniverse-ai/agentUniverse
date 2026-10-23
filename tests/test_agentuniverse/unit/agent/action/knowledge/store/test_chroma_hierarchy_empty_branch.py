"""An exhausted hierarchy frontier must not restart at unrelated descendants."""
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

chromadb = pytest.importorskip('chromadb')

from agentuniverse.agent.action.knowledge.store.chroma_hierarchical_store import ChromaHierarchicalStore
from agentuniverse.agent.action.knowledge.store.query import Query


def result(ids):
    return {
        'ids': [ids],
        'documents': [[f'text {identifier}' for identifier in ids]],
        'metadatas': None,
        'embeddings': None,
        'distances': [[0.1] * len(ids)],
    }


@pytest.mark.parametrize('empty_depth', [0, 1])
@pytest.mark.parametrize('embeddings', [[], [[1.0, 0.0]]])
def test_empty_frontier_stops_without_another_global_search(empty_depth, embeddings):
    store = ChromaHierarchicalStore(search_depth=3, similarity_top_k=1)
    collection = MagicMock()
    responses = ([result(['selected-root'])] if empty_depth else []) + [result([])]
    collection.query.side_effect = responses + [result(['unrelated-descendant'])] * 3
    store.collection = collection

    documents = store.query(Query(query_str='target', embeddings=embeddings))

    assert documents == []
    assert collection.query.call_count == empty_depth + 1
    assert collection.query.call_args_list[0].kwargs['where'] == {'hierarchical_level': 0}
    if empty_depth:
        assert collection.query.call_args_list[1].kwargs['where'] == {
            'hierarchical_parent': 'selected-root'
        }


@pytest.mark.parametrize('missing_roots', [True, False])
def test_real_collection_never_returns_descendants_outside_selected_branch(
        missing_roots, tmp_path):
    # A PersistentClient is identified by its path, so this only collides with
    # a previous run over the same directory; keep the cache pristine anyway.
    from chromadb.api.client import SharedSystemClient
    SharedSystemClient.clear_system_cache()
    client = chromadb.PersistentClient(
        path=str(tmp_path / "chroma"),
        settings=chromadb.Settings(anonymized_telemetry=False),
    )
    name = f'empty_branch_{uuid4().hex}'
    collection = client.create_collection(name, embedding_function=None)
    try:
        if missing_roots:
            collection.add(
                ids=['orphan'], documents=['orphan'], embeddings=[[1.0, 0.0]],
                metadatas=[{'hierarchical_level': 1, 'hierarchical_parent': 'missing'}],
            )
        else:
            collection.add(
                ids=['selected', 'other-root', 'other-child', 'other-grandchild'],
                documents=['selected', 'other root', 'other child', 'other grandchild'],
                embeddings=[[1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [1.0, 0.0]],
                metadatas=[
                    {'hierarchical_level': 0, 'hierarchical_parent': 'root'},
                    {'hierarchical_level': 0, 'hierarchical_parent': 'root'},
                    {'hierarchical_level': 1, 'hierarchical_parent': 'other-root'},
                    {'hierarchical_level': 2, 'hierarchical_parent': 'other-child'},
                ],
            )
        store = ChromaHierarchicalStore(
            search_depth=2 if missing_roots else 3, similarity_top_k=1,
            collection=collection,
        )

        documents = store.query(Query(query_str='target', embeddings=[[1.0, 0.0]]))

        assert documents == []
    finally:
        client.delete_collection(name)


def test_empty_parent_does_not_discard_matching_sibling_branch():
    store = ChromaHierarchicalStore(search_depth=2, similarity_top_k=2)
    collection = MagicMock()
    collection.query.side_effect = [
        result(['empty-parent', 'matching-parent']), result([]), result(['matching-child'])
    ]
    store.collection = collection

    documents = store.query(Query(query_str='target', embeddings=[[1.0, 0.0]]))

    assert [doc.id for doc in documents] == ['matching-child']
    assert collection.query.call_count == 3

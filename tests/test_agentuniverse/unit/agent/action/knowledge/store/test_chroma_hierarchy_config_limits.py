"""Exercise per-level retrieval limits through the documented YAML loader."""
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip('chromadb')

from agentuniverse.agent.action.knowledge.store.chroma_hierarchical_store import ChromaHierarchicalStore
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _load_store(tmp_path, limits):
    path = tmp_path / 'hierarchy.yaml'
    text = '''name: hierarchy
description: YAML retrieval limits
search_depth: 2
similarity_top_k: 3
metadata:
  type: STORE
  module: agentuniverse.agent.action.knowledge.store.chroma_hierarchical_store
  class: ChromaHierarchicalStore
'''
    if limits is not None:
        text += f'similarity_top_k_list: {limits}\n'
    path.write_text(text, encoding='utf-8')
    configer = ComponentConfiger().load_by_configer(Configer(str(path)).load())
    # Initialization registers database setup for post-fork execution. Keep
    # these callbacks out of the application's global queue during this test.
    with patch('agentuniverse.agent.action.knowledge.store.store.add_post_fork'):
        return ChromaHierarchicalStore().initialize_by_component_configer(configer)


def _response(rows):
    return {
        'ids': [[identifier for identifier, _ in rows]],
        'documents': [[identifier for identifier, _ in rows]],
        'distances': [[distance for _, distance in rows]],
        'embeddings': None,
        'metadatas': None,
    }


@pytest.mark.parametrize('limits,expected_counts,expected_ids', [
    ([2, 1], [2, 1, 1], ['a1']),
    ([1], [1, 3], ['a1', 'a2']),
    ([], [3, 3, 3], ['a1', 'a2', 'b1']),
    (None, [3, 3, 3], ['a1', 'a2', 'b1']),
])
def test_yaml_limits_reach_each_query_and_final_ranking(
        tmp_path, limits, expected_counts, expected_ids):
    store = _load_store(tmp_path, limits)
    collection = MagicMock()
    rows_by_parent = {
        'a': [('a1', 0.1), ('a2', 0.2)],
        'b': [('b1', 0.3), ('b2', 0.4)],
    }

    def query(**kwargs):
        parent = kwargs['where'].get('hierarchical_parent')
        rows = rows_by_parent[parent] if parent else [('a', 0.1), ('b', 0.2)]
        return _response(rows[:kwargs['n_results']])

    collection.query.side_effect = query
    store.collection = collection

    documents = store.query(Query(query_str='test', embeddings=[[1.0, 0.0]]))

    assert [call.kwargs['n_results'] for call in collection.query.call_args_list] == expected_counts
    assert [doc.id for doc in documents] == expected_ids

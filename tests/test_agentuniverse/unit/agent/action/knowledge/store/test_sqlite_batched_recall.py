"""SQLite recall should use indexes and bounded batches without changing ranks."""
import sqlite3
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


@pytest.fixture
def store():
    instance = SQLiteStore()
    instance.conn = sqlite3.connect(':memory:')
    instance._create_tables()
    yield instance
    instance.conn.close()


def populate(store, count):
    with store.conn:
        store.conn.executemany(
            'INSERT INTO documents VALUES (?, ?, ?, ?)',
            [(str(i), 'hello ' * (i + 1), i + 1, '{"source":"test"}') for i in range(count)],
        )
        store.conn.executemany(
            'INSERT INTO inverted_index VALUES (?, ?)', [('hello', str(i)) for i in range(count)],
        )


@pytest.mark.parametrize('count,max_selects', [(100, 5), (1001, 9)])
def test_recall_batches_candidate_reads_and_preserves_bm25(store, count, max_selects):
    populate(store, count)
    statements = []
    store.conn.set_trace_callback(statements.append)
    # Use a known scoring rule to check ranking separately from access mechanics.
    with patch.object(SQLiteStore, 'compute_bm25', autospec=True,
                      side_effect=lambda self, query, text, index, total, words: len(text)) as score:
        result = store.query(Query(query_str='hello', keywords={'hello'}))
    assert [doc.id for doc in result] == [str(i) for i in range(count - 1, count - 11, -1)]
    assert all(doc.metadata == {'source': 'test'} for doc in result)
    assert all(doc.text == 'hello ' * (int(doc.id) + 1) for doc in result)
    assert score.call_count == count
    assert all(call.args[-2:] == (count, count * (count + 1) // 2) for call in score.call_args_list)
    selects = [sql for sql in statements if sql.lstrip().upper().startswith('SELECT')]
    assert len(selects) <= max_selects


def test_existing_database_gets_lookup_indexes_idempotently(store):
    populate(store, 1)
    store.conn.execute('DROP INDEX idx_inverted_index_term_doc_id')
    store.conn.execute('DROP INDEX idx_inverted_index_doc_id')
    store._create_tables()
    store._create_tables()
    assert store.conn.execute('SELECT COUNT(*) FROM documents').fetchone()[0] == 1
    for sql in (
        "SELECT doc_id FROM inverted_index WHERE term = 'hello'",
        "DELETE FROM inverted_index WHERE doc_id = '1'",
    ):
        plan = ' '.join(row[3] for row in store.conn.execute('EXPLAIN QUERY PLAN ' + sql))
        assert 'SEARCH' in plan
        assert 'SCAN inverted_index' not in plan


def test_empty_recall(store):
    assert store.query(Query(query_str='absent', keywords={'absent'})) == []


def test_real_bm25_ranking(store):
    populate(store, 3)
    result = store.query(Query(query_str='hello', keywords={'hello'}))
    # BM25 saturation still prefers higher term frequency with this corpus.
    assert [doc.id for doc in result] == ['2', '1', '0']


def test_large_result_window_batches_metadata_and_binds_ids(store):
    populate(store, 1001)
    special_id = "id'with?sql"
    with store.conn:
        store.conn.execute('UPDATE documents SET id = ? WHERE id = ?', (special_id, '0'))
        store.conn.execute('UPDATE inverted_index SET doc_id = ? WHERE doc_id = ?', (special_id, '0'))
    store.similarity_top_k = 1001
    with patch.object(SQLiteStore, 'compute_bm25', return_value=1):
        result = store.query(Query(query_str='hello', keywords={'hello'}))
    assert len(result) == 1001
    assert special_id in {doc.id for doc in result}
    assert all(doc.metadata == {'source': 'test'} for doc in result)


def test_shared_keywords_do_not_duplicate_candidates(store):
    populate(store, 3)
    with store.conn:
        store.conn.executemany(
            'INSERT INTO inverted_index VALUES (?, ?)', [('other', str(i)) for i in range(3)],
        )
    result = store.query(Query(query_str='hello', keywords={'hello', 'other'}))
    assert [doc.id for doc in result] == ['2', '1', '0']

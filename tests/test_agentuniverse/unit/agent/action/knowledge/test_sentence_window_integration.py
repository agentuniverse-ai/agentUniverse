"""Real files, sentence persistence, same-text source identity and expansion."""

import json
from unittest.mock import MagicMock, patch

import pytest
import tiktoken

import agentuniverse.base.annotation.trace as trace_module
from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
from agentuniverse.agent.action.knowledge.doc_processor.sentence_window import SentenceWindowExpander, SentenceWindowSplitter
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


@pytest.mark.parametrize("mode", ["disabled", "sentences", "expanded"])
def test_file_ingestion_reopen_and_context_expansion(tmp_path, record_testsuite_property, mode):
    texts = [f"Only when voltage is {voltage}. Run alpha procedure. It must stop on heat." for voltage in (10, 20)]
    paths = [tmp_path / f"manual-{i}.txt" for i in range(2)]
    for path, text in zip(paths, texts):
        path.write_text(text, encoding="utf-8")
    # Include all fixture terms in BOTH baseline and sentence indexes; the
    # extractor's default top_k=3 can omit alpha from the longer baseline.
    processors = {"split": SentenceWindowSplitter(), "expand": SentenceWindowExpander(), "keywords": JiebaKeywordExtractor(top_k=50)}
    store = SQLiteStore(db_path=str(tmp_path / "sentences.db"), keyword_extractor="keywords")
    knowledge = Knowledge(name="sentence-example", stores=["local"], readers={"txt": "raw"},
                          insert_processors=[] if mode == "disabled" else ["split"],
                          post_processors=["expand"] if mode == "expanded" else [])
    with patch.object(knowledge_module, "DocProcessorManager") as pm, \
            patch("agentuniverse.agent.action.knowledge.store.sqlite_store.DocProcessorManager") as sm, \
            patch.object(knowledge_module, "ReaderManager") as rm, \
            patch.object(knowledge_module, "StoreManager") as stm, \
            patch.object(knowledge_module, "RagRouterManager") as routers, \
            patch.object(trace_module, "ConversationMemoryModule"), \
            patch.object(trace_module, "Monitor") as monitor:
        pm.return_value.get_instance_obj.side_effect = lambda name, **kw: processors[name]
        sm.return_value.get_instance_obj.side_effect = lambda name, **kw: processors[name]
        rm.return_value.get_instance_obj.return_value = TxtReader()
        stm.return_value.get_instance_obj.return_value = store
        router = MagicMock()
        router.rag_route.return_value = [(Query(query_str="alpha", keywords={"alpha"}), "local")]
        routers.return_value.get_instance_obj.return_value = router
        monitor.get_invocation_chain.return_value = []
        try:
            store._new_client()
            for path in paths:
                knowledge.insert_knowledge(source_path=str(path))
            rows = store.conn.execute("SELECT text, metadata FROM documents").fetchall()
            assert len(rows) == (2 if mode == "disabled" else 6)
            if mode == "expanded":
                record_testsuite_property("sentence_fixture_original_utf8_bytes", sum(len(text.encode("utf-8")) for text in texts))
                record_testsuite_property("sentence_fixture_stored_text_utf8_bytes", sum(len(row[0].encode("utf-8")) for row in rows))
                record_testsuite_property("sentence_fixture_stored_metadata_utf8_bytes", sum(len(row[1].encode("utf-8")) for row in rows))
            store.conn.close()
            store._new_client()
            result = knowledge.query_knowledge(query_str="alpha")
            assert len(result) == 2 and len({doc.id for doc in result}) == 2
            if mode == "sentences":
                assert all(doc.text == "Run alpha procedure." for doc in result)
            else:
                assert {doc.text for doc in result} == set(texts)
            if mode == "disabled":
                assert all("sentence_window" not in doc.metadata for doc in result)
            elif mode == "expanded":
                assert all(not doc.embedding and not doc.keywords for doc in result)
                assert {doc.metadata["file_name"] for doc in result} == {path.name for path in paths}
                assert all(doc.metadata["sentence_window"]["matches"][0]["text"] == "Run alpha procedure." for doc in result)
                record_testsuite_property("sentence_fixture_recalled_sentence_chars", 2 * len("Run alpha procedure."))
                record_testsuite_property("sentence_fixture_expanded_chars", sum(len(doc.text) for doc in result))
                tokenizer = tiktoken.get_encoding("cl100k_base")
                record_testsuite_property("sentence_fixture_anchor_cl100k_tokens", 2 * len(tokenizer.encode("Run alpha procedure.")))
                record_testsuite_property("sentence_fixture_expanded_cl100k_tokens", sum(len(tokenizer.encode(doc.text)) for doc in result))
                persisted = store.conn.execute("SELECT metadata FROM documents").fetchall()
                assert all(json.loads(row[0])["sentence_window"]["stage"] == "sentence" for row in persisted)
        finally:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
            if store.conn is not None:
                store.conn.close()

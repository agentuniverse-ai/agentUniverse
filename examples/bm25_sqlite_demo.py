"""Standalone retrieval example: python -m examples.bm25_sqlite_demo.

Uses a temporary database and real component managers; no server or API key.
Run in a fresh process, not inside an already bootstrapped application.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from agentuniverse.agent.action.knowledge.doc_processor.bm25_reranker import BM25Reranker
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def main():
    ApplicationConfigManager().app_configer = AppConfiger()
    yaml_path = Path(__file__).resolve().parents[1] / "agentuniverse/agent/action/knowledge/doc_processor/bm25_reranker.yaml"
    config = ComponentConfiger().load_by_configer(Configer(path=str(yaml_path)).load())
    reranker = BM25Reranker().initialize_by_component_configer(config)
    keywords = JiebaKeywordExtractor(name="demo_keywords", top_k=100)
    router = BaseRouter(name="base_router")
    registrations = []
    knowledge = None
    store = None
    with TemporaryDirectory(prefix="au-bm25-") as directory:
        try:
            store = SQLiteStore(name="demo_store", db_path=str(Path(directory) / "manuals.db"), keyword_extractor="demo_keywords")
            for manager, component in [(DocProcessorManager(), keywords), (DocProcessorManager(), reranker),
                                       (RagRouterManager(), router), (StoreManager(), store)]:
                code = component.get_instance_code()
                manager.register(code, component)
                registrations.append((manager, code))
            store._new_client()
            store.insert_document([
                Document(id="near", text="AX-120 installation manual"),
                Document(id="exact", text="AX-12 installation manual"),
                Document(id="other", text="General maintenance manual"),
            ])
            store.conn.close()
            store._new_client()
            before = store.conn.execute("SELECT id, metadata FROM documents ORDER BY id").fetchall()
            knowledge = Knowledge(name="manual_search", stores=["demo_store"])
            original = knowledge.query_knowledge(query_str="AX-12 manual")
            knowledge.post_processors = ["bm25_reranker"]
            reranked = knowledge.query_knowledge(query_str="AX-12 manual")
            persisted = store.conn.execute("SELECT id, metadata FROM documents ORDER BY id").fetchall()
            report = {
                "workflow": "sqlite_insert_reopen_public_knowledge_query",
                "original_ids": [doc.id for doc in original],
                "reranked": [{"id": doc.id, "text": doc.text, "bm25_score": doc.metadata["bm25_score"]} for doc in reranked],
                "persisted_count": len(persisted),
                "persisted_metadata_unchanged": persisted == before,
                "limitation": "controlled integration fixture, not proof of aggregate relevance improvement",
            }
        finally:
            if knowledge is not None:
                knowledge.insert_executor.shutdown(wait=True)
                knowledge.query_executor.shutdown(wait=True)
            if store is not None and store.conn is not None:
                store.conn.close()
            for manager, code in reversed(registrations):
                manager.unregister(code)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

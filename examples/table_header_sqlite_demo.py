"""Run in a fresh process: python -m examples.table_header_sqlite_demo.

Synthetic parameter table; real file, managers, public Knowledge and SQLite.
No API key or existing application/database required.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
from agentuniverse.agent.action.knowledge.doc_processor.table_header_splitter import TableHeaderSplitter
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def main():
    ApplicationConfigManager().app_configer = AppConfiger()
    config_path = Path(__file__).resolve().parents[1] / "agentuniverse/agent/action/knowledge/doc_processor/table_header_splitter.yaml"
    config = Configer(str(config_path)).load()
    config.set("max_chars", 120)
    splitter = TableHeaderSplitter().initialize_by_component_configer(ComponentConfiger(config).load())
    header = "| model | power (W) |\n| --- | --- |\n"
    source = "# alpha specifications\n\n" + header + "".join(f"| alpha{i} | {i * 10} |\n" for i in range(12))
    registrations = []
    knowledge = None
    store = None
    with TemporaryDirectory(prefix="au-table-") as directory:
        path = Path(directory) / "specifications.md"
        path.write_text(source, encoding="utf-8")
        try:
            store = SQLiteStore(name="table_store", db_path=str(Path(directory) / "tables.db"), keyword_extractor="table_keywords", similarity_top_k=100)
            components = [(DocProcessorManager(), splitter),
                          (DocProcessorManager(), JiebaKeywordExtractor(name="table_keywords", top_k=100)),
                          (ReaderManager(), TxtReader(name="raw_markdown")),
                          (RagRouterManager(), BaseRouter(name="base_router")),
                          (StoreManager(), store)]
            for manager, component in components:
                code = component.get_instance_code()
                manager.register(code, component)
                registrations.append((manager, code))
            store._new_client()
            knowledge = Knowledge(name="table_demo", stores=["table_store"], readers={"md": "raw_markdown"}, insert_processors=["table_header_splitter"])
            knowledge.insert_knowledge(source_path=str(path))
            stored_count = store.conn.execute("SELECT count(*) FROM documents").fetchone()[0]
            store.conn.close()
            store._new_client()
            recalled = knowledge.query_knowledge(query_str="alpha")
            tables = [doc for doc in recalled if doc.metadata["table_chunk"]["kind"] == "table"]
            report = {"fixture": "synthetic_parameter_table", "stored_count": stored_count,
                      "table_chunks": [{"text": doc.text, "rows": [doc.metadata["table_chunk"]["row_start"], doc.metadata["table_chunk"]["row_end"]], "file_name": doc.metadata["file_name"]} for doc in tables],
                      "all_headers_retained": bool(tables) and all(header in doc.text for doc in tables)}
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

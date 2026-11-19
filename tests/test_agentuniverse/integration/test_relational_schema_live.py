"""Catalog and relationship context checked against real SQLite/PostgreSQL."""

import json
import os
import uuid

import pytest
from sqlalchemy import create_engine, event, text

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.relational_schema_store import RelationalSchemaStore


@pytest.fixture(params=["sqlite", "postgresql"])
def database(request, tmp_path):
    if request.param == "postgresql":
        url = os.environ["AU_SCHEMA_POSTGRES_URL"]
        engine = create_engine(url)
        schema = "b05_" + uuid.uuid4().hex[:12]
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
    else:
        engine = create_engine("sqlite:///" + str(tmp_path / "catalog.db"))
        schema = "main"

    def q(name):
        return f"{schema}.{name}"

    with engine.begin() as conn:
        conn.execute(
            text(
                f"CREATE TABLE {q('customers')} (tenant INTEGER, id INTEGER, customer_name TEXT, PRIMARY KEY (tenant,id))"
            )
        )
        conn.execute(
            text(
                f"CREATE TABLE {q('orders')} (id INTEGER PRIMARY KEY, tenant INTEGER, customer_id INTEGER, FOREIGN KEY (tenant,customer_id) REFERENCES customers(tenant,id))"
                if schema == "main"
                else f"CREATE TABLE {q('orders')} (id INTEGER PRIMARY KEY, tenant INTEGER, customer_id INTEGER, FOREIGN KEY (tenant,customer_id) REFERENCES {q('customers')}(tenant,id))"
            )
        )
        conn.execute(text(f"CREATE TABLE {q('products')} (id INTEGER PRIMARY KEY, product_name TEXT UNIQUE)"))
        conn.execute(
            text(
                f"CREATE TABLE {q('items')} (id INTEGER PRIMARY KEY, order_id INTEGER REFERENCES {'orders' if schema == 'main' else q('orders')}(id), product_id INTEGER REFERENCES {'products' if schema == 'main' else q('products')}(id))"
            )
        )
        conn.execute(
            text(
                f"CREATE TABLE {q('cycles')} (id INTEGER PRIMARY KEY, parent_id INTEGER REFERENCES {'cycles' if schema == 'main' else q('cycles')}(id))"
            )
        )
        conn.execute(text(f"INSERT INTO {q('customers')} VALUES (1,1,'PRIVATE_ROW_NEVER_READ')"))
    calls = []

    def record(conn, cursor, statement, parameters, context, executemany):
        calls.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    try:
        yield engine, schema, calls
    finally:
        event.remove(engine, "before_cursor_execute", record)
        if schema != "main":
            with engine.begin() as conn:
                conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        engine.dispose()


def store(database, **kwargs):
    engine, schema, _ = database
    tables = [(schema, name) for name in ["customers", "orders", "items", "products", "cycles"]]
    return RelationalSchemaStore(client=engine, tables=tables, seed_limit=2, **kwargs)


def test_compound_fk_bridge_and_catalog_values(database):
    engine, schema, calls = database
    docs, report = store(database).query_with_report(Query(query_str="customers products"))
    context = docs[0].metadata["relational_schema"]
    assert [entry["table"] for entry in context["tables"]] == ["customers", "items", "orders", "products"]
    assert report["paths"] == [[[schema, "customers"], [schema, "orders"], [schema, "items"], [schema, "products"]]]
    fk = next(edge for edge in context["foreign_keys"] if edge["from"][1] == "orders")
    assert fk["columns"] == ["tenant", "customer_id"]
    assert fk["referred_columns"] == ["tenant", "id"]
    assert fk["to"] == [schema, "customers"]
    customers = next(t for t in context["tables"] if t["table"] == "customers")
    assert customers["primary_key"] == ["tenant", "id"]
    assert [c["name"] for c in customers["columns"]] == ["tenant", "id", "customer_name"]
    assert "PRIVATE_ROW_NEVER_READ" not in docs[0].text
    assert json.loads(docs[0].text) == context
    assert calls and all("PRIVATE_ROW" not in call for call in calls)
    # Catalog queries are compared to engine metadata, not handwritten mock objects.
    with engine.connect() as conn:
        if schema == "main":
            raw = conn.exec_driver_sql("PRAGMA main.foreign_key_list(orders)").fetchall()
            assert [(r[3], r[4]) for r in raw] == [("tenant", "tenant"), ("customer_id", "id")]
        else:
            names = (
                conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_schema=:s AND table_name=:t ORDER BY ordinal_position"
                    ),
                    {"s": schema, "t": "customers"},
                )
                .scalars()
                .all()
            )
            assert names == [c["name"] for c in customers["columns"]]


@pytest.mark.parametrize(
    "options,reason", [({"max_hops": 2}, "no_path_within_hops"), ({"max_context_tables": 2}, "table_budget")]
)
def test_path_budgets(database, options, reason):
    docs, report = store(database, **options).query_with_report(Query(query_str="customers products"))
    assert len(docs[0].metadata["relational_schema"]["tables"]) == 2
    assert report["omitted_paths"][0]["reason"] == reason
    assert report["paths"] == []


def test_empty_cycles_and_external_fk(database):
    s = store(database)
    assert s.query(Query(query_str="unmatched")) == []
    assert s.query(Query(query_str="")) == []
    cycle = s.query(Query(query_str="cycles"))[0].metadata["relational_schema"]
    assert cycle["foreign_keys"][0]["from"] == cycle["foreign_keys"][0]["to"]
    s.tables = [pair for pair in s.tables if pair[1] != "orders"]
    docs, report = s.query_with_report(Query(query_str="items products"))
    assert any(edge["to"][1] == "orders" for edge in report["external_foreign_keys"])
    assert all(t["table"] != "orders" for t in docs[0].metadata["relational_schema"]["tables"])


@pytest.mark.parametrize(
    "options,message",
    [
        ({"max_columns": 1}, "max_columns"),
        ({"max_foreign_keys": 1}, "max_foreign_keys"),
        ({"max_context_chars": 1}, "max_context_chars"),
    ],
)
def test_catalog_output_budgets(database, options, message):
    with pytest.raises(ValueError, match=message):
        store(database, **options).query(Query(query_str="customers products"))


def test_readonly_business_rows_and_deterministic(database):
    s = store(database)
    a = s.query(Query(query_str="customers products"))[0]
    b = s.query(Query(query_str="products customers"))[0]
    assert a == b
    with pytest.raises(ValueError, match="similarity_top_k"):
        s.query(Query(query_str="customers", similarity_top_k=2))
    with pytest.raises(NotImplementedError):
        s.insert_document([])


def test_postgres_cross_schema_same_names_and_search_path():
    engine = create_engine(os.environ["AU_SCHEMA_POSTGRES_URL"])
    a, b = "b05a_" + uuid.uuid4().hex[:10], "b05b_" + uuid.uuid4().hex[:10]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {a}"))
            conn.execute(text(f"CREATE SCHEMA {b}"))
            conn.execute(text(f"CREATE TABLE {a}.entity (id INTEGER PRIMARY KEY, local_only TEXT)"))
            conn.execute(text(f"CREATE TABLE {b}.entity (id INTEGER PRIMARY KEY, remote_only TEXT)"))
            conn.execute(
                text(f"CREATE TABLE {a}.bridge (id INTEGER PRIMARY KEY, target INTEGER REFERENCES {b}.entity(id))")
            )

        # The target schema is visible on search_path: reflection must not guess
        # that an unqualified referred table belongs to the source schema.
        @event.listens_for(engine, "checkout")
        def search_path(dbapi_connection, record, proxy):
            cursor = dbapi_connection.cursor()
            cursor.execute(f"SET search_path TO {b}, public")
            cursor.close()

        s = RelationalSchemaStore(client=engine, tables=[(a, "entity"), (b, "entity"), (a, "bridge")], seed_limit=2)
        docs, report = s.query_with_report(Query(query_str="bridge remote_only"))
        context = docs[0].metadata["relational_schema"]
        assert context["foreign_keys"][0]["to"] == [b, "entity"]
        assert [t["schema"] for t in context["tables"] if t["table"] == "entity"] == [b]
        assert report["paths"]
    finally:
        with engine.begin() as conn:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {a} CASCADE"))
            conn.execute(text(f"DROP SCHEMA IF EXISTS {b} CASCADE"))
        engine.dispose()


def test_knowledge_public_query(database):
    from unittest.mock import patch

    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.configer import Configer

    managers = [StoreManager(), RagRouterManager()]
    pools = [dict(m._instance_obj_map) for m in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    knowledge = None
    try:
        config = Configer()
        config.value = {"BASE_INFO": {"appname": "schema-test"}}
        apps.app_configer = AppConfiger().load_by_configer(config)
        s = store(database)
        s.name = "schema_context"
        router = BaseRouter(name="base_router")
        for m, c in zip(managers, [s, router]):
            m.register(c.get_instance_code(), c)
        knowledge = Knowledge(stores=["schema_context"])
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            docs = knowledge.query_knowledge(query_str="customers products")
        assert len(docs) == 1
        assert len(docs[0].metadata["relational_schema"]["tables"]) == 4
    finally:
        if knowledge:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        for m, pool in zip(managers, pools):
            m._instance_obj_map.clear()
            m._instance_obj_map.update(pool)
        apps.app_configer = previous

import asyncio
import json
import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.myscale_store import MyScaleStore
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class FakeQueryResult:
    def __init__(self, rows):
        self.result_rows = rows


class FakeClient:
    """Mimics the subset of the clickhouse-connect client used by MyScaleStore."""

    def __init__(self, query_rows=None):
        self.commands = []
        self.inserts = []
        self.query_rows = query_rows or []

    def command(self, sql, parameters=None):
        self.commands.append((sql, parameters))
        return None

    def query(self, sql, parameters=None):
        self.last_sql = sql
        self.last_params = parameters
        return FakeQueryResult(self.query_rows)

    def insert(self, table, rows, column_names=None, database=None):
        self.inserts.append((database, table, column_names, list(rows)))


class MyScaleStoreTest(unittest.TestCase):
    def test_rejects_unsafe_table_name(self):
        with self.assertRaisesRegex(ValueError, "table_name"):
            MyScaleStore(table_name="docs; DROP")._validate_config(False)

    def test_rejects_unsafe_database_name(self):
        with self.assertRaisesRegex(ValueError, "database"):
            MyScaleStore(database="db; DROP")._validate_config(False)

    def test_rejects_unknown_distance_metric(self):
        with self.assertRaisesRegex(ValueError, "distance"):
            MyScaleStore(distance="manhattan")._validate_config(False)

    def test_rejects_invalid_port(self):
        with self.assertRaisesRegex(ValueError, "port"):
            MyScaleStore(port=99999)._validate_config(False)

    def test_invalid_top_k_fails_before_query(self):
        client = FakeClient()
        store = MyScaleStore(client=client, dimensions=2)
        with self.assertRaisesRegex(ValueError, "similarity_top_k"):
            store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=-1))
        # No query should have reached the client.
        self.assertEqual(client.commands, [])

    def test_query_requires_embedding(self):
        store = MyScaleStore(client=FakeClient(), dimensions=2)
        with self.assertRaisesRegex(ValueError, "requires embeddings"):
            store.query(Query(query_str="hello"))

    def test_rejects_dimension_mismatch(self):
        store = MyScaleStore(dimensions=3)
        with self.assertRaisesRegex(ValueError, "does not match"):
            store._check_vector([1.0, 2.0])

    def test_infers_dimension(self):
        store = MyScaleStore()
        store._check_vector([1.0, 2.0, 3.0])
        self.assertEqual(store.dimensions, 3)

    def test_create_table_sql_contains_array_type(self):
        store = MyScaleStore(dimensions=4, database="db", table_name="docs")
        sql = store._create_table_sql(4)
        self.assertIn("Array(Float32)", sql)
        self.assertIn("db.docs", sql)
        self.assertIn("MergeTree", sql)

    def test_distance_expression_uses_correct_function(self):
        self.assertIn("cosineDistance", MyScaleStore(distance="cosine")._distance_expr())
        self.assertIn("L2Distance", MyScaleStore(distance="l2")._distance_expr())
        self.assertIn("dotProduct", MyScaleStore(distance="inner_product")._distance_expr())

    def test_query_builds_sql_and_binds_vector_and_top_k(self):
        client = FakeClient()
        store = MyScaleStore(client=client, dimensions=2, table_name="docs")
        store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=7))
        self.assertIn("ORDER BY distance", client.last_sql)
        self.assertIn("cosineDistance", client.last_sql)
        self.assertEqual(client.last_params["p"], [1.0, 0.0])
        self.assertEqual(client.last_params["top_k"], 7)

    def test_query_with_metadata_filter(self):
        client = FakeClient()
        store = MyScaleStore(client=client, dimensions=2, table_name="docs")
        store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=3), metadata_filter={"team": "acme"})
        self.assertIn("JSONExtractString(metadata", client.last_sql)
        self.assertEqual(client.last_params["f_key_0"], "team")
        self.assertEqual(client.last_params["f_val_0"], "acme")

    def test_query_rejects_bad_filter_key(self):
        store = MyScaleStore(client=FakeClient(), dimensions=2, table_name="docs")
        with self.assertRaisesRegex(ValueError, "valid identifier"):
            store.query(Query(embeddings=[[1.0, 0.0]]), metadata_filter={"bad key!": "x"})

    def test_query_converts_rows_to_documents(self):
        rows = [("1", "hello", json.dumps({"team": "a"}), [0.1, 0.2], 0.5)]
        client = FakeClient(query_rows=rows)
        store = MyScaleStore(client=client, dimensions=2, table_name="docs")
        results = store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=5))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "1")
        self.assertEqual(results[0].text, "hello")
        self.assertEqual(results[0].metadata, {"team": "a"})
        self.assertEqual(results[0].embedding, [0.1, 0.2])

    def test_query_uses_embedding_component(self):
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = MyScaleStore(client=FakeClient(), dimensions=2, table_name="docs", embedding_model="embed")
        with patch("agentuniverse.agent.action.knowledge.store.myscale_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.query(Query(query_str="hello"))
        manager.return_value.get_instance_obj.assert_called_once_with("embed", strict=True)

    def test_upsert_inserts_parameterized_rows(self):
        client = FakeClient()
        store = MyScaleStore(client=client, dimensions=2, database="db", table_name="docs", create_table=False)
        store.upsert_document(
            [Document(id="1", text="hello", metadata={"a": 1}, embedding=[0.1, 0.2])]
        )
        database, table, columns, rows = client.inserts[0]
        self.assertEqual((database, table, columns), ("db", "docs", ["id", "text", "metadata", "embedding"]))
        self.assertEqual(rows[0][0], "1")
        self.assertEqual(json.loads(rows[0][2]), {"a": 1})
        self.assertEqual(rows[0][3], [0.1, 0.2])

    def test_upsert_generates_missing_embeddings(self):
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = MyScaleStore(client=FakeClient(), dimensions=2, embedding_model="embed", create_table=False)
        document = Document(id="1", text="hello")
        with patch("agentuniverse.agent.action.knowledge.store.myscale_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.upsert_document([document])
        self.assertEqual(document.embedding, [0.1, 0.2])

    def test_upsert_without_embeddings_requires_model(self):
        store = MyScaleStore(client=FakeClient(), dimensions=2, create_table=False)
        with self.assertRaisesRegex(ValueError, "embedding_model"):
            store.upsert_document([Document(id="1", text="hello")])

    def test_delete_is_parameterized(self):
        client = FakeClient()
        store = MyScaleStore(client=client, database="db", table_name="docs")
        store.delete_document("x' OR 1=1")
        sql, params = client.commands[-1]
        self.assertIn("DELETE FROM db.docs", sql)
        self.assertEqual(params, {"doc_id": "x' OR 1=1"})

    def test_new_client_creates_table_when_dimensions_known(self):
        driver = Mock()
        client = FakeClient()
        driver.get_client.return_value = client
        store = MyScaleStore(host="h", port=8123, dimensions=4, table_name="docs")
        with patch.object(store, "_dependencies", return_value=driver):
            store._new_client()
        driver.get_client.assert_called_once_with(
            host="h", port=8123, username=None, password=None, database="default", secure=True
        )
        self.assertTrue(any("CREATE TABLE" in cmd[0] for cmd in client.commands))

    def test_missing_dependency_hint(self):
        with patch.dict("sys.modules", {"clickhouse_connect": None}):
            with self.assertRaisesRegex(ImportError, "clickhouse-connect"):
                MyScaleStore._dependencies()

    def test_async_crud(self):
        rows = [("1", "async", json.dumps({}), [0.0, 1.0], 0.1)]
        client = FakeClient(query_rows=rows)
        store = MyScaleStore(client=client, dimensions=2, table_name="docs", create_table=False)

        async def run():
            await store.async_upsert_document([Document(id="1", text="async", embedding=[0.0, 1.0])])
            result = await store.async_query(Query(embeddings=[[0.0, 1.0]], similarity_top_k=1))
            await store.async_delete_document("1")
            return result

        result = asyncio.run(run())
        self.assertEqual(result[0].text, "async")
        self.assertEqual(len(client.inserts), 1)
        self.assertTrue(any("DELETE" in cmd[0] for cmd in client.commands))

    def test_component_schema(self):
        config = Configer()
        config.value = {
            "name": "myscale_store",
            "dimensions": 3,
            "metadata": {
                "type": "STORE",
                "module": "agentuniverse.agent.action.knowledge.store.myscale_store",
                "class": "MyScaleStore",
            },
        }
        component = ComponentConfiger().load_by_configer(config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.STORE.value)
        self.assertEqual(component.metadata_class, "MyScaleStore")


if __name__ == "__main__":
    unittest.main()

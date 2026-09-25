"""Opt-in real database tests; URL must name a disposable test_* database.

AGENTUNIVERSE_PGVECTOR_TEST_URL must use an administrator that can create roles
and install pgvector. Only uniquely named test roles and schemas are removed.
"""

import asyncio
import os
import secrets
import unittest
import uuid

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.query import Query


@unittest.skipUnless(os.getenv("AGENTUNIVERSE_PGVECTOR_TEST_URL"), "dedicated pgvector test database not configured")
class PGVectorPermissionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg
        from psycopg import sql
        from psycopg.conninfo import make_conninfo

        url = os.environ["AGENTUNIVERSE_PGVECTOR_TEST_URL"]
        cls.admin = psycopg.connect(url, autocommit=True)
        cls.addClassCleanup(cls.admin.close)
        if not cls.admin.info.dbname.startswith("test_"):
            message = "database name must start with test_; never use an application database"
            raise unittest.SkipTest(message)
        suffix = uuid.uuid4().hex[:12]
        cls.schema = "au_test_" + suffix
        role = "au_app_" + suffix
        password = secrets.token_urlsafe(24)
        cls.admin.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cls.admin.execute(
            sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(role), sql.Literal(password))
        )
        cls.addClassCleanup(cls.admin.execute, sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))
        cls.admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(cls.schema)))
        cls.addClassCleanup(cls.admin.execute, sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(cls.schema)))
        cls.admin.execute(sql.SQL("SET search_path TO {}, public").format(sql.Identifier(cls.schema)))
        cls.admin.execute(
            "CREATE TABLE docs (id TEXT PRIMARY KEY, text TEXT NOT NULL, metadata JSONB NOT NULL, embedding vector(2) NOT NULL)"
        )
        cls.admin.execute("INSERT INTO docs VALUES ('seed', 'original', '{\"team\": \"a\"}', '[1,0]')")
        cls.admin.execute(
            sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(sql.Identifier(cls.schema), sql.Identifier(role))
        )
        cls.admin.execute(sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON docs TO {}").format(sql.Identifier(role)))
        options = "-c search_path=" + cls.schema + ",public"
        cls.app_url = make_conninfo(url, user=role, password=password, options=options)
        cls.read_url = make_conninfo(cls.app_url, options=options + " -c default_transaction_read_only=on")
        cls.admin_url = make_conninfo(url, options=options)

    def store(self, *, read_only=False, automatic=False, table_name="docs"):
        return PGVectorStore(
            connection_url=self.admin_url if automatic else self.read_url if read_only else self.app_url,
            table_name=table_name,
            dimensions=2,
            create_table=automatic,
        )

    @staticmethod
    def query():
        return Query(embeddings=[[1.0, 0.0]], similarity_top_k=10)

    def test_sync_restricted_role_crud(self):
        store = self.store()
        try:
            self.assertEqual([d.id for d in store.query(self.query(), metadata_filter={"team": "a"})], ["seed"])
            self.assertFalse(
                store.client.execute(
                    "SELECT has_schema_privilege(current_user, current_schema(), 'CREATE')"
                ).fetchone()[0]
            )
            store.upsert_document([Document(id="sync", text="new", embedding=[0.0, 1.0])])
            store.update_document([Document(id="sync", text="updated", embedding=[0.0, 1.0])])
            self.assertEqual(next(d.text for d in store.query(self.query()) if d.id == "sync"), "updated")
            store.delete_document("sync")
            self.assertNotIn("sync", [d.id for d in store.query(self.query())])
        finally:
            if store.client:
                store.client.close()

    def test_sync_read_only_query(self):
        store = self.store(read_only=True)
        try:
            self.assertEqual([d.id for d in store.query(self.query())], ["seed"])
            self.assertEqual(store.client.execute("SHOW transaction_read_only").fetchone()[0], "on")
        finally:
            if store.client:
                store.client.close()

    def test_sync_default_creation(self):
        store = self.store(automatic=True, table_name="automatic_sync")
        try:
            store.insert_document([Document(id="one", text="created", embedding=[1.0, 0.0])])
            self.assertEqual([d.id for d in store.query(self.query())], ["one"])
            self.assertTrue(
                store.client.execute(
                    "SELECT EXISTS (SELECT FROM pg_indexes WHERE schemaname = current_schema() AND tablename = 'automatic_sync' AND indexdef LIKE '%USING hnsw%')"
                ).fetchone()[0]
            )
        finally:
            if store.client:
                store.client.close()

    def test_async_operations(self):
        asyncio.run(self.async_operations())

    async def async_operations(self):
        for read_only, automatic, table in [
            (False, False, "docs"),
            (True, False, "docs"),
            (False, True, "automatic_async"),
        ]:
            with self.subTest(read_only=read_only, automatic=automatic):
                store = self.store(read_only=read_only, automatic=automatic, table_name=table)
                try:
                    if not read_only:
                        await store.async_insert_document([Document(id="async", text="new", embedding=[0.0, 1.0])])
                        await store.async_update_document([Document(id="async", text="updated", embedding=[0.0, 1.0])])
                    documents = await store.async_query(self.query())
                    if read_only:
                        self.assertEqual([d.id for d in documents], ["seed"])
                        cursor = await store.async_client.execute("SHOW transaction_read_only")
                        self.assertEqual((await cursor.fetchone())[0], "on")
                    else:
                        self.assertEqual(next(d.text for d in documents if d.id == "async"), "updated")
                        await store.async_delete_document("async")
                        self.assertNotIn("async", [d.id for d in await store.async_query(self.query())])
                finally:
                    if store.async_client:
                        await store.async_client.close()


if __name__ == "__main__":
    unittest.main()

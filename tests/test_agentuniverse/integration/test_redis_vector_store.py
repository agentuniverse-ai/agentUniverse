"""Redis Search regressions; opt in with AGENTUNIVERSE_TEST_REDIS_URL.

Run against a disposable Redis 7+ instance with Search (PEXPIRETIME verifies
exact expiry preservation). Tests create unique indexes and key prefixes and
remove only their own resources.
"""

import asyncio
import os
import unittest
from uuid import uuid4

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore


@unittest.skipUnless(os.getenv("AGENTUNIVERSE_TEST_REDIS_URL"), "requires a Redis Search test URL")
class RedisVectorStoreIntegrationTest(unittest.TestCase):
    def setUp(self):
        import redis

        self.url = os.environ["AGENTUNIVERSE_TEST_REDIS_URL"]
        suffix = uuid4().hex
        self.index = f"au_test_{suffix}"
        self.prefix = f"au_test:{suffix}:"
        self.connection = redis.from_url(self.url, decode_responses=False)
        self.store = RedisVectorStore(
            connection_url=self.url,
            index_name=self.index,
            key_prefix=self.prefix,
            dimensions=2,
            filter_tag_fields=["category", "active"],
        )
        self.addCleanup(self.connection.close)
        self.addCleanup(self.cleanup_resources)

    def cleanup_resources(self):
        from redis.exceptions import ResponseError

        try:
            self.connection.execute_command("FT.DROPINDEX", self.index)
        except ResponseError as exc:
            if "unknown index" not in str(exc).lower():
                raise
        finally:
            self.connection.delete(f"{self.prefix}manual", f"{self.prefix}other")

    @staticmethod
    def document(metadata, document_id="manual"):
        return Document(id=document_id, text="Current manual", metadata=metadata, embedding=[1.0, 0.0])

    async def check_replacement(self, asynchronous):
        async def call(method, *args, **kwargs):
            if asynchronous:
                return await getattr(self.store, f"async_{method}")(*args, **kwargs)
            return getattr(self.store, method)(*args, **kwargs)

        async def matching_ids(metadata_filter=None):
            documents = await call(
                "query", Query(embeddings=[[1.0, 0.0]], similarity_top_k=10), metadata_filter=metadata_filter
            )
            return {document.id for document in documents}

        try:
            await call(
                "upsert_document",
                [
                    self.document({"category": "legacy", "active": True}),
                    self.document({"category": "retained", "active": False}, "other"),
                ],
            )
            self.assertEqual(await matching_ids({"category": "legacy"}), {"manual"})
            key = f"{self.prefix}manual"
            self.connection.hset(key, "application_note", "keep")
            self.connection.expire(key, 600)
            expiry = self.connection.execute_command("PEXPIRETIME", key)

            # Remove one indexed field while retaining another, including a false value.
            await call("update_document", [self.document({"active": False})])
            self.assertEqual(await matching_ids({"category": "legacy"}), set())
            self.assertEqual(await matching_ids({"active": False}), {"manual", "other"})
            self.assertIsNone(self.connection.hget(key, "meta_category"))

            # Remove all metadata, then repeat the replacement to check idempotence.
            for _ in range(2):
                await call("upsert_document", [self.document({})])
                self.assertEqual(await matching_ids({"active": False}), {"other"})
                self.assertEqual(await matching_ids(), {"manual", "other"})
                self.assertIsNone(self.connection.hget(key, "meta_active"))
                self.assertEqual(self.connection.hget(key, "metadata"), b"{}")

            # Reintroduce and change indexed values in a batch without losing other documents.
            await call(
                "upsert_document",
                [
                    self.document({"category": "current", "active": True}),
                    self.document({}, "other"),
                ],
            )
            self.assertEqual(await matching_ids({"category": "current", "active": True}), {"manual"})
            self.assertEqual(await matching_ids({"category": "retained"}), set())
            self.assertEqual(await matching_ids({"category": "legacy"}), set())
            self.assertEqual(self.connection.hget(key, "application_note"), b"keep")
            self.assertEqual(self.connection.execute_command("PEXPIRETIME", key), expiry)
        finally:
            if self.store.client is not None:
                self.store.client.close()
            if self.store.async_client is not None:
                await self.store.async_client.aclose()

    def test_sync_metadata_replacement(self):
        asyncio.run(self.check_replacement(False))

    def test_async_metadata_replacement(self):
        asyncio.run(self.check_replacement(True))


if __name__ == "__main__":
    unittest.main()

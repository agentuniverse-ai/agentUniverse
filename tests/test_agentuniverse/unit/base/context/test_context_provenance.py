import asyncio
import unittest
from datetime import datetime, timedelta, timezone

from agentuniverse.base.context.context_provenance import (
    AuthorityLevel,
    ContextProvenanceManager,
    ContextRecord,
    ContextScope,
    ContextSource,
    ContextStatus,
)


class ContextProvenanceManagerTest(unittest.TestCase):
    def setUp(self):
        self.manager = ContextProvenanceManager()
        self.manager.clear()

    def tearDown(self):
        self.manager.clear()

    def test_add_and_resolve(self):
        record = self.manager.add(
            "customer", {"tier": "gold"}, ContextSource.USER, ContextScope.SESSION, AuthorityLevel.USER
        )
        self.assertIsInstance(record, ContextRecord)
        self.assertEqual(self.manager.resolve("customer"), {"tier": "gold"})

    def test_deep_copies_mutable_values(self):
        value = {"items": [1]}
        self.manager.add("state", value, "user")
        value["items"].append(2)
        resolved = self.manager.resolve("state")
        resolved["items"].append(3)
        self.assertEqual(self.manager.resolve("state"), {"items": [1]})

    def test_higher_authority_supersedes_lower(self):
        low = self.manager.add("region", "guessed", "agent", authority=AuthorityLevel.AGENT)
        high = self.manager.add("region", "confirmed", "user", authority=AuthorityLevel.USER)
        self.assertEqual(self.manager.get(low.id).status, ContextStatus.SUPERSEDED)
        self.assertIsNotNone(self.manager.get(low.id).status_changed_at)
        self.assertIn(low.id, high.supersedes)
        self.assertEqual(self.manager.resolve("region"), "confirmed")

    def test_historical_resolution_survives_supersession(self):
        first_at = datetime.now(timezone.utc) - timedelta(minutes=2)
        second_at = first_at + timedelta(minutes=1)
        self.manager.add("region", "old", "agent", observed_at=first_at)
        self.manager.add("region", "new", "user", observed_at=second_at)
        self.assertEqual(self.manager.resolve("region", at=first_at), "old")
        self.assertEqual(self.manager.resolve("region", at=second_at), "new")

    def test_lower_authority_cannot_supersede_higher(self):
        system = self.manager.add("policy", "required", "system", authority=AuthorityLevel.SYSTEM)
        agent = self.manager.add("policy", "optional", "agent", authority=AuthorityLevel.AGENT)
        self.assertEqual(self.manager.get(system.id).status, ContextStatus.ACTIVE)
        self.assertEqual(self.manager.resolve("policy"), "required")
        self.assertEqual({record.id for record in self.manager.conflicts("policy")}, {system.id, agent.id})

    def test_same_value_is_not_conflict(self):
        self.manager.add("currency", "USD", "tool", supersede=False)
        self.manager.add("currency", "USD", "agent", supersede=False)
        self.assertEqual(self.manager.conflicts("currency"), [])

    def test_scope_filter(self):
        self.manager.add("language", "turn", "user", scope=ContextScope.TURN, supersede=False)
        self.manager.add("language", "session", "user", scope=ContextScope.SESSION, supersede=False)
        self.assertEqual(self.manager.resolve("language", ContextScope.TURN), "turn")
        self.assertEqual(self.manager.resolve("language", ContextScope.SESSION), "session")

    def test_confidence_breaks_authority_tie(self):
        self.manager.add("answer", "low", "agent", authority=10, confidence=0.4, supersede=False)
        self.manager.add("answer", "high", "agent", authority=10, confidence=0.9, supersede=False)
        self.assertEqual(self.manager.resolve("answer"), "high")

    def test_expired_record_is_not_active(self):
        now = datetime.now(timezone.utc)
        record = self.manager.add("token", "value", "tool", observed_at=now, expires_at=now + timedelta(seconds=1))
        self.assertEqual(self.manager.resolve("token", at=now + timedelta(seconds=2)), None)
        self.assertTrue(record.is_active(now))

    def test_future_observation_is_not_active_early(self):
        now = datetime.now(timezone.utc)
        observed = now + timedelta(minutes=1)
        self.manager.add("forecast", "current", "tool", observed_at=now)
        record = self.manager.add("forecast", "ready", "tool", observed_at=observed)
        self.assertFalse(record.is_active(now))
        self.assertEqual(self.manager.resolve("forecast", at=now), "current")
        self.assertEqual(self.manager.resolve("forecast", at=observed), "ready")

    def test_rejects_expiry_before_observation(self):
        now = datetime.now(timezone.utc)
        with self.assertRaisesRegex(ValueError, "later"):
            self.manager.add("x", 1, "tool", observed_at=now, expires_at=now)

    def test_rejects_naive_datetime(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            self.manager.add("x", 1, "tool", observed_at=datetime.now())

    def test_promotion_preserves_parent_and_authority(self):
        source = self.manager.add("decision", "approve", "user", scope=ContextScope.TURN, authority=AuthorityLevel.USER)
        promoted = self.manager.promote(source.id, ContextScope.SESSION)
        self.assertEqual(promoted.parent_id, source.id)
        self.assertEqual(promoted.authority, AuthorityLevel.USER)
        self.assertEqual(promoted.scope, ContextScope.SESSION)

    def test_promotion_cannot_escalate_authority(self):
        source = self.manager.add("decision", "draft", "agent", authority=AuthorityLevel.AGENT)
        with self.assertRaisesRegex(ValueError, "cannot increase"):
            self.manager.promote(source.id, ContextScope.SESSION, AuthorityLevel.USER)

    def test_promotion_requires_wider_scope(self):
        source = self.manager.add("decision", "x", "agent", scope=ContextScope.SESSION)
        with self.assertRaisesRegex(ValueError, "wider"):
            self.manager.promote(source.id, ContextScope.TURN)

    def test_rejected_record_cannot_be_promoted(self):
        source = self.manager.add("decision", "x", "agent")
        self.manager.set_status(source.id, ContextStatus.REJECTED)
        with self.assertRaisesRegex(ValueError, "only active"):
            self.manager.promote(source.id, ContextScope.SESSION)

    def test_status_transition(self):
        record = self.manager.add("claim", "x", "agent")
        updated = self.manager.set_status(record.id, ContextStatus.REJECTED)
        self.assertEqual(updated.status, ContextStatus.REJECTED)
        self.assertEqual(self.manager.resolve("claim"), None)

    def test_terminal_status_cannot_be_reactivated(self):
        record = self.manager.add("claim", "x", "agent")
        self.manager.set_status(record.id, ContextStatus.REJECTED)
        with self.assertRaisesRegex(ValueError, "terminal"):
            self.manager.set_status(record.id, ContextStatus.ACTIVE)
        self.assertEqual(self.manager.get(record.id).status, ContextStatus.REJECTED)

    def test_snapshot_restore_and_reset(self):
        self.manager.add("one", 1, "user")
        snapshot = self.manager.snapshot()
        self.manager.add("two", 2, "user")
        token = self.manager.restore(snapshot)
        self.assertEqual(self.manager.resolve("two"), None)
        self.manager.reset(token)
        self.assertEqual(self.manager.resolve("two"), 2)

    def test_export_is_serializable_shape(self):
        self.manager.add("one", 1, "user", scope=ContextScope.TASK, authority=AuthorityLevel.USER)
        exported = self.manager.export()[0]
        self.assertEqual(exported["source"], "user")
        self.assertEqual(exported["scope"], "task")
        self.assertEqual(exported["authority"], "user")
        self.assertIn("observed_at", exported)

    def test_invalid_confidence(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            self.manager.add("x", 1, "agent", confidence=1.1)

    def test_async_context_isolation(self):
        async def worker(value):
            self.manager.clear()
            self.manager.add("worker", value, "agent")
            await asyncio.sleep(0)
            return self.manager.resolve("worker")

        async def run():
            return await asyncio.gather(worker("a"), worker("b"))

        self.assertEqual(asyncio.run(run()), ["a", "b"])
        self.assertIsNone(self.manager.resolve("worker"))


if __name__ == "__main__":
    unittest.main()

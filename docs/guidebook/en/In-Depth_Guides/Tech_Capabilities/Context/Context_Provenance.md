# Context Provenance

`ContextProvenanceManager` is an opt-in foundation for context engineering. It keeps immutable values with `source`, `observed_at`, `confidence`, `scope`, `authority`, expiry, actor, and lineage instead of mixing user facts, tool observations, and agent inferences in an untyped dictionary.

```python
from agentuniverse.base.context import AuthorityLevel, ContextProvenanceManager, ContextScope

manager = ContextProvenanceManager()
manager.add("customer_region", "APAC", source="agent", authority=AuthorityLevel.AGENT)
manager.add("customer_region", "EMEA", source="user", authority=AuthorityLevel.USER, scope=ContextScope.SESSION)
region = manager.resolve("customer_region")
```

Records with equal key and scope are superseded only by a new record of equal or greater authority. Lower-authority contradictions remain observable through `conflicts()` but cannot override system/user facts during `resolve()`. `promote()` moves a record from turn to task/session/global scope while preserving lineage and forbidding authority escalation. Expiry, rejection, history, export, snapshots, and async-task isolation are supported. Existing `FrameworkContextManager` behavior is unchanged.

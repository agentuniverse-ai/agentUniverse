# Component registration aliases

Component aliases provide a migration window when an agent, tool, model, or
other configured component is renamed. Register the canonical component first,
then add an alternative bare name through its manager:

```python
manager.register_alias(
    alias_name="legacy_search",
    target_name="web_search",
)

tool = manager.get_instance_obj("legacy_search")
```

Alias lookups preserve normal manager behavior, including defensive copies and
strict lookup errors. Targets may themselves be aliases; the manager stores the
resolved canonical code so alias chains cannot form cycles. Collisions and
missing targets are rejected.

Use `get_alias_map()` for introspection. `unregister_alias()` removes only the
alternative name and never unregisters the canonical component. Alias and
target names belong to the same application and component manager.

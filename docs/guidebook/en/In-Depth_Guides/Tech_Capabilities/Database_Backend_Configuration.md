# Database-backed configuration repository

`SQLConfigRepository` stores versioned component dictionaries on any SQLAlchemy engine,
including the existing `SQLDBWrapper` engine. Writes are transactional and use optimistic
revision checks; every revision has an audit row and rollback creates another visible revision.
Environments are isolated. Raw secret-like fields are rejected in favor of `secret_ref` values.

`as_configer()` returns the existing `Configer` contract, so component configurers do not need a
second parsing architecture. `LayeredConfigResolver` applies defaults, YAML, database and runtime
overrides in that order, preserving YAML compatibility during migration.

## Runtime integration

Pass the repository to the normal bootstrap. Matching records overlay YAML by component `name`;
records that do not have a YAML counterpart are also loaded. Repository failures abort startup
rather than silently producing a partially overridden component graph.

```python
from sqlalchemy import create_engine
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.config.repository import SQLConfigRepository

repository = SQLConfigRepository(create_engine("sqlite:///components.db"))
repository.put(
    "LLM", "default_openai_llm",
    {"temperature": 0.2, "api_key": "${OPENAI_API_KEY}"},
    environment="production", expected_revision=0,
)
AgentUniverse().start(
    component_config_repository=repository,
    config_environment="production",
)
```

Database values may be partial overlays. Database-only values must include enough `metadata`
(`type`, `module`, and `class`) to initialize the component. Secret-like values accept structured
`secret_ref` objects, `env://`/`vault://` URIs, or existing `${ENV_VAR}` placeholders; literal
secrets are rejected.

## Migration and rollback

```python
from pathlib import Path
from agentuniverse.base.config.repository import (
    export_yaml_directory, import_yaml_files,
)

report = import_yaml_files(
    repository, Path("intelligence").rglob("*.yaml"),
    environment="staging", dry_run=True,
)
assert not report.errors

# Run again without dry_run, then keep the generated audit revision.
import_yaml_files(repository, Path("intelligence").rglob("*.yaml"),
                  environment="staging")
repository.rollback("TOOL", "search", revision=1,
                    environment="staging", expected_revision=2)
export_yaml_directory(repository, "config-export", environment="staging")
```

Use `expected_revision` on updates and deletes to prevent lost updates. Imports preserve
`${ENV_VAR}` placeholders instead of resolving them on the migration host.

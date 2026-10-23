# Offline component configuration preflight

Before starting services, inspect explicitly selected YAML components from one application:

```sh
python -m agentuniverse.base.config.preflight path/to/agent.yaml path/to/knowledge.yaml
```

The JSON graph contains typed node IDs, reference edges with file/field locations,
and diagnostics. Exit codes: 0 = declared scope checked, 1 = errors, 2 = unresolved.
It never imports configured classes, evaluates `@FUNC`, reads environment variables,
constructs components, starts services or changes registrations.

For custom classes and built-ins outside the selected files, use explicit declarations:

```python
from agentuniverse.base.config.preflight import inspect_components

report = inspect_components(
    ["knowledge.yaml"],
    class_types={"myapp.Library": "KNOWLEDGE"},
    external=["STORE:sqlite", "READER:text"],
    capabilities={"STORE:sqlite": ["keyword-query"]},
    requirements={"STORE:sqlite": ["keyword-query"]},
)
```

`class_types` takes precedence when `meta_class` is present, because runtime type
resolution instantiates that class. External IDs and capabilities are **caller
assertions**, never proof of installation or runtime support. Missing required
capability declarations produce unresolved diagnostics.

Built-in reference rules cover Agent's profile LLM/prompt, planner, memories,
tools, toolkits and knowledge, plus Knowledge's stores/readers/processors/router/
paraphrasers. Other types report partial coverage. Extend the rules explicitly with
`reference_fields={"TOOL": {"delegate": "TOOL"}}`; `*` selects list items or mapping
values. Empty rule maps can explicitly declare no reference fields. Cycles in these
selected references are reported; they do not necessarily imply runtime deadlock.

Names follow `info.name` for agents, prompt metadata version (or the runtime path
fallback), and `name` for other types. Duplicate names are errors within a type,
even when runtime registration would retain the first entry. This tool cannot
infer names supplied by custom Python constructors. It does not scan directories,
import packages, infer default LLM/router dependencies, resolve application TOML,
validate every class-specific field, inspect SQL overlays or model inheritance.
A checked result applies only to the reported coverage and selected namespace.
Dynamic values remain unresolved rather than being guessed.

Input is bounded by file count, bytes, nesting depth and expanded YAML node count.
Duplicate keys, non-string mapping keys and YAML merge keys are rejected to avoid
ambiguous graphs. Reports exclude raw parser excerpts and configuration values;
component names, file paths and reference names are included, so review reports
before sharing. The selected files remain unchanged.

Tests compare real KnowledgeConfiger identities and PromptManager registration,
inspect shipped examples, block sockets in a fresh subprocess, and exercise
missing/type-mismatched references, cycles, aliases, malformed YAML, bounds and CLI
exit codes. No provider/service availability is claimed.

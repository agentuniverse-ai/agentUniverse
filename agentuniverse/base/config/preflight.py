"""Offline, declaration-only component graph checks; never imports configured classes.

Use ``python -m agentuniverse.base.config.preflight files...``. This is a
partial preflight, not proof that application startup or a provider will work.
"""

import argparse
import json
from pathlib import Path

import yaml

from agentuniverse.base.component.component_enum import ComponentEnum

# These paths mirror lookups in Agent and Knowledge, not arbitrary YAML names.
REFERENCE_FIELDS = {
    "AGENT": {
        "profile.llm_model.name": "LLM",
        "profile.prompt_version": "PROMPT",
        "plan.planner.name": "PLANNER",
        "memory.name": "MEMORY",
        "memory.conversation_memory": "MEMORY",
        "action.tool.*": "TOOL",
        "action.toolkit.*": "TOOLKIT",
        "action.knowledge.*": "KNOWLEDGE",
    },
    "KNOWLEDGE": {
        "stores.*": "STORE",
        "readers.*": "READER",
        "insert_processors.*": "DOC_PROCESSOR",
        "post_processors.*": "DOC_PROCESSOR",
        "query_paraphrasers.*": "QUERY_PARAPHRASER",
        "rag_router": "RAG_ROUTER",
    },
}


class _Loader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently changing the effective graph."""

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError("mapping keys must be unique strings")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def _dynamic(value):
    return isinstance(value, str) and ("@FUNC" in value or "${" in value)


def _walk(value, path="", ancestors=(), budget=None):
    if budget is None:
        budget = [100_000]
    budget[0] -= 1
    if budget[0] < 0:
        raise ValueError("expanded YAML node limit exceeded")
    if isinstance(value, (dict, list)):
        if id(value) in ancestors or len(ancestors) >= 64:
            raise ValueError("recursive or excessively nested YAML")
        ancestors = (*ancestors, id(value))
        children = value.items() if isinstance(value, dict) else enumerate(value)
        for key, child in children:
            yield from _walk(child, f"{path}.{key}".lstrip("."), ancestors, budget)
    else:
        yield path, value


def _select(value, parts, path=""):
    if value is None:
        return
    if not parts:
        yield path, value
    elif parts[0] == "*":
        if isinstance(value, (list, dict)):
            children = value.items() if isinstance(value, dict) else enumerate(value)
            for key, child in children:
                yield from _select(child, parts[1:], f"{path}.{key}".lstrip("."))
        else:
            yield path, None
    elif isinstance(value, dict) and parts[0] in value:
        yield from _select(value[parts[0]], parts[1:], f"{path}.{parts[0]}".lstrip("."))
    elif not isinstance(value, dict):
        yield path, value


def inspect_components(
    paths,
    *,
    class_types=None,
    external=(),
    reference_fields=None,
    capabilities=None,
    requirements=None,
    max_files=2000,
    max_file_bytes=1_048_576,
):
    """Inspect explicitly selected YAML files and return a JSON-compatible graph.

    Args:
        paths: Component files from one application namespace (no directory scan).
        class_types: Explicit meta_class -> ComponentEnum value declarations.
        external: Known external IDs, e.g. ``STORE:sqlite``; existence is asserted
            by the caller, not verified against an installed application.
        reference_fields: Extra type -> dotted field -> target type declarations.
            ``*`` selects a list's items or a mapping's values. No code executes.
        capabilities: Component ID -> declared capability names.
        requirements: Component ID -> required capability names, checked only
            against declarations. No runtime capability introspection occurs.
        max_files: Maximum selected files.
        max_file_bytes: Per-file UTF-8 byte limit.

    Returns:
        Nodes, edges, diagnostics, coverage and a ``status`` of error, unresolved
        or checked. ``checked`` applies only to the declared scope.

    Raises:
        ValueError: Invalid limits or caller declarations.
    """
    for limit in (max_files, max_file_bytes):
        if type(limit) is not int or limit <= 0:
            raise ValueError("limits must be positive integers")
    types = set(ComponentEnum.to_value_list())
    rules = {kind: dict(fields) for kind, fields in REFERENCE_FIELDS.items()}
    for kind, fields in (reference_fields or {}).items():
        if kind not in types or not isinstance(fields, dict):
            raise ValueError("invalid reference field declaration")
        for field, target in fields.items():
            if not isinstance(field, str) or not field or not isinstance(target, str) or target not in types:
                raise ValueError("invalid reference field declaration")
        rules.setdefault(kind, {}).update(fields)
    class_types = class_types or {}
    if any(not isinstance(k, str) or not isinstance(v, str) or v not in types for k, v in class_types.items()):
        raise ValueError("invalid class type declaration")
    external = set(external)
    for key in external:
        if not isinstance(key, str) or ":" not in key or key.split(":", 1)[0] not in types:
            raise ValueError("external IDs must be TYPE:name")
    for declarations in (capabilities or {}, requirements or {}):
        for key, values in declarations.items():
            if not isinstance(key, str) or not isinstance(values, (list, tuple, set)):
                raise ValueError("capabilities must map IDs to collections of strings")
            if any(not isinstance(value, str) or not value for value in values):
                raise ValueError("capabilities must be nonempty strings")
    files = []
    for path in paths:
        files.append(Path(path))
        if len(files) > max_files:
            raise ValueError("file count limit exceeded")
    files = sorted(set(files), key=str)
    nodes, edges, diagnostics = [], [], []
    configs, index = {}, {}

    def issue(code, file, field, detail, severity="error"):
        diagnostics.append(dict(code=code, file=str(file), field=field, detail=detail, severity=severity))

    for file in files:
        try:
            with file.open("rb") as stream:
                raw = stream.read(max_file_bytes + 1)
            if len(raw) > max_file_bytes:
                raise ValueError("file byte limit exceeded")
            data = yaml.load(raw.decode("utf-8"), Loader=_Loader)
            if not isinstance(data, dict):
                raise ValueError("component must be a mapping")
            leaves = list(_walk(data))
        except (OSError, UnicodeError, ValueError, yaml.YAMLError, RecursionError) as exc:
            # Avoid quoting config values or parser excerpts that could contain secrets.
            issue("invalid_yaml", file, "$", type(exc).__name__)
            continue
        for field, value in leaves:
            if _dynamic(value):
                issue("dynamic_value", file, field, "not evaluated", "unresolved")
        metadata = data.get("metadata") or {}
        if not isinstance(metadata, dict):
            issue("invalid_metadata", file, "metadata", "expected mapping")
            continue
        kind = metadata.get("type")
        meta_class = data.get("meta_class")
        if meta_class:
            kind = class_types.get(meta_class) if isinstance(meta_class, str) else None
            if kind is None:
                issue("dynamic_type", file, "meta_class", "requires explicit class_types declaration", "unresolved")
                continue
        elif not metadata and "prompt" in str(file):
            kind = "PROMPT"
        if _dynamic(kind):
            continue
        if not isinstance(kind, str) or kind not in types:
            issue("unknown_type", file, "metadata.type", "expected ComponentEnum value")
            continue
        if kind == "AGENT":
            info = data.get("info", {})
            name = info.get("name") if isinstance(info, dict) else None
            name_field = "info.name"
        elif kind == "PROMPT":
            name = metadata.get("version") if metadata else f"{file.parent.name}.{file.stem}"
            name_field = "metadata.version"
        else:
            name, name_field = data.get("name"), "name"
        if _dynamic(name):
            continue
        if not isinstance(name, str) or not name.strip():
            issue("missing_name", file, name_field, "requires a literal nonempty name")
            continue
        key = f"{kind}:{name}"
        node = dict(id=key, type=kind, name=name, file=str(file))
        nodes.append(node)
        if key in index or key in external:
            issue("duplicate_name", file, name_field, key)
        index.setdefault(key, []).append(node)
        configs[str(file)] = data
        if kind not in rules:
            issue("partial_coverage", file, "$", "no reference fields declared for this type", "unresolved")

    available = set(index) | external
    for node in nodes:
        for pattern, target_type in rules.get(node["type"], {}).items():
            for field, value in _select(configs[node["file"]], pattern.split(".")):
                if _dynamic(value):
                    continue
                if not isinstance(value, str) or not value.strip():
                    issue("invalid_reference", node["file"], field, "expected literal component name")
                    continue
                target = f"{target_type}:{value}"
                edges.append(dict(source=node["id"], target=target, file=node["file"], field=field))
                if target not in available:
                    alternatives = sorted(key for key in available if key.split(":", 1)[1] == value)
                    issue("wrong_type" if alternatives else "missing_reference", node["file"], field, target)
    # Iterative reachability avoids recursion limits on long valid graphs.
    adjacency = {key: set() for key in index}
    for edge in edges:
        if edge["target"] in index:
            adjacency[edge["source"]].add(edge["target"])
    for edge in edges:
        pending, visited = [edge["target"]], set()
        while pending:
            key = pending.pop()
            if key == edge["source"]:
                issue("cycle", edge["file"], edge["field"], f"{edge['source']} -> {edge['target']}")
                break
            if key not in visited:
                visited.add(key)
                pending.extend(adjacency.get(key, ()))
    for key, required in sorted((requirements or {}).items()):
        missing = set(required) - set((capabilities or {}).get(key, ()))
        if key not in available or missing:
            issue(
                "capability_unresolved",
                "<declarations>",
                key,
                "component absent or required capabilities not declared",
                "unresolved",
            )
    status = "checked"
    if any(item["severity"] == "unresolved" for item in diagnostics):
        status = "unresolved"
    if any(item["severity"] == "error" for item in diagnostics):
        status = "error"
    return dict(
        status=status,
        nodes=nodes,
        edges=edges,
        diagnostics=diagnostics,
        coverage=rules,
        external=sorted(external),
        scope="selected files; literal declared references; no runtime validation",
    )


def main():
    """Print deterministic JSON; exit 0 checked, 1 errors, 2 unresolved."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    report = inspect_components(args.files)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return {"checked": 0, "error": 1, "unresolved": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())

"""Bridge versioned repository records into the existing YAML loader."""
# ruff: noqa: TRY003
from __future__ import annotations

import copy
from pathlib import Path

from agentuniverse.base.config.configer import Configer, PlaceholderResolver
from agentuniverse.base.config.repository.base import ConfigRecord, ConfigRepository
from agentuniverse.base.config.repository.layered import deep_merge


def component_config_name(configer: Configer) -> str:
    """Return the stable repository key for a file-backed configuration."""
    name = (configer.value or {}).get("name")
    if name:
        return str(name)
    return Path(configer.path or "unnamed").stem


def _record_configer(record: ConfigRecord, base: Configer | None = None) -> Configer:
    value = deep_merge(base.value, record.value) if base else copy.deepcopy(record.value)
    value.setdefault("name", record.name)
    metadata_type = (value.get("metadata") or {}).get("type")
    if metadata_type and metadata_type != record.component_type:
        raise ValueError(
            f"database record {record.component_type}/{record.name} contains "
            f"metadata.type={metadata_type}"
        )
    value = PlaceholderResolver().resolve(value)
    configer = Configer(path=(
        f"db://{record.environment}/{record.component_type}/"
        f"{record.name}@{record.revision}"
    ))
    configer.value = value
    return configer


def merge_repository_configers(
        file_configers: list[Configer], repository: ConfigRepository,
        component_type: str, environment: str = "default") -> list[Configer]:
    """Overlay database records onto YAML and append database-only components.

    YAML remains the compatibility baseline. A matching database record wins at
    every key it defines, while omitted keys continue to come from YAML. A
    repository error is deliberately propagated so startup cannot silently run
    with a partially applied configuration set.
    """
    records = repository.list(component_type=component_type,
                              environment=environment)
    records_by_name = {record.name: record for record in records}
    result: list[Configer] = []
    consumed: set[str] = set()
    for configer in file_configers:
        name = component_config_name(configer)
        record = records_by_name.get(name)
        if record is None:
            result.append(configer)
            continue
        result.append(_record_configer(record, configer))
        consumed.add(name)
    for name in sorted(records_by_name.keys() - consumed):
        result.append(_record_configer(records_by_name[name]))
    return result

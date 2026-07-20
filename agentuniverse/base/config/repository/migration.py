"""Import/export helpers for migrating YAML component configuration."""
# ruff: noqa: TRY003, TRY301
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from agentuniverse.base.config.repository.base import ConfigRepository
from agentuniverse.base.config.repository.sql_repository import ConfigNotFoundError


@dataclass
class MigrationReport:
    imported: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def import_yaml_files(repository: ConfigRepository, paths: Iterable[str | Path], *,
                      environment: str = "default", updated_by: str = "migration",
                      overwrite: bool = False, dry_run: bool = False) -> MigrationReport:
    """Import component YAML without resolving environment placeholders."""
    report = MigrationReport()
    for raw_path in paths:
        path = Path(raw_path)
        try:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise TypeError("component YAML must contain a mapping")
            component_type = (value.get("metadata") or {}).get("type")
            if not component_type:
                raise ValueError("metadata.type is required")
            name = str(value.get("name") or path.stem)
            key = f"{component_type}/{name}"
            expected_revision = 0
            try:
                current = repository.get(component_type, name, environment)
            except ConfigNotFoundError:
                current = None
            if current is not None and not overwrite:
                report.skipped.append(key)
                continue
            if current is not None:
                expected_revision = current.revision
            if not dry_run:
                repository.put(component_type, name, value,
                               environment=environment,
                               expected_revision=expected_revision,
                               updated_by=updated_by)
            report.imported.append(key)
        except Exception as exc:  # collect all invalid files for one migration run
            report.errors.append(f"{path}: {exc}")
    return report


def export_yaml_directory(repository: ConfigRepository, target: str | Path, *,
                          environment: str = "default",
                          overwrite: bool = False) -> list[Path]:
    """Export current records into ``TYPE/name.yaml`` files."""
    target = Path(target)
    written: list[Path] = []
    for record in repository.list(environment=environment):
        component_dir = target / record.component_type.lower()
        component_dir.mkdir(parents=True, exist_ok=True)
        path = component_dir / f"{record.name}.yaml"
        if path.exists() and not overwrite:
            raise FileExistsError(path)
        path.write_text(
            yaml.safe_dump(record.value, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        written.append(path)
    return written

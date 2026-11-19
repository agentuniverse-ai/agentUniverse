"""Contracts shared by component-configuration repositories."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from agentuniverse.base.config.configer import Configer


@dataclass(frozen=True)
class ConfigRecord:
    """A versioned component configuration stored outside the source tree."""

    component_type: str
    name: str
    environment: str
    value: dict
    revision: int
    updated_at: datetime
    updated_by: str

    def as_configer(self) -> Configer:
        """Return a regular ``Configer`` understood by component configurers."""
        configer = Configer(
            path=(f"db://{self.environment}/{self.component_type}/"
                  f"{self.name}@{self.revision}")
        )
        configer.value = copy.deepcopy(self.value)
        return configer


class ConfigRepository(Protocol):
    """Minimal repository contract required by the agentUniverse loader."""

    def get(self, component_type: str, name: str,
            environment: str = "default") -> ConfigRecord:
        ...

    def list(self, component_type: str | None = None,
             environment: str = "default") -> list[ConfigRecord]:
        ...

    def put(self, component_type: str, name: str, value: dict, *,
            environment: str = "default", expected_revision: int | None = None,
            updated_by: str = "system") -> ConfigRecord:
        ...

from dataclasses import dataclass
from typing import Optional, Dict, Any

from ..component.component_enum import ComponentEnum
from ..config.configer import Configer


@dataclass
class StorageContext:
    """
    Context for configuration storage operations.
    """
    raw_path: str
    trimmed_path: Optional[str] = None
    configer_type: Optional[ComponentEnum] = None
    configer: Optional[Configer] = None
    metadata: Dict[str, Any] = None

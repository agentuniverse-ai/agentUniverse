from typing import Optional, Dict, Any
from ..component.component_enum import ComponentEnum
from ..config.configer import Configer


def _check_and_trim_path(path: str, root_package_name: Optional[str]) -> Optional[str]:
    """
    Ensure path contains root_package_name, and return trimmed path.
    """
    if not path or not root_package_name:
        return None
    idx = path.find(root_package_name)
    return None if idx == -1 else path[idx:]


class StorageContext:
    """
    Context for configuration storage operations.
    """

    def __init__(
        self,
        instance_code: str,
        root_package_name: Optional[str] = None,
        configer_type: Optional[ComponentEnum] = None,
        configer: Optional[Configer] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.instance_code = instance_code
        self.raw_path = configer.path if configer else None
        self.trimmed_path = _check_and_trim_path(self.raw_path, root_package_name) if self.raw_path else None
        self.configer_type = configer_type
        self.configer = configer
        self.metadata = metadata or {}


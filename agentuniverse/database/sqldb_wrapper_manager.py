from ..base.annotation.singleton import singleton
from ..base.component.component_enum import ComponentEnum
from ..base.component.component_manager_base import ComponentManagerBase
from .sqldb_wrapper import SQLDBWrapper


@singleton
class SQLDBWrapperManager(ComponentManagerBase[SQLDBWrapper]):
    """A singleton manager class of the DBWrapper."""

    def __init__(self):
        super().__init__(ComponentEnum.SQLDB_WRAPPER)

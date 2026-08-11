"""Manager for context compressor components."""

from agentuniverse.agent.context.compressor.context_compressor import ContextCompressor
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class ContextCompressorManager(ComponentManagerBase[ContextCompressor]):
    """A singleton manager for ContextCompressor instances."""

    def __init__(self):
        super().__init__(ComponentEnum.CONTEXT_COMPRESSOR)

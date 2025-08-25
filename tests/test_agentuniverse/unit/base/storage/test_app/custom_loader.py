from agentuniverse.base.config.configer import Configer
from agentuniverse.base.storage.loader.base_config_loader import BaseConfigLoader
from agentuniverse.base.storage.storage_context import StorageContext


class CustomConfigLoader(BaseConfigLoader):
    def __init__(self, configer: Configer):
        super().__init__(configer)

    def load(self, ctx: StorageContext):
        print(f"Loading config for {ctx.trimmed_path}")

    def save(self, ctx: StorageContext):
        print(f"Saving config for {ctx.trimmed_path}")

    def delete(self, ctx: StorageContext):
        pass

    def _get_key(self, name):
        pass

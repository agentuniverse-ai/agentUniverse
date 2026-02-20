# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/23 17:49
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agentuniverse_product.py
import sys

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.component.application_component_manager import ApplicationComponentManager
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.base.util.system_util import get_project_root_path
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_configer import ProductConfiger
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.dal.message_library import MESSAGE_TABLE_NAME, MessageORM
from agentuniverse_product.dal.session_library import SESSION_TABLE_NAME, SessionORM


@singleton
class AgentUniverseProduct(object):
    """Initialize the agentUniverse product."""

    def __init__(self):
        self.__application_container = ApplicationComponentManager()
        self.__config_container: ApplicationConfigManager = ApplicationConfigManager()
        self.__system_default_product_package = []

    def start(self, config_path: str = None):
        """Start the agentUniverse product."""
        # get default config path
        project_root_path = get_project_root_path()
        sys.path.append(str(project_root_path.parent))
        self._add_to_sys_path(project_root_path, ['platform', 'app'])
        if not config_path:
            config_path = project_root_path / 'config' / 'config.toml'
            config_path = str(config_path)

        # load the configuration file
        configer = Configer(path=config_path).load()

        # init product tables (session and message)
        self.__init_product_tables()

        # scan and register the product components
        self.__scan_and_register_product(self.__config_container.app_configer)

        # start the product ui server
        config = configer.value.get('MAGENT_UI', {})
        try:
            from magent_ui import launch
        except ImportError as e:
            print(e)
            raise ImportError(
                "Could not start product server provided by magent-ui."
                " Please install it with `pip install magent-ui ruamel.yaml`."
            )
        launch(**config)

    def __init_product_tables(self):
        """Initialize the product tables including session and message tables."""
        system_sqldb_wrapper = SQLDBWrapperManager().get_instance_obj('__system_db__')
        if system_sqldb_wrapper is None:
            raise Exception('system db has not been initialized.')
        with system_sqldb_wrapper.engine.connect() as conn:
            # init session db
            if not conn.dialect.has_table(conn, SESSION_TABLE_NAME):
                SessionORM.metadata.create_all(
                    system_sqldb_wrapper.engine)
            # init message db
            if not conn.dialect.has_table(conn, MESSAGE_TABLE_NAME):
                MessageORM.metadata.create_all(
                    system_sqldb_wrapper.engine)

    def __scan_and_register_product(self, app_configer: AppConfiger):
        """Scan the product component directory and register the product components.

        Args:
            app_configer(AppConfiger): the AppConfiger object
        """
        core_product_package_list = ((app_configer.core_product_package_list or app_configer.core_default_package_list)
                                     + self.__system_default_product_package)
        if core_product_package_list is None:
            return
        product_configer_list = AgentUniverse().scan(core_product_package_list, ConfigTypeEnum.YAML,
                                                     ComponentEnum.PRODUCT)
        self.__register(product_configer_list)

    def __register(self, product_configer_list: list[ComponentConfiger]):
        """Register the product components.

        Args:
            product_configer_list(list): the product component configer list
        """
        for product_configer in product_configer_list:
            configer_instance: ProductConfiger = ProductConfiger(
            ).load_by_configer(product_configer.configer)
            component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(
                configer_instance)
            product_instance: Product = component_clz(
            ).initialize_by_component_configer(configer_instance)
            if product_instance is None:
                continue
            product_instance.component_config_path = product_configer.configer.path
            ProductManager().register(product_instance.get_instance_code(), product_instance)

    def _add_to_sys_path(self, root_path, sub_dirs):
        for sub_dir in sub_dirs:
            app_path = root_path / sub_dir
            if app_path.exists():
                sys.path.append(str(app_path))

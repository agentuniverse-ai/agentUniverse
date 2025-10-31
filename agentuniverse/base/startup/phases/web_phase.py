# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: web_phase.py

import importlib

from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext
from agentuniverse.agent_serve.web.request_task import RequestLibrary
from agentuniverse.agent_serve.web.rpc.grpc.grpc_server_booster import set_grpc_config
from agentuniverse.agent_serve.web.web_booster import ACTIVATE_OPTIONS
from agentuniverse.agent_serve.web.web_util import FlaskServerManager


class WebPhase(StartupPhase):
    """Web services initialization phase.

    This phase initializes:
    1. Web request task database
    2. HTTP server configuration
    3. gRPC server (if enabled)
    4. Gunicorn server (if enabled)
    5. Extension modules

    It depends on CONFIG, LOGGING, and TELEMETRY phases.
    """

    def __init__(self):
        """Initialize the web phase."""
        super().__init__(StartupPhaseEnum.WEB)

    def execute(self, context: StartupContext) -> None:
        """Execute the web services initialization phase.

        Args:
            context: The startup context

        Raises:
            Exception: If web services initialization fails
        """
        try:
            configer = context.configer

            # Initialize web request task database
            RequestLibrary(configer=configer)

            # Configure HTTP server timeout
            sync_service_timeout = configer.value.get('HTTP_SERVER', {}).get('sync_service_timeout')
            if sync_service_timeout:
                FlaskServerManager().sync_service_timeout = sync_service_timeout

            # Initialize gRPC if enabled
            grpc_activate = configer.value.get('GRPC', {}).get('activate')
            if grpc_activate and grpc_activate.lower() == 'true':
                ACTIVATE_OPTIONS["grpc"] = True
                set_grpc_config(configer)

            # Initialize Gunicorn if enabled
            gunicorn_activate = configer.value.get('GUNICORN', {}).get('activate')
            if gunicorn_activate and gunicorn_activate.lower() == 'true':
                ACTIVATE_OPTIONS["gunicorn"] = True
                if context.gunicorn_config_path:
                    from agentuniverse.agent_serve.web.gunicorn_server import GunicornApplication
                    GunicornApplication(config_path=context.gunicorn_config_path)

            # Initialize extension modules
            self._init_extension_modules(configer, context)

            # Mark phase as completed
            self._mark_completed()

        except Exception as e:
            self._mark_failed(e)
            raise

    def rollback(self, context: StartupContext) -> None:
        """Rollback the web phase.

        Args:
            context: The startup context

        Note:
            Web service cleanup is complex and typically handled by
            the respective managers. This is a no-op for safety.
        """
        pass

    def get_dependencies(self) -> list[StartupPhaseEnum]:
        """Return the list of phases this phase depends on.

        Returns:
            List containing CONFIG, LOGGING, and TELEMETRY phases
        """
        return [StartupPhaseEnum.CONFIG, StartupPhaseEnum.LOGGING, StartupPhaseEnum.TELEMETRY]

    def _init_extension_modules(self, configer, context: StartupContext) -> None:
        """Initialize extension modules.

        Args:
            configer: The configuration object
            context: The startup context
        """
        ext_classes = configer.value.get('EXTENSION_MODULES', {}).get('class_list')
        if not isinstance(ext_classes, list):
            return

        for ext_class in ext_classes:
            if "YamlFuncExtension" in ext_class:
                # Store YAML function extension instance in config container
                instance = self._dynamic_import_and_init(ext_class)
                context.config_container.app_configer.yaml_func_instance = instance
            else:
                # Initialize other extensions with configer
                self._dynamic_import_and_init(ext_class, configer)

    def _dynamic_import_and_init(self, class_path: str, configer=None):
        """Dynamically import and initialize a class.

        Args:
            class_path: Full class path like package_name.class_name
            configer: Optional configer to pass to constructor

        Returns:
            Instance of the imported class
        """
        module_path, _, class_name = class_path.rpartition('.')
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls(configer) if configer else cls()

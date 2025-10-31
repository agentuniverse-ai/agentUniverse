# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: config_phase.py

import sys
from pathlib import Path

from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.custom_configer.custom_key_configer import CustomKeyConfiger
from agentuniverse.base.util.system_util import get_project_root_path
from agentuniverse.base.util import character_util


class ConfigPhase(StartupPhase):
    """Configuration loading phase.

    This phase handles:
    1. Loading the main configuration file
    2. Loading custom keys (API keys, secrets)
    3. Parsing sub-configuration paths
    4. Setting up the application configuration manager

    Note: This phase loads configuration ONCE, eliminating the duplicate
    loading issue in the original implementation.
    """

    def __init__(self):
        """Initialize the configuration phase."""
        super().__init__(StartupPhaseEnum.CONFIG)

    def execute(self, context: StartupContext) -> None:
        """Execute the configuration loading phase.

        Args:
            context: The startup context

        Raises:
            Exception: If configuration loading fails
        """
        try:
            # Show startup banner
            character_util.show_au_start_banner()

            # Get project root path and update sys.path
            project_root_path = get_project_root_path()
            context.project_root_path = project_root_path
            sys.path.append(str(project_root_path.parent))
            self._add_to_sys_path(project_root_path, ['intelligence', 'app'])

            # Determine config path
            if not context.config_path:
                context.config_path = str(project_root_path / 'config' / 'config.toml')

            # Load main configuration
            configer = Configer(path=context.config_path).load()

            # Parse and load custom key configuration first
            custom_key_configer_path = self._parse_sub_config_path(
                configer.value.get('SUB_CONFIG_PATH', {}).get('custom_key_path'),
                context.config_path
            )
            context.custom_key_configer_path = custom_key_configer_path

            # Initialize custom key configer (this loads API keys into environment)
            if custom_key_configer_path:
                CustomKeyConfiger(custom_key_configer_path)

            # Reload configuration after custom keys are loaded
            # This allows config values to reference environment variables set by custom keys
            configer = Configer(path=context.config_path).load()
            context.configer = configer

            # Load application configuration
            app_configer = AppConfiger().load_by_configer(configer)
            context.app_configer = app_configer

            # Initialize configuration container
            config_container = ApplicationConfigManager()
            config_container.app_configer = app_configer
            context.config_container = config_container

            # Parse other sub-configuration paths
            context.log_config_path = self._parse_sub_config_path(
                configer.value.get('SUB_CONFIG_PATH', {}).get('log_config_path'),
                context.config_path
            )

            context.gunicorn_config_path = self._parse_sub_config_path(
                configer.value.get('GUNICORN', {}).get('gunicorn_config_path'),
                context.config_path
            )

            # Mark phase as completed
            self._mark_completed()

        except Exception as e:
            self._mark_failed(e)
            raise

    def rollback(self, context: StartupContext) -> None:
        """Rollback the configuration phase.

        Args:
            context: The startup context
        """
        # Clear configuration objects
        context.configer = None
        context.app_configer = None
        context.config_container = None

    def get_dependencies(self) -> list[StartupPhaseEnum]:
        """Return the list of phases this phase depends on.

        Returns:
            Empty list (no dependencies)
        """
        return []

    def _parse_sub_config_path(self, input_path: str, reference_file_path: str) -> str | None:
        """Resolve a sub config file path according to main config file.

        Args:
            input_path: Absolute or relative path of sub config file
            reference_file_path: Main config file path

        Returns:
            A file path or None when no such file
        """
        if not input_path:
            return None

        input_path_obj = Path(input_path)
        if input_path_obj.is_absolute():
            combined_path = input_path_obj
        else:
            reference_file_path_obj = Path(reference_file_path)
            combined_path = reference_file_path_obj.parent / input_path_obj

        return str(combined_path)

    def _add_to_sys_path(self, root_path: Path, sub_dirs: list[str]) -> None:
        """Add subdirectories to sys.path.

        Args:
            root_path: The root path
            sub_dirs: List of subdirectory names
        """
        for sub_dir in sub_dirs:
            app_path = root_path / sub_dir
            if app_path.exists():
                sys.path.append(str(app_path))

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/28 17:31
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: config_extension.py
from agentuniverse.base.config.configer import Configer


class ConfigExtension:
    """Extension hook for custom application configuration.

    Its ``__init__`` is invoked during agentUniverse initialization, allowing
    users to load extra configuration or initialize external services.
    """

    def __init__(self, configer: Configer) -> None:
        """
        This method is automatically executed during the initialization of the agentUniverse.
        It serves as a hook for users to define custom initialization logic for the application.

        For example, this method can be used to:
            - Load additional configuration files.
            - Initialize external services or APIs.
            - Set up default values or environment variables required by the application.
        """
        pass

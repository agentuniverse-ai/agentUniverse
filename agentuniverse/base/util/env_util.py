# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 11:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: env_util.py

import os


def get_from_env(env_key: str) -> str:
    """Read the value of an environment variable.

    Args:
        env_key: The name of the environment variable to look up.

    Returns:
        The environment variable's value if it is set and non-empty,
        otherwise None.
    """
    if env_key in os.environ and os.environ[env_key]:
        return os.environ[env_key]

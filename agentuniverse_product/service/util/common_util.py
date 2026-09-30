# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/30 20:30
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: common_util.py
import os
from pathlib import Path


def dict_does_not_contain_keys(d: dict, keys: list) -> bool:
    """Check if the dictionary does not contain any of the specified keys."""
    return all(key not in d for key in keys)


def get_core_path():
    """Resolve the platform core directory path when it exists.

    Returns:
        Path or None: The core path, or None when no core directory is found.
    """
    if os.path.exists(os.path.join('..', 'core')):
        return Path(os.path.join('..', 'core'))
    elif os.path.exists(os.path.join('..', '..', 'app', 'core')):
        return Path(os.path.join('..', '..', 'app', 'core'))
    return None


def get_resources_path():
    """Resolve the platform resources directory path.

    Returns:
        Path: The resources directory path.
    """
    if os.path.exists(os.path.join('..', '..', 'platform', 'difizen', 'resources')):
        return Path(os.path.join('..', '..', 'platform', 'difizen', 'resources'))
    elif os.path.exists(os.path.join('..', 'resources')):
        return Path(os.path.join('..', 'resources'))
    else:
        return Path(os.path.join('..', '..', 'app', 'resources'))

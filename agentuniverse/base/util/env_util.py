# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 11:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: env_util.py

import os


def get_from_env(env_key: str) -> str:
    if env_key in os.environ and os.environ[env_key]:
        return os.environ[env_key]

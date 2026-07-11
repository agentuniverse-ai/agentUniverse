# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/29 10:21
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: __init__.py
try:
    from agentuniverse.base.util.platform_import_guard import ensure_stdlib_platform
except ModuleNotFoundError:
    pass
else:
    ensure_stdlib_platform(__name__, __file__)

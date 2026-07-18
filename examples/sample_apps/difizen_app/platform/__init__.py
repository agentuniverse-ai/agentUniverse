# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/15 16:47
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: __init__.py
try:
    from agentuniverse.base.util.platform_import_guard import ensure_stdlib_platform
except ModuleNotFoundError:
    pass
else:
    ensure_stdlib_platform(__name__, __file__)

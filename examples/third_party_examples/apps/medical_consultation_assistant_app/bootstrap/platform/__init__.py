# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/02 12:23
# @Author  : zhangxi
# @Email   : 1724585800@qq.com
# @FileName: __init__.py
try:
    from agentuniverse.base.util.platform_import_guard import ensure_stdlib_platform
except ModuleNotFoundError:
    pass
else:
    ensure_stdlib_platform(__name__, __file__)

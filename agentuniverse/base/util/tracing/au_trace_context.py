# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/6 17:21
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: au_trace_context.py

import warnings

from agentuniverse.base.tracing import au_trace_context as new_module


def __getattr__(name):
    if hasattr(new_module, name):
        warnings.warn(
            f"Importing {name} from 'agentuniverse.base.util.tracing.au_trace_context' "
            "is deprecated and will be removed in future. "
            f"Please use 'from agentuniverse.base.tracing.au_trace_context import {name}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(new_module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = getattr(new_module, "__all__", [])

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/3 14:13
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: trace_manager.py
import warnings

from agentuniverse.base.tracing import au_trace_manager as new_module


def __getattr__(name):
    if hasattr(new_module, name):
        warnings.warn(
            f"Importing {name} from 'agentuniverse.base.util.tracing.au_trace_manager' "
            "is deprecated and will be removed in future. "
            f"Please use 'from agentuniverse.base.tracing.au_trace_manager import {name}' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return getattr(new_module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = getattr(new_module, '__all__', [])

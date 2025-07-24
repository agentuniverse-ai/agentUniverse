# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/24 15:33
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: after_register_queue.py
from typing import List, Tuple, Callable, Any

FunctionWithArgs = Tuple[Callable, Tuple[Any, ...], dict]
AFTER_REGISTER_QUEUE: List[FunctionWithArgs] = []


def add_after_register(func: Callable, *args: Any, **kwargs: Any) -> None:
    """
    Add funcs and parameters into a waiting list, all of them will be executed
    after all component registered, and before post fork queue
    """

    AFTER_REGISTER_QUEUE.append((func, args, kwargs))

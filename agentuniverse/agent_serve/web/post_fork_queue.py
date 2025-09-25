# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/3 23:09
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: post_fork_queue.py

from typing import List, Tuple, Callable, Any

FunctionWithArgs = Tuple[Callable, Tuple[Any, ...], dict]
POST_FORK_QUEUE: List[FunctionWithArgs] = []


def add_post_fork(func: Callable, *args: Any, **kwargs: Any) -> None:
    """
    Add func and parameters into a waiting list, all of them will be executed
    after gunicorn worker child processes have been forked, or before flask
    main app start if you work without gunicorn.
    """

    POST_FORK_QUEUE.append((func, args, kwargs))



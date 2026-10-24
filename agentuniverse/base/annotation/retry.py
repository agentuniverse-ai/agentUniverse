# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/28 17:46
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: retry.py

import functools
import math
import time
from typing import Any, Callable


def retry(max_retries: int = 3, delay: float = 1.0) -> Callable:
    """Retry a synchronous callable after exceptions.

    Args:
        max_retries: Maximum number of invocation attempts.
        delay: Seconds to wait between failed attempts.

    Returns:
        A decorator that preserves the wrapped callable's metadata and
        re-raises the final exception unchanged when all attempts fail.
    """
    if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 1:
        raise ValueError("max_retries must be a positive integer")
    if (
        isinstance(delay, bool)
        or not isinstance(delay, (int, float))
        or not math.isfinite(delay)
        or delay < 0
    ):
        raise ValueError("delay must be a non-negative number")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            last_exception = None
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    retries += 1
                    if retries < max_retries:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

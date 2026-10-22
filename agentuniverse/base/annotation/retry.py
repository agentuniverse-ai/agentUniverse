# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/28 17:46
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: retry.py

import functools
import time
from typing import Any, Callable


def retry(max_retries: int = 3, delay: float = 1.0) -> Callable:
    """Return a decorator that retries the wrapped callable on failure.

    Args:
        max_retries: The maximum number of attempts for the callable.
        delay: The number of seconds to wait between attempts.

    Returns:
        Callable: the decorator that applies the retry behavior.
    """
    def decorator(func: Callable) -> Callable:
        """Wrap the given callable with retry logic.

        Args:
            func: The callable to invoke and retry on exception.

        Returns:
            Callable: the retry-enabled wrapper around ``func``.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Execute func, retrying until success or retries are exhausted.

            Args:
                args: Positional arguments forwarded to the wrapped callable.
                kwargs: Keyword arguments forwarded to the wrapped callable.

            Returns:
                Any: the result of the wrapped callable.

            Raises:
                Exception: if the callable fails on every attempt.
            """
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
            raise Exception(f"Failed after {max_retries} retries. Last error: {str(last_exception)}")
        return wrapper
    return decorator

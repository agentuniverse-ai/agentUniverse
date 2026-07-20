# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/28 17:46
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: retry.py

import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


def retry(max_retries: int = 3, delay: float = 1.0) -> Callable:
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
                        logger.debug("retry %s attempt %d/%d failed: %s",
                                     func.__name__, retries, max_retries, e)
                        time.sleep(delay)
            # Preserve the original exception type and traceback instead of
            # wrapping it in a bare Exception. Callers that catch specific
            # types (HttpError, TimeoutError, ...) will now work, and the
            # full stack trace is retained for diagnosis.
            raise last_exception
        return wrapper
    return decorator

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 14:31
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: thread_with_result.py

from concurrent.futures import ThreadPoolExecutor, Future
from threading import Thread
from typing import Callable

from opentelemetry import context as otel_context

from agentuniverse.base.context.context_coordinator import ContextCoordinator


class ThreadWithReturnValue(Thread):
    """A thread can save the target func exec result."""

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None):
        super().__init__(group, target, name, args, kwargs)

        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs
        self.args = args
        self.target = target
        self._return = None
        self.error = None
        self._context_pack = ContextCoordinator.save_context()

    def run(self):
        """Run the target func and save result in _return."""
        if self.target is not None:
            # set the context values in the thread
            otel_token = ContextCoordinator.recover_context(self._context_pack)
            try:
                self._return = self.target(*self.args, **self.kwargs)
            except BaseException as e:
                # Transport target failures to result(), including cancellation/exit.
                self.error = e
            finally:
                if otel_token:
                    otel_context.detach(otel_token)

    def result(self):
        """Wait for target func finished, then return the result or raise an
        error, including BaseException subclasses raised by the target.
        """
        self.join()
        if self.error is not None:
            raise self.error
        return self._return


class ContextAwareFuture(Future):
    """A Future that can store context and error information."""

    def __init__(self):
        super().__init__()
        self.error = None
        self._context_pack = None


class ThreadPoolExecutorWithReturnValue(ThreadPoolExecutor):
    """A ThreadPoolExecutor that preserves context across threads."""

    def submit(self, fn: Callable, *args, **kwargs) -> ContextAwareFuture:
        """Submit a callable with context preservation.

        Target failures, including BaseException subclasses, are delivered
        through the returned future's result/exception methods.
        """
        context_pack = ContextCoordinator.save_context()
        future = ContextAwareFuture()
        future._context_pack = context_pack

        def context_wrapper():
            otel_token = None
            try:
                otel_token = ContextCoordinator.recover_context(context_pack)

                result = fn(*args, **kwargs)

            except BaseException as e:
                # Match executor failure transport so the outer future
                # does not remain pending after a target exits.
                future.error = e
                future.set_exception(e)

            else:
                # Completion callbacks are not part of the target's failure.
                future.set_result(result)

            finally:
                if otel_token:
                    otel_context.detach(otel_token)

        super().submit(context_wrapper)

        return future

    def map(self, func: Callable, *iterables, timeout=None, chunksize=1):
        """Apply func to each element of iterables with context preservation."""
        context_pack = ContextCoordinator.save_context()

        def context_aware_func(*args):
            otel_token = None
            try:
                otel_token = ContextCoordinator.recover_context(context_pack)
                return func(*args)
            except Exception as e:
                raise e
            finally:
                if otel_token:
                    otel_context.detach(otel_token)

        return super().map(context_aware_func, *iterables,
                           timeout=timeout, chunksize=chunksize)

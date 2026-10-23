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
            except Exception as e:
                self.error = e
            finally:
                if otel_token:
                    otel_context.detach(otel_token)

    def result(self):
        """Wait for target func finished, then return the result or raise an
        error."""
        self.join()
        if self.error is not None:
            raise self.error
        return self._return


class ContextAwareFuture(Future):
    """A Future that can store context and error information.

    `ThreadPoolExecutorWithReturnValue.submit()` builds one of these in front of
    the real future returned by `super().submit()`, so the two have to agree on
    their state. `cancel()` is delegated to the underlying future: a `Future`
    that reports a successful cancel while the work keeps running makes the
    caller believe a side effect was prevented when it was not.
    """

    def __init__(self, inner: Future | None = None):
        super().__init__()
        self.error = None
        self._context_pack = None
        self._inner = inner

    def cancel(self):
        """Cancel the work through the future that actually owns it."""
        if self._inner is None:
            return super().cancel()
        cancelled = self._inner.cancel()
        if cancelled:
            super().cancel()
        return cancelled

    def cancelled(self):
        if self._inner is not None and self._inner.cancelled():
            return True
        return super().cancelled()

    def running(self):
        if self._inner is not None:
            return self._inner.running()
        return super().running()

    def done(self):
        if self._inner is not None:
            return self._inner.done()
        return super().done()


class ThreadPoolExecutorWithReturnValue(ThreadPoolExecutor):
    """A ThreadPoolExecutor that preserves context across threads."""

    def submit(self, fn: Callable, *args, **kwargs) -> ContextAwareFuture:
        """Submit a callable to be executed with context preservation."""
        context_pack = ContextCoordinator.save_context()
        future = ContextAwareFuture()
        future._context_pack = context_pack

        def context_wrapper():
            otel_token = None
            try:
                otel_token = ContextCoordinator.recover_context(context_pack)

                result = fn(*args, **kwargs)
                future.set_result(result)

            except Exception as e:
                future.error = e
                future.set_exception(e)

            finally:
                if otel_token:
                    otel_context.detach(otel_token)

        # Keep the real future: `ContextAwareFuture.cancel()` has to reach it,
        # otherwise a cancel reports success while the callable still runs.
        inner = super().submit(context_wrapper)
        future._inner = inner

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

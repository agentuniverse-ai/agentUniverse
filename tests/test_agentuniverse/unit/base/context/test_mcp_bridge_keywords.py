"""Exercise keyword forwarding with real AnyIO portals and cleanup stacks."""

import asyncio
from contextlib import asynccontextmanager, closing
from contextvars import ContextVar
import threading
import unittest

from agentuniverse.base.context.mcp_session_manager import (
    MCPSessionManager, SyncAsyncExitStack,
)


class MCPBridgeKeywordTests(unittest.TestCase):
    def test_async_keyword_only_arguments_run_on_portal_thread(self):
        caller = threading.get_ident()

        async def operation(*, message, enabled):
            await asyncio.sleep(0)
            return message, enabled, threading.get_ident()

        with closing(SyncAsyncExitStack()) as stack:
            message, enabled, worker = stack.run_async(
                operation, message='hello', enabled=False)
        self.assertEqual((message, enabled), ('hello', False))
        self.assertNotEqual(worker, caller)

    def test_async_mixed_arguments_and_kwargs_are_forwarded(self):
        async def operation(first, *rest, multiplier, **options):
            return (first + sum(rest)) * multiplier, options

        with closing(SyncAsyncExitStack()) as stack:
            self.assertEqual(stack.run_async(operation, 2, 3, 4,
                                             multiplier=2, label='value', empty=None),
                             (18, {'label': 'value', 'empty': None}))

    def test_async_exception_is_propagated_without_replacement(self):
        failure = ValueError('target failed')

        async def operation(*, fail):
            if fail:
                raise failure

        with closing(SyncAsyncExitStack()) as stack:
            with self.assertRaises(ValueError) as raised:
                stack.run_async(operation, fail=True)
        self.assertIs(raised.exception, failure)

    def test_positional_only_call_is_preserved(self):
        async def operation(value, /):
            return value * 2

        with closing(SyncAsyncExitStack()) as stack:
            self.assertEqual(stack.run_async(operation, 3), 6)

    def test_callback_kwargs_are_deferred_and_callback_identity_is_preserved(self):
        events = []

        def record(value, *, label):
            events.append((value, label))

        with closing(SyncAsyncExitStack()) as stack:
            registered = stack.callback(record, 3, label='closed')
            self.assertIs(registered, record)
            self.assertEqual(events, [])
        self.assertEqual(events, [(3, 'closed')])

    def test_keyword_callbacks_keep_lifo_cleanup_order(self):
        events = []

        def record(*, value):
            events.append(value)

        with closing(SyncAsyncExitStack()) as stack:
            stack.callback(record, value='first')
            stack.callback(record, value='second')
        self.assertEqual(events, ['second', 'first'])

    def test_async_context_is_closed_after_keyword_call_failure(self):
        events = []

        @asynccontextmanager
        async def resource():
            events.append('opened')
            try:
                yield 'resource'
            finally:
                events.append('closed')

        async def operation(*, message):
            raise ValueError(message)

        with closing(SyncAsyncExitStack()) as stack:
            self.assertEqual(stack.enter_async_context(resource()), 'resource')
            with self.assertRaisesRegex(ValueError, 'target failed'):
                stack.run_async(operation, message='target failed')
        self.assertEqual(events, ['opened', 'closed'])

    def test_manager_delegate_forwards_keyword_arguments(self):
        manager = MCPSessionManager()
        previous = manager.save_mcp_session()

        async def operation(*, value):
            return value

        try:
            with closing(SyncAsyncExitStack()) as stack:
                manager.recover_mcp_session({}, stack)
                self.assertEqual(manager.run_async(operation, value='delegated'), 'delegated')
        finally:
            manager.recover_mcp_session(**previous)

    def test_caller_context_is_propagated_for_keyword_calls(self):
        context = ContextVar('bridge_keyword_test')
        token = context.set('caller')

        async def operation(*, suffix):
            value = context.get() + suffix
            context.set('worker')
            return value

        try:
            with closing(SyncAsyncExitStack()) as stack:
                self.assertEqual(stack.run_async(operation, suffix=' context'), 'caller context')
            self.assertEqual(context.get(), 'caller')
        finally:
            context.reset(token)


if __name__ == '__main__':
    unittest.main()

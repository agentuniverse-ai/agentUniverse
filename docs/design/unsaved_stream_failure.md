# Stream failures without persistence

`RequestTask(saved=False)` disables database persistence, not the in-memory
request state machine. If the worker result raises an ordinary exception,
`receive_steps`, `user_receive_steps`, and `async_receive_steps` record its
error message and transition from `running` to `fail` before yielding the SSE
error event. This also holds when the consumer closes immediately after that
event. Database access still occurs only for saved requests.

Previously the three handlers put both state updates inside the persistence
condition. Unsaved streams emitted an error while `request_state()` remained
`running` and the in-memory result stayed empty. The synchronous `run` and
background `append_steps` paths already separated state from persistence.

This change does not alter SSE payloads, cancellation, successful async
completion, timeout polling, or database-write failure handling. It does not
catch cancellation or other `BaseException` subclasses.

## Regression coverage

The regression suite covers both direct consumer generators and the public
`stream_run`, `user_stream_run`, and `async_stream_run` entry points. Public
entry-point tests use actual worker threads (with Flask test request context
copying) and scheduled coroutine producers. Each producer emits a partial
chunk before raising, then signals EOF. Tests verify chunk format, the
`running` state during partial output, the `fail` state and recorded error
before the error event is consumed, and cleanup after exhaustion or early
consumer close. Saved requests update persistence once; unsaved requests
never instantiate the persistence library.
Direct consumer tests also cover both supported end markers, `EOF_SIGNAL`
and `None`, for synchronous and asynchronous failure paths.

Persistence and trace-ID lookup are mocked. These are local integration tests,
not a live HTTP/provider/database test. EOF-free worker failures, database
write failures and cancellation remain outside this regression's scope.

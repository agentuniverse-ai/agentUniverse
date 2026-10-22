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

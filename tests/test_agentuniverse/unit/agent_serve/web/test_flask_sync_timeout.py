import time
from concurrent.futures import TimeoutError

import pytest

from agentuniverse.agent_serve.web.flask_server import _run_with_timeout


def test_run_with_timeout_does_not_wait_for_worker_completion():
    started_at = time.monotonic()

    with pytest.raises(TimeoutError):
        _run_with_timeout(lambda: time.sleep(0.5), timeout=0.01)

    assert time.monotonic() - started_at < 0.2

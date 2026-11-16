import pytest

from agentuniverse.base.annotation.retry import retry


def test_retry_returns_after_a_later_attempt_succeeds():
    attempts = 0

    @retry(max_retries=2, delay=0)
    def flaky():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("temporary")
        return "ok"

    assert flaky() == "ok"
    assert attempts == 2


def test_retry_reraises_the_final_exception_instance():
    error = ValueError("permanent")

    @retry(max_retries=2, delay=0)
    def failing():
        raise error

    with pytest.raises(ValueError) as raised:
        failing()

    assert raised.value is error


@pytest.mark.parametrize(
    ("max_retries", "delay"),
    [(0, 0), (True, 0), (1, -1), (1, True), (1, float("nan")), (1, float("inf"))],
)
def test_retry_rejects_invalid_configuration(max_retries, delay):
    with pytest.raises(ValueError):
        retry(max_retries=max_retries, delay=delay)

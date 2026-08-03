"""Retry policy for workflow node execution."""

from pydantic import BaseModel, Field, model_validator


class RetryPolicyConfigurationError(ValueError):
    """Raised when retry delay bounds are inconsistent."""

    def __init__(self):
        super().__init__('initial_delay cannot be greater than max_delay')


class RetryPolicy(BaseModel):
    """Deterministic retry settings for an individual workflow node.

    ``max_attempts`` includes the first execution. A value of one therefore
    preserves the existing fail-fast behavior.
    """

    max_attempts: int = Field(default=1, ge=1)
    initial_delay: float = Field(default=0, ge=0)
    backoff_multiplier: float = Field(default=2, ge=1)
    max_delay: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_delay_bounds(self) -> 'RetryPolicy':
        if self.max_delay is not None and self.initial_delay > self.max_delay:
            raise RetryPolicyConfigurationError
        return self

    def delay_before_attempt(self, attempt: int) -> float:
        """Return the delay before a retry attempt numbered from two."""
        if attempt < 2:
            return 0
        delay = self.initial_delay * self.backoff_multiplier ** (attempt - 2)
        if self.max_delay is not None:
            delay = min(delay, self.max_delay)
        return delay

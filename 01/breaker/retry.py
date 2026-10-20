import time
from collections.abc import Callable
from typing import TypeVar

from .backoff import exponential_backoff
from .circuit_breaker import CircuitBreaker

T = TypeVar("T")

def call_with_breaker_and_retry[T](
    fn: Callable[[], T],
    breaker: CircuitBreaker,
    max_retries: int = 3,
) -> T:
    if max_retries < 1:
        raise ValueError("max_retries must be >= 1")
        
    for attempt in range(max_retries):
        if not breaker.allow():
            raise RuntimeError("circuit_open")
        breaker.before_call()
        try:
            result = fn()
            breaker.on_success()
            return result
        except Exception:
            breaker.on_failure()
            if attempt == max_retries - 1:
                raise
            time.sleep(exponential_backoff(attempt))

    raise RuntimeError("unreachable: retry loop exited without returning")
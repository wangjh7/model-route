# 复用 01 熔断 + 重试
from breaker import CircuitBreaker, call_with_breaker_and_retry

from .billing import BillingLedger
from .fallback import LLMResult, fallback_invoke
from .router import route_by_complexity
from .type import Complexity, Provider, ProviderOutput


def invoke_with_pipeline(
    user_msg: str,
    complexity: Complexity,
    providers: dict[str, Provider],
    breaker: CircuitBreaker,
    ledger: BillingLedger,
    max_retries: int = 2,
) -> LLMResult:
    """闭环：路由 → 熔断 → 重试 → 降级 → 计费。"""
    decision = route_by_complexity(complexity)
    primary_fn = providers[decision.model]

    def _call() -> ProviderOutput:
        return primary_fn(user_msg)

    try:
        raw = call_with_breaker_and_retry(_call, breaker, max_retries=max_retries)
        result = LLMResult(
            text=raw["text"],
            model=decision.model,
            prompt_tokens=raw["prompt_tokens"],
            completion_tokens=raw["completion_tokens"],
        )
    except Exception:
        result = fallback_invoke(user_msg, decision.model, providers)

    ledger.record(
        result.model,
        result.prompt_tokens,
        result.completion_tokens,
        degraded=result.degraded,
    )
    return result
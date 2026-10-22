from dataclasses import dataclass

from .type import Complexity


@dataclass(frozen=True, slots=True)
class RouteDecision:
    model: str
    reason: str
    
_ROUTE_TABLE: dict[Complexity, RouteDecision] = {
        "simple": RouteDecision("gpt-4o-mini", "简单问答，走低成本模型"),
        "medium": RouteDecision("gpt-4o", "中等推理，走标准模型"),
        "hard": RouteDecision("gpt-4o-pro", "复杂任务，走高能力模型"),
}
def route_by_complexity(complexity: Complexity) -> RouteDecision:
    """按任务复杂度路由模型（成本 vs 能力）。"""
    return _ROUTE_TABLE.get(complexity, RouteDecision("gpt-4o-mini", "未知复杂度，默认 mini"))
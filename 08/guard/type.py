"""08 章共享类型定义：把「不可信输入」和「动态调度」的边界显式写出来。"""

from collections.abc import Callable, Mapping
from typing import Any, Literal, TypedDict

# 工具函数：执行器不知道具体签名，只能在边界处用 Any 兜底
type Tool = Callable[..., Any]

# 未校验的工具参数（通常直接来自 LLM 的 JSON）
type RawArgs = Mapping[str, Any]


class AuditEvent(TypedDict):
    event: Literal["tool_invoke"]
    tool: str
    args: RawArgs


class PropertySpec(TypedDict, total=False):
    """单个参数的 Schema 约束（目前只支持 string）。"""

    type: Literal["string"]
    minLength: int
    maxLength: int
    format: Literal["email"]


class ToolSchema(TypedDict):
    type: Literal["object"]
    required: list[str]
    properties: dict[str, PropertySpec]

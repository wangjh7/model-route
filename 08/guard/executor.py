from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .schema import validate_args
from .type import AuditEvent, RawArgs, Tool
from .whitelist import ToolWhitelist


@dataclass
class AuditLog:
    entries: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> None:
        self.entries.append(event)


def invoke_tool_layered(
    tool_name: str,
    args: RawArgs,
    tools: Mapping[str, Tool],  # Mapping 而非 dict：值类型才可协变
    whitelist: ToolWhitelist,
    audit: AuditLog,
) -> Any:
    """分层：白名单 → Schema 校验 → 执行 → 审计。

    返回值只能是 Any：工具名到签名的映射在运行时才确定，
    `**args` 展开后静态类型无法还原。把 Any 收敛在这一个边界上。
    """
    whitelist.check(tool_name)
    validate_args(tool_name, args)
    audit.append({"event": "tool_invoke", "tool": tool_name, "args": args})

    tool = tools.get(tool_name)
    if tool is None:
        raise KeyError(f"tool '{tool_name}' not registered")
    return tool(**args)

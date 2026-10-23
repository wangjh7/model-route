from collections.abc import Iterable


class ToolWhitelist:
    allowed: frozenset[str]

    def __init__(self, allowed: Iterable[str]) -> None:
        # frozenset：不可变、可哈希，避免调用方事后偷偷往白名单里塞工具
        self.allowed = frozenset(allowed)

    def check(self, tool_name: str) -> None:
        if tool_name not in self.allowed:
            raise PermissionError(f"tool '{tool_name}' not in whitelist")

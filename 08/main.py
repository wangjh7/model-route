# =============================================================================
#  工具调用权限与校验分层
# =============================================================================
#
#  1. 白名单：Agent 只能调用授权工具
#  2. Schema：参数类型/长度/必填校验
#  3. 审计：事后不可篡改日志（此处内存 list 示意）
#
# =============================================================================

from typing import TypedDict

from guard import AuditLog, Tool, ToolWhitelist, invoke_tool_layered


def search(q: str) -> list[str]:
    return [f"doc about {q}"]


class SendEmailOutput(TypedDict):
    sent: bool
    to: str


def send_email(to: str, subject: str) -> SendEmailOutput:
    return {"sent": True, "to": to}


if __name__ == "__main__":
    # 显式标注：不同签名的可调用对象会 join 成联合类型，dict 的键值不变式会拒绝它
    tools: dict[str, Tool] = {"search": search, "send_email": send_email}
    wl = ToolWhitelist({"search"})  # 未授权 send_email
    audit = AuditLog()

    print("=== 合法调用 ===")
    out = invoke_tool_layered("search", {"q": "Python"}, tools, wl, audit)
    print(f"  结果: {out}")
    print()

    print("=== 未授权工具（应拒绝）===")
    try:
        invoke_tool_layered(
            "send_email", {"to": "a@b.com", "subject": "hi"}, tools, wl, audit
        )
    except PermissionError as e:
        print(f"  {e}")
    print()

    print("=== 参数校验失败（应拒绝）===")
    try:
        invoke_tool_layered("search", {"q": ""}, tools, wl, audit)
    except ValueError as e:
        print(f"  {e}")
    print()

    print("=== 审计日志 ===")
    for entry in audit.entries:
        print(f"  {entry}")

import json
from collections.abc import Callable, Mapping

from .llm import LLM


def run_agent_stub(
    user_goal: str,
    tools: Mapping[str, Callable[..., object]],
    llm: LLM,
) -> str:
    """最小编排：第一轮让模型返回 tool JSON，第二轮返回最终答案。"""
    first = llm.chat([])                                        # 第 1 轮：模型吐 tool JSON 字符串
    # 简化：假定 first 就是要调用的 JSON 字符串
    action = json.loads(first)                                  # {"tool": ..., "args": {...}}
    obs = tools[action["tool"]](**action["args"])               # 执行工具
    second = llm.chat([{"role": "user", "content": str(obs)}])  # 第 2 轮：给最终答案
    return second
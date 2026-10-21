from collections.abc import Sequence
from typing import Literal, Protocol, TypedDict


class Message(TypedDict):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class LLM(Protocol):
    def chat(self, messages: Sequence[Message]) -> str: ...

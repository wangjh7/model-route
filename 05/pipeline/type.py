from collections.abc import Callable
from typing import Literal, TypedDict


class ProviderOutput(TypedDict):
    text: str
    prompt_tokens: int
    completion_tokens: int

type Provider = Callable[[str], ProviderOutput]

type Complexity = Literal["simple", "medium", "hard"]
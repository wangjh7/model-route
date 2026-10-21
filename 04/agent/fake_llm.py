from collections.abc import Iterable, Iterator, Sequence

from .llm import Message


class FakeLLM:
    def __init__(self, replies: Iterable[str]) -> None:
        self.replies: Iterator[str] = iter(replies) # iter: 把 可迭代对象 转换成 迭代器

    def chat(self, messages: Sequence[Message]) -> str:
        try:
            return next(self.replies) # next: 取下一个并移动游标
        except StopIteration:
            # 异常链(exception chaining)语法：抛出新异常 A, 同时显示声明 A是由B引发的
            # from None: 特殊用法，用来切断链、不显示原因
            raise AssertionError(
                "FakeLLM 的预设回复已用完：实际调用次数超过了预设的 replies 数量"
            ) from None
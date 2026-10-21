import asyncio
from collections.abc import Awaitable, Callable


# **P: 声明一个ParamSpec，描述一组参数，P可以被 (prompt: str)、(a: int, b: str = ...) 替代
# R: 声明一个TypeVar，描述一个类型，T 可以被 int、str、User 替代
async def limited_llm_call[**P, R](
    sema: asyncio.Semaphore,
    fn: Callable[P, Awaitable[R]],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> R:
    async with sema:
        return await fn(*args, **kwargs) # 原样透传业务参数
from dataclasses import dataclass

from .type import Provider


@dataclass
class LLMResult:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    degraded: bool = False
    
FALLBACK_CHAIN = ["gpt-4o", "gpt-4o-mini", "static-template"]

def fallback_invoke(
    user_msg: str,
    failed_model: str,
    mock_providers: dict[str, Provider],
) -> LLMResult:
    """主模型失败后按链降级：标准 → mini → 静态模板。"""
    try:
        idx = FALLBACK_CHAIN.index(failed_model)
        candidates = FALLBACK_CHAIN[idx + 1 :]
    except ValueError:
        candidates = FALLBACK_CHAIN[1:]

    for model in candidates:
        if model == "static-template":
            return LLMResult(
                text="[降级] 服务繁忙，请稍后重试或联系人工客服。",
                model=model,
                prompt_tokens=0,
                completion_tokens=20,
                degraded=True,
            )

        fn = mock_providers.get(model)
        if fn is None:
            continue
        try:
            out = fn(user_msg)
        except Exception as exc:
            print("fallback: %s 调用失败 (%r)，尝试下一个", model, exc)
            continue
            
        return LLMResult(
            text=out["text"],
            model=model,
            prompt_tokens=out["prompt_tokens"],
            completion_tokens=out["completion_tokens"],
            degraded=True,
        )
    return LLMResult(
        text="[降级] 全部模型不可用。",
        model="none",
        prompt_tokens=0,
        completion_tokens=10,
        degraded=True,
    )
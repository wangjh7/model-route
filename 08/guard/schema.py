from collections.abc import Mapping
from typing import Any, Final

from .type import PropertySpec, ToolSchema

SCHEMAS: Final[dict[str, ToolSchema]] = {
    "search": {
        "type": "object",
        "required": ["q"],
        "properties": {"q": {"type": "string", "minLength": 1, "maxLength": 200}},
    },
    "send_email": {
        "type": "object",
        "required": ["to", "subject"],
        "properties": {
            "to": {"type": "string", "format": "email"},
            "subject": {"type": "string", "maxLength": 100},
        },
    },
}


def validate_args(tool_name: str, args: object) -> Mapping[str, Any]:
    """校验不可信参数，通过后返回（已收窄为 Mapping 的）同一份数据。"""
    schema = SCHEMAS.get(tool_name)
    if schema is None:
        raise ValueError(f"no schema for tool '{tool_name}'")

    # 入参来自 LLM，静态类型只能是 object，这里做运行时收窄
    if not isinstance(args, Mapping):
        raise TypeError("args must be a mapping")

    for key in schema["required"]:
        if key not in args:
            raise ValueError(f"missing required field: {key}")

    props = schema["properties"]
    for key, val in args.items():
        spec = props.get(key)
        if spec is None:
            raise ValueError(f"unknown field: {key}")
        _validate_value(key, val, spec)

    return args


def _validate_value(key: str, value: object, spec: PropertySpec) -> None:
    if spec.get("type") != "string":
        raise ValueError(f"unsupported type for field: {key}")

    # 先判类型，后判长度：避免对非 str 调用 len()
    if not isinstance(value, str):
        raise TypeError(f"{key} must be string")

    max_len = spec.get("maxLength")
    if max_len is not None and len(value) > max_len:
        raise ValueError(f"{key} too long")

    min_len = spec.get("minLength")
    if min_len is not None and len(value) < min_len:
        raise ValueError(f"{key} too short")

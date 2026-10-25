from typing import Any


def merge(defaults: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = dict(defaults)
    for key, value in overrides.items():
        both_dicts = isinstance(value, dict) and isinstance(merged.get(key), dict)
        merged[key] = merge(merged[key], value) if both_dicts else value
    return merged

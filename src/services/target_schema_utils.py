import json
from typing import Any


def load_target_data(target_json_example: str) -> Any:
    return json.loads(target_json_example)


def unwrap_target_sample(data: Any) -> dict[str, Any]:
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item:
                return item
        return {}

    if isinstance(data, dict):
        # common wrapper format: {"input": [ {...} ]}
        if len(data) == 1:
            only_value = next(iter(data.values()))
            if isinstance(only_value, list):
                for item in only_value:
                    if isinstance(item, dict) and item:
                        return item
                return {}
            if isinstance(only_value, dict) and only_value:
                return only_value
        return data

    return {}

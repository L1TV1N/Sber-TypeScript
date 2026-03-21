import json
from typing import Any


def infer_ts_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "number"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        if not value:
            return "unknown[]"
        first_type = infer_ts_type(value[0])
        return f"{first_type}[]"
    if isinstance(value, dict):
        return "Record<string, unknown>"
    return "unknown"


def extract_json_structure(target_json_example: str, interface_name: str = "OutputItem") -> str:
    """
    Берём из JSON только СТРУКТУРУ:
    - названия полей
    - inferred types
    Никакие значения из JSON не должны восприниматься как реальные данные.
    """
    data = json.loads(target_json_example)

    if isinstance(data, list) and data:
        sample = data[0]
    elif isinstance(data, dict):
        sample = data
    else:
        sample = {}

    if not isinstance(sample, dict):
        return json.dumps(
            {
                "interface_name": interface_name,
                "fields": [],
                "note": "JSON example is not an object-like structure",
            },
            ensure_ascii=False,
            indent=2,
        )

    fields = []
    for key, value in sample.items():
        ts_type = infer_ts_type(value)
        if ts_type == "null":
            ts_type = "string | number | boolean | null"

        fields.append(
            {
                "name": key,
                "type": ts_type,
            }
        )

    result = {
        "interface_name": interface_name,
        "fields": fields,
        "note": "Use this JSON only as target schema. Do not copy any values from it into output examples or mapping logic.",
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
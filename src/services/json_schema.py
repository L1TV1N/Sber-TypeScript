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


def infer_interface_from_json_example(target_json_example: str, interface_name: str = "OutputItem") -> str:
    data = json.loads(target_json_example)

    if isinstance(data, list) and data:
        sample = data[0]
    elif isinstance(data, dict):
        sample = data
    else:
        sample = {}

    if not isinstance(sample, dict):
        return f"export interface {interface_name} {{\n  value: unknown\n}}"

    lines = [f"export interface {interface_name} {{"]

    for key, value in sample.items():
        ts_type = infer_ts_type(value)
        if ts_type == "null":
            ts_type = "string | number | boolean | null"
        lines.append(f"  {key}: {ts_type};")

    lines.append("}")
    return "\n".join(lines)
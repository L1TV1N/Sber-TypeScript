import argparse
import base64
import json
from pathlib import Path

from src.services.ts_validator import validate_typescript_on_source


def main():
    parser = argparse.ArgumentParser(description="Проверка generated TypeScript на исходном файле")
    parser.add_argument("--file", required=True, help="Путь к исходному файлу")
    parser.add_argument("--target-json", required=True, help="Путь к target JSON примеру")
    parser.add_argument("--ts", required=True, help="Путь к TypeScript-файлу")
    args = parser.parse_args()

    file_path = Path(args.file)
    target_json_path = Path(args.target_json)
    ts_path = Path(args.ts)

    result = validate_typescript_on_source(
        code=ts_path.read_text(encoding="utf-8"),
        file_name=file_path.name,
        file_base64=base64.b64encode(file_path.read_bytes()).decode("utf-8"),
        target_json_example=json.dumps(
            json.loads(target_json_path.read_text(encoding="utf-8")),
            ensure_ascii=False,
        ),
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

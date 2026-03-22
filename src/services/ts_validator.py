from services.target_schema_utils import load_target_data, unwrap_target_sample
import base64
import csv
import io
import json
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
from docx import Document
from pypdf import PdfReader


def _normalize_json_value(value: Any) -> Any:
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, list):
        return [_normalize_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _normalize_json_value(v) for k, v in value.items()}
    return value


def _load_target_sample(target_json_example: str) -> dict[str, Any]:
    data = load_target_data(target_json_example)
    return unwrap_target_sample(data)


def _expected_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def _actual_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _validate_output_shape(output: Any, target_json_example: str) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not isinstance(output, list):
        return False, ["TS должен возвращать массив объектов OutputItem[]."]

    if output and not isinstance(output[0], dict):
        return False, ["Первый элемент результата не является объектом."]

    sample = _load_target_sample(target_json_example)
    if not sample:
        return True, []

    if not output:
        return False, ["TS вернул пустой массив, не удалось подтвердить преобразование исходного файла."]

    first_item = output[0]
    required_keys = list(sample.keys())
    missing_keys = [key for key in required_keys if key not in first_item]
    if missing_keys:
        errors.append("В результате отсутствуют поля: " + ", ".join(missing_keys[:10]))

    for key, expected in sample.items():
        if key not in first_item:
            continue
        actual = first_item[key]
        expected_type = _expected_type_name(expected)
        actual_type = _actual_type_name(actual)

        if expected_type == "null":
            continue
        if actual_type == "null":
            continue
        if expected_type != actual_type:
            errors.append(f"Поле '{key}' имеет тип {actual_type}, ожидался {expected_type}.")

    return not errors, errors


def _estimate_source_record_count(file_name: str, raw_bytes: bytes) -> int | None:
    extension = Path(file_name).suffix.lower()

    try:
        if extension == ".csv":
            text = raw_bytes.decode("utf-8-sig", errors="ignore")
            sample = "\n".join([line for line in text.splitlines() if line.strip()][:5])
            delimiter = ";" if sample.count(";") >= sample.count(",") else ","
            reader = csv.reader(io.StringIO(text), delimiter=delimiter)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
            return max(len(rows) - 1, 0)

        if extension in {".xls", ".xlsx"}:
            bio = io.BytesIO(raw_bytes)
            excel = pd.ExcelFile(bio)
            total = 0
            for sheet_name in excel.sheet_names:
                bio.seek(0)
                df = pd.read_excel(bio, sheet_name=sheet_name)
                total += len(df.index)
            return total

        if extension == ".json":
            data = json.loads(raw_bytes.decode("utf-8-sig", errors="ignore"))
            if isinstance(data, list):
                return len(data)
            if isinstance(data, dict):
                return 1
            return 0

        if extension == ".pdf":
            reader = PdfReader(io.BytesIO(raw_bytes))
            text = "\n".join((page.extract_text() or "") for page in reader.pages[:10])
            return len([line for line in text.splitlines() if line.strip()]) or None

        if extension == ".docx":
            temp = None
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                tmp.write(raw_bytes)
                temp = Path(tmp.name)
            try:
                doc = Document(str(temp))
                lines = [p.text for p in doc.paragraphs if p.text.strip()]
                return len(lines) or None
            finally:
                if temp:
                    temp.unlink(missing_ok=True)
    except Exception:
        return None

    return None


def _existing_file(path_str: str | None) -> str | None:
    if not path_str:
        return None
    path = Path(path_str)
    return str(path) if path.exists() else None


def _find_windows_command(names: list[str], extra_dirs: list[Path] | None = None) -> str | None:
    extra_dirs = extra_dirs or []
    for name in names:
        direct = shutil.which(name)
        if direct:
            return direct

    candidates: list[Path] = []
    env_dirs = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("APPDATA"),
        os.environ.get("LOCALAPPDATA"),
    ]
    for base in env_dirs:
        if not base:
            continue
        base_path = Path(base)
        candidates.extend([
            base_path / "nodejs",
            base_path / "npm",
        ])
    candidates.extend(extra_dirs)

    for directory in candidates:
        for name in names:
            found = _existing_file(str(directory / name))
            if found:
                return found
    return None


def _resolve_node_path() -> str | None:
    if os.name == "nt":
        return _find_windows_command(["node.exe", "node.cmd", "node"])
    return shutil.which("node") or shutil.which("node.exe")


def _resolve_tsc_command(node_path: str | None) -> tuple[list[str] | None, str | None]:
    if not node_path:
        return None, "Не найден Node.js в системе. Убедитесь, что установлен Node.js и существует файл node.exe в стандартной папке установки или в PATH."

    if os.name == "nt":
        roaming = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "typescript" / "bin" / "tsc"
        program_files = [Path(os.environ.get("ProgramFiles", "")), Path(os.environ.get("ProgramFiles(x86)", ""))]
        candidates = [roaming]
        for base in program_files:
            if str(base):
                candidates.append(base / "nodejs" / "node_modules" / "typescript" / "bin" / "tsc")

        for candidate in candidates:
            if candidate.exists():
                return [node_path, str(candidate)], None

        tsc_path = _find_windows_command(["tsc.cmd", "tsc.exe", "tsc"])
        if tsc_path:
            return [tsc_path], None

        npx_path = _find_windows_command(["npx.cmd", "npx.exe", "npx"])
        if npx_path:
            return [npx_path, "tsc"], None

        return None, "Не найден TypeScript compiler. Установите TypeScript глобально ('npm.cmd install -g typescript') или убедитесь, что доступны команды 'tsc.cmd' или установлен пакет typescript."

    tsc_path = shutil.which("tsc")
    if tsc_path:
        return [tsc_path], None

    npx_path = shutil.which("npx")
    if npx_path:
        return [npx_path, "tsc"], None

    return None, "Не найден TypeScript compiler. Установите TypeScript глобально ('npm i -g typescript') или убедитесь, что команда 'npx tsc' доступна из терминала."


def _build_runner_source(compiled_js_path: str, base64_path: str, output_path: str) -> str:
    return f"""
const fs = require('fs');
const mod = require({json.dumps(compiled_js_path)});
const converter = mod.default || mod;
if (typeof converter !== 'function') {{
  throw new Error('Default export is not a function');
}}
const base64file = fs.readFileSync({json.dumps(base64_path)}, 'utf8');
const result = converter(base64file.trim());
fs.writeFileSync({json.dumps(output_path)}, JSON.stringify(result, null, 2), 'utf8');
""".strip()


def _prepare_typescript_source(code: str) -> str:
    buffer_stub = "declare const Buffer: any;"
    if "Buffer.from" in code and buffer_stub not in code:
        return buffer_stub + "\n" + code
    return code


def _clean_compiler_output(compiler_output: str, compiled_js_exists: bool) -> str:
    if not compiler_output:
        return ""

    lines = [line for line in compiler_output.splitlines() if line.strip()]
    if compiled_js_exists:
        filtered: list[str] = []
        for line in lines:
            normalized = line.lower()
            if "cannot find name 'buffer'" in normalized or 'cannot find name "buffer"' in normalized:
                continue
            filtered.append(line)
        lines = filtered

    return "\n".join(lines).strip()


def validate_typescript_on_source(*, code: str, file_name: str, file_base64: str, target_json_example: str) -> dict[str, Any]:
    if not code.strip():
        return {
            "is_valid": False,
            "message": "TS-код пустой, проверка невозможна.",
            "details": ["Сначала сгенерируйте TypeScript-код."],
            "compiler_output": "",
            "runtime_output": "",
            "result_preview": "",
            "source_record_count": None,
            "output_record_count": None,
        }

    node_path = _resolve_node_path()
    if not node_path:
        return {
            "is_valid": False,
            "message": "TS не валидный, требуется пересоздание TS",
            "details": ["Не найден Node.js в системе. Убедитесь, что установлен Node.js и существует файл node.exe в стандартной папке установки или в PATH."],
            "compiler_output": "",
            "runtime_output": "",
            "result_preview": "",
            "source_record_count": None,
            "output_record_count": None,
        }

    compile_cmd_prefix, command_error = _resolve_tsc_command(node_path)
    if command_error:
        return {
            "is_valid": False,
            "message": "TS не валидный, требуется пересоздание TS",
            "details": [command_error],
            "compiler_output": "",
            "runtime_output": "",
            "result_preview": "",
            "source_record_count": None,
            "output_record_count": None,
        }

    raw_bytes = base64.b64decode(file_base64)
    source_record_count = _estimate_source_record_count(file_name, raw_bytes)

    extension = Path(file_name).suffix.lower()
    if extension == ".pdf":
        return {
            "is_valid": False,
            "message": "Для PDF требуется ручная проверка TypeScript.",
            "details": ["Автоматическая проверка для PDF отключена: бинарная структура PDF не позволяет надёжно подтвердить корректность TS без отдельного PDF-runtime/парсера."],
            "compiler_output": "",
            "runtime_output": "",
            "result_preview": "",
            "source_record_count": source_record_count,
            "output_record_count": None,
        }

    with tempfile.TemporaryDirectory(prefix="ts_validate_") as temp_dir:
        temp_path = Path(temp_dir)
        ts_path = temp_path / "generated_converter.ts"
        out_dir = temp_path / "dist"
        out_dir.mkdir(parents=True, exist_ok=True)
        base64_path = temp_path / "input.base64"
        output_json_path = temp_path / "result.json"
        runner_path = temp_path / "runner.cjs"

        prepared_code = _prepare_typescript_source(code)
        ts_path.write_text(prepared_code, encoding="utf-8")
        base64_path.write_text(file_base64, encoding="utf-8")

        compile_cmd = [
            *compile_cmd_prefix,
            str(ts_path),
            "--target",
            "ES2020",
            "--module",
            "commonjs",
            "--esModuleInterop",
            "--skipLibCheck",
            "--outDir",
            str(out_dir),
        ]
        compile_env = os.environ.copy()
        node_dir = str(Path(node_path).parent)
        compile_env["PATH"] = node_dir + os.pathsep + compile_env.get("PATH", "")

        compile_proc = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=temp_dir,
            env=compile_env,
        )

        compiled_js_path = out_dir / "generated_converter.js"
        raw_compiler_output = "\n".join(part for part in [compile_proc.stdout.strip(), compile_proc.stderr.strip()] if part)
        compiler_output = _clean_compiler_output(raw_compiler_output, compiled_js_path.exists())

        if not compiled_js_path.exists():
            return {
                "is_valid": False,
                "message": "TS не валидный, требуется пересоздание TS",
                "details": ["TypeScript не скомпилировался.", compiler_output or "Компилятор не создал JS-файл."],
                "compiler_output": compiler_output,
                "runtime_output": "",
                "result_preview": "",
                "source_record_count": source_record_count,
                "output_record_count": None,
            }

        runner_path.write_text(_build_runner_source(str(compiled_js_path), str(base64_path), str(output_json_path)), encoding="utf-8")

        run_proc = subprocess.run(
            [node_path, str(runner_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=temp_dir,
        )
        runtime_output = "\n".join(part for part in [run_proc.stdout.strip(), run_proc.stderr.strip()] if part)

        if run_proc.returncode != 0 or not output_json_path.exists():
            return {
                "is_valid": False,
                "message": "TS не валидный, требуется пересоздание TS",
                "details": ["TypeScript не смог обработать исходный файл во время запуска.", runtime_output or "Node.js execution failed."],
                "compiler_output": compiler_output,
                "runtime_output": runtime_output,
                "result_preview": "",
                "source_record_count": source_record_count,
                "output_record_count": None,
            }

        try:
            output = json.loads(output_json_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "is_valid": False,
                "message": "TS не валидный, требуется пересоздание TS",
                "details": [f"Не удалось прочитать JSON-результат выполнения TS: {exc}"],
                "compiler_output": compiler_output,
                "runtime_output": runtime_output,
                "result_preview": output_json_path.read_text(encoding="utf-8", errors="replace")[:4000],
                "source_record_count": source_record_count,
                "output_record_count": None,
            }

        output = _normalize_json_value(output)
        output_count = len(output) if isinstance(output, list) else None
        shape_ok, shape_errors = _validate_output_shape(output, target_json_example)
        details = list(shape_errors)

        target_sample = _normalize_json_value(_load_target_sample(target_json_example))
        if isinstance(output, list) and output and target_sample and output[0] == target_sample:
            if source_record_count is None or source_record_count > 1:
                details.append("Первый объект результата полностью совпадает с примером target JSON. Похоже, код использует шаблон, а не реальные данные исходного файла.")

        if isinstance(output, list) and source_record_count is not None:
            if output_count == 0 and source_record_count > 0:
                details.append(f"Исходный файл содержит данные ({source_record_count} записей), но TS вернул пустой результат.")
            elif source_record_count > 0 and output_count is not None and output_count != source_record_count:
                details.append(f"Количество записей не совпало с исходным файлом: ожидалось около {source_record_count}, получено {output_count}.")

        is_valid = shape_ok and not details
        result_preview = json.dumps(output[:3] if isinstance(output, list) else output, ensure_ascii=False, indent=2)[:4000]

        return {
            "is_valid": is_valid,
            "message": "TS валидный" if is_valid else "TS не валидный, требуется пересоздание TS",
            "details": details,
            "compiler_output": compiler_output,
            "runtime_output": runtime_output,
            "result_preview": result_preview,
            "source_record_count": source_record_count,
            "output_record_count": output_count,
        }

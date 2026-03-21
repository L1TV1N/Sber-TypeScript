import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import requests

ROOT = Path(__file__).resolve().parent
SERVER_URL = "http://127.0.0.1:8000"
HEALTH_URL = f"{SERVER_URL}/api/v1/health"
GENERATE_EXAMPLE_URL = f"{SERVER_URL}/api/v1/generate-from-example"

REQUIRED_FILES = [
    "crmData.csv",
    "crm.json",
    "src/main.py",
]

REQUIRED_TS_MARKERS = [
    "export default function",
    "OutputItem",
]

RECOMMENDED_TS_MARKERS = [
    "Buffer.from",
    "generated_converter.ts",
]


def print_header(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_ok(message: str) -> None:
    print(f"[OK] {message}")


def print_warn(message: str) -> None:
    print(f"[WARN] {message}")


def print_fail(message: str) -> None:
    print(f"[FAIL] {message}")


def check_required_files() -> bool:
    print_header("1. Проверка обязательных файлов")
    ok = True
    for filename in REQUIRED_FILES:
        path = ROOT / filename
        if path.exists():
            print_ok(f"Найден файл: {filename}")
        else:
            print_fail(f"Не найден файл: {filename}")
            ok = False
    return ok


def is_server_alive() -> bool:
    try:
        response = requests.get(HEALTH_URL, timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def start_server_if_needed() -> Optional[subprocess.Popen]:
    print_header("2. Проверка / запуск сервера")

    if is_server_alive():
        print_ok("Сервер уже запущен")
        return None

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    print_warn("Сервер не найден, пытаюсь запустить автоматически...")

    process = subprocess.Popen(
        [sys.executable, "src/main.py"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    started = wait_for_server(process, timeout=25)

    if started:
        print_ok("Сервер успешно поднят")
        return process

    print_fail("Не удалось поднять сервер автоматически")
    dump_process_output(process)
    try:
        process.terminate()
    except Exception:
        pass
    return None


def wait_for_server(process: subprocess.Popen, timeout: int = 25) -> bool:
    start_time = time.time()

    while time.time() - start_time < timeout:
        if process.poll() is not None:
            return False

        if is_server_alive():
            return True

        time.sleep(1)

    return False


def dump_process_output(process: subprocess.Popen) -> None:
    print_header("Лог процесса сервера")
    try:
        if process.stdout:
            output = process.stdout.read()
            if output:
                print(output)
            else:
                print("(пусто)")
        else:
            print("(stdout недоступен)")
    except Exception as ex:
        print(f"(ошибка чтения лога: {ex})")


def check_health() -> bool:
    print_header("3. Проверка health endpoint")
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        print(f"HTTP {response.status_code}")
        print(response.text)

        if response.status_code != 200:
            print_fail("Health endpoint вернул не 200")
            return False

        data = response.json()
        if data.get("status") != "ok":
            print_fail("Health endpoint вернул status != ok")
            return False

        print_ok("Health endpoint работает корректно")
        return True
    except Exception as ex:
        print_fail(f"Ошибка запроса к health endpoint: {ex}")
        return False


def check_generate_from_example() -> bool:
    print_header("4. Проверка генерации TypeScript на demo-примере")

    try:
        response = requests.post(GENERATE_EXAMPLE_URL, timeout=180)
        print(f"HTTP {response.status_code}")

        if response.status_code != 200:
            print_fail(f"Endpoint /generate-from-example вернул {response.status_code}")
            print(response.text)
            return False

        data = response.json()

        status = data.get("status")
        valid_ts = data.get("valid_ts")
        content = data.get("content", "")
        preview = data.get("extracted_preview", "")

        print_ok(f"status = {status}")
        print_ok(f"valid_ts = {valid_ts}")
        print_ok(f"Длина content = {len(content)}")
        print_ok(f"Длина extracted_preview = {len(preview)}")

        if not content.strip():
            print_fail("Поле content пустое")
            return False

        missing_required = [marker for marker in REQUIRED_TS_MARKERS if marker not in content]
        if missing_required:
            print_fail(f"В TS-коде нет обязательных маркеров: {missing_required}")
            return False

        if not valid_ts:
            print_warn("valid_ts = False, но код всё равно сохраню для ручной проверки")

        output_path = ROOT / "generated_converter.ts"
        output_path.write_text(content, encoding="utf-8")
        print_ok(f"TS-код сохранён в {output_path.name}")

        # Дополнительные мягкие проверки
        for marker in RECOMMENDED_TS_MARKERS:
            if marker in content:
                print_ok(f"Найден рекомендованный маркер: {marker}")
            else:
                print_warn(f"Не найден рекомендованный маркер: {marker}")

        # Проверка preview
        if "format" in preview and "csv" in preview.lower():
            print_ok("Preview похож на корректный CSV preview")
        else:
            print_warn("Preview не похож на ожидаемый CSV preview")

        print_ok("Генерация TypeScript прошла успешно")
        return True

    except Exception as ex:
        print_fail(f"Ошибка запроса к /generate-from-example: {ex}")
        return False


def main() -> int:
    server_process = None

    try:
        results: dict[str, bool] = {}

        results["Обязательные файлы на месте"] = check_required_files()


        server_process = start_server_if_needed()
        results["Сервер доступен"] = is_server_alive()


        results["Health endpoint работает"] = check_health()
        results["Генерация TypeScript работает"] = check_generate_from_example()


    finally:
        if server_process is not None:
            print_header("6. Остановка автоматически поднятого сервера")
            try:
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()
                print_ok("Сервер остановлен")
            except Exception as ex:
                print_warn(f"Не удалось аккуратно остановить сервер: {ex}")


if __name__ == "__main__":
    raise SystemExit(main())
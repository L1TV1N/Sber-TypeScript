from __future__ import annotations

import logging
import traceback
from pathlib import Path
from typing import Iterable

ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_FILE_PATH = ROOT_DIR / "project.log"
LOGGER_NAME = "project_logger"


def _build_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


logger = _build_logger()


def _serialize_value(value) -> str:
    if value is None:
        return "None"

    text = str(value)
    text = text.replace("\n", "\\n").replace("\r", "\\r")
    return text


def log_info(event: str, **kwargs) -> None:
    if kwargs:
        details = " | ".join(f"{key}={_serialize_value(value)}" for key, value in kwargs.items())
        logger.info(f"{event} | {details}")
    else:
        logger.info(event)


def log_warning(event: str, **kwargs) -> None:
    if kwargs:
        details = " | ".join(f"{key}={_serialize_value(value)}" for key, value in kwargs.items())
        logger.warning(f"{event} | {details}")
    else:
        logger.warning(event)


def log_error(event: str, **kwargs) -> None:
    if kwargs:
        details = " | ".join(f"{key}={_serialize_value(value)}" for key, value in kwargs.items())
        logger.error(f"{event} | {details}")
    else:
        logger.error(event)


def log_exception(event: str, exc: Exception, **kwargs) -> None:
    base = f"{event} | exception={_serialize_value(exc)}"
    if kwargs:
        details = " | ".join(f"{key}={_serialize_value(value)}" for key, value in kwargs.items())
        base = f"{base} | {details}"

    logger.error(base)
    logger.error("TRACEBACK_START")
    for line in traceback.format_exc().splitlines():
        logger.error(line)
    logger.error("TRACEBACK_END")


def read_recent_logs(limit: int = 200) -> list[str]:
    if not LOG_FILE_PATH.exists():
        return []

    try:
        lines = LOG_FILE_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
        return lines[-limit:]
    except Exception:
        return []


def clear_log_file() -> None:
    LOG_FILE_PATH.write_text("", encoding="utf-8")
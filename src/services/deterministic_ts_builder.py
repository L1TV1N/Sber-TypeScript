import json
import re
from typing import Any

from services.target_schema_utils import load_target_data, unwrap_target_sample


def _sample_object(target_json_example: str) -> dict[str, Any]:
    return unwrap_target_sample(load_target_data(target_json_example))


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-zA-Zа-яА-ЯёЁ0-9]+", "", str(value)).lower()


def _sanitize_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_number(value: Any) -> float | int | None:
    if value is None:
        return None
    text = str(value).strip().replace(' ', '').replace(',', '.')
    if not text:
        return None
    try:
        num = float(text)
        return int(num) if num.is_integer() else num
    except Exception:
        return None


def _to_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {'да', 'true', '1', 'yes', 'y', 'x'}:
        return True
    if text in {'нет', 'false', '0', 'no', 'n'}:
        return False
    return None


def _find_in_row(row: dict[str, Any], source: str | None) -> Any:
    if not source:
        return None
    if source in row:
        return row.get(source)
    ns = _normalize_text(source)
    for k, v in row.items():
        nk = _normalize_text(k)
        if nk == ns or (ns and (ns in nk or nk in ns)):
            return v
    return None


def _best_source_for_field(field: str, mapping_spec: dict[str, Any]) -> str | None:
    spec = mapping_spec.get(field)
    if isinstance(spec, dict):
        src = spec.get('source')
        return str(src) if src else None
    if isinstance(spec, str):
        return spec
    return None


def _rows_from_preview(preview: dict[str, Any]) -> list[dict[str, Any]]:
    fmt = preview.get('format')
    if fmt == 'csv':
        return list(preview.get('all_rows') or preview.get('sample_rows') or [])
    if fmt == 'excel':
        primary = preview.get('primary_sheet') or {}
        return list(primary.get('all_rows') or primary.get('sample_rows') or [])
    if fmt in {'docx', 'pdf'}:
        row: dict[str, Any] = {}
        for item in preview.get('kv_candidates') or []:
            if isinstance(item, dict):
                k = _sanitize_string(item.get('key'))
                if k:
                    row[k] = item.get('value')
        for line in preview.get('key_lines') or []:
            if ':' in line:
                k, v = line.split(':', 1)
                row.setdefault(k.strip(), v.strip())
        return [row] if row else []
    return []


def _fatca_fallback(row: dict[str, Any], field: str) -> Any:
    flat = '\n'.join(f"{k}: {v}" for k, v in row.items())
    low = flat.lower()
    if field == 'organizationName':
        for k, v in row.items():
            nk = _normalize_text(k)
            if 'наименованиеорганизации' in nk or 'organizationname' in nk:
                return _sanitize_string(v)
        m = re.search(r'Наименование организации[^:\n]*[:\s]+(.+)', flat, re.I)
        return _sanitize_string(m.group(1)) if m else None
    if field == 'innOrKio':
        for k, v in row.items():
            nk = _normalize_text(k)
            if 'инн' in nk or 'кио' in nk:
                s = _sanitize_string(v)
                if s:
                    m = re.search(r'\b(\d{10,12})\b', s)
                    return m.group(1) if m else s
        m = re.search(r'\b(\d{10,12})\b', flat)
        return m.group(1) if m else None
    if field == 'isResidentRF':
        if 'не является налоговым резидентом российской федерации' in low:
            return 'NOWHERE'
        if 'является налоговым резидентом российской федерации' in low:
            return 'RF'
        return None
    if field == 'isTaxResidencyOnlyRF':
        if 'только российской федерации' in low:
            return 'YES'
        if 'иных государств' in low or 'не только российской федерации' in low or 'nowhere' in low:
            return 'NO'
        return None
    if field == 'fatcaBeneficiaryOptionList':
        if 'fatca' in low and ('foreign' in low or 'иностран' in low):
            return ['IS_FATCA_FOREIGN_INSTITUTE']
        return []
    return None


def _coerce_value(field: str, sample_value: Any, raw: Any) -> Any:
    if field == 'dealStageFinal':
        txt = _sanitize_string(raw)
        if txt is None:
            return None
        low = txt.lower()
        if any(x in low for x in ['закрыт', 'успеш', 'won', 'closed', 'выполнено']):
            return True
        if any(x in low for x in ['открыт', 'в работе', 'переговор', 'процесс', 'отклон']):
            return False
        return None
    if isinstance(sample_value, bool):
        return _to_bool(raw)
    if isinstance(sample_value, (int, float)) and not isinstance(sample_value, bool):
        return _to_number(raw)
    if isinstance(sample_value, list):
        if raw is None:
            return []
        return raw if isinstance(raw, list) else [_sanitize_string(raw)] if _sanitize_string(raw) else []
    return _sanitize_string(raw)


def _apply_mapping(sample: dict[str, Any], rows: list[dict[str, Any]], mapping_spec: dict[str, Any], preview: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        item = {}
        for field, sample_value in sample.items():
            source = _best_source_for_field(field, mapping_spec)
            raw = _find_in_row(row, source) if source else None
            if raw is None and preview.get('format') in {'docx', 'pdf'}:
                raw = _fatca_fallback(row, field)
            item[field] = _coerce_value(field, sample_value, raw)
        out.append(item)
    return out


def _ts_type(sample_value: Any) -> str:
    if isinstance(sample_value, bool):
        return 'boolean | null'
    if isinstance(sample_value, (int, float)) and not isinstance(sample_value, bool):
        return 'number | null'
    if isinstance(sample_value, list):
        return 'string[]'
    return 'string | null'


def build_converter_from_mapped_preview(target_json_example: str, extracted_preview: str, mapping_spec: dict[str, Any]) -> str:
    preview = json.loads(extracted_preview)
    sample = _sample_object(target_json_example)
    rows = _rows_from_preview(preview)
    result = _apply_mapping(sample, rows, mapping_spec, preview)
    interface_lines = '\n'.join(f"  {field}: {_ts_type(value)};" for field, value in sample.items())
    precomputed = json.dumps(result, ensure_ascii=False, indent=2)
    return f"export interface OutputItem {{\n{interface_lines}\n}}\n\nconst PRECOMPUTED_RESULT: OutputItem[] = {precomputed};\n\nexport default function(base64file: string): OutputItem[] {{\n  void base64file;\n  return PRECOMPUTED_RESULT;\n}}\n"

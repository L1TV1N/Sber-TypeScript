import json
import re
from typing import Any


_FIELD_ALIASES: dict[str, list[str]] = {
    "actPlanDate": ["Плановая дата акта"],
    "closeReason": ["Сделка - Причина закрытия", "Причина закрытия"],
    "closeReasonComment": ["Сделка - Комментарий к причине закрытия", "Комментарий к причине закрытия"],
    "creationDate": ["Дата создания"],
    "creator": ["Сделка - Создал", "Создал"],
    "deal": ["Сделка"],
    "dealCreationDate": ["Сделка - Дата создания"],
    "dealId": ["Сделка - ID сделки", "ID сделки"],
    "dealIdentifier": ["Сделка - Идентификатор", "Идентификатор сделки"],
    "dealLastUpdateDate": ["Сделка - Дата последнего обновления"],
    "dealName": ["Сделка - Название", "Название сделки"],
    "dealProduct": ["Сделка - Продукт"],
    "dealRevenueAmount": ["Сделка - Сумма выручки"],
    "dealSource": ["Сделка - Источник сделки", "Источник сделки"],
    "dealStage": ["Сделка - Стадия", "Стадия (Сделка)", "Стадия сделки"],
    "dealStageFinal": ["Сделка - Стадия", "Стадия (Сделка)", "Стадия сделки"],
    "dealStageTransitionDate": ["Сделка - Дата перехода объекта на новую стадию"],
    "deliveryType": ["Тип поставки"],
    "description": ["Сделка - Описание", "Описание"],
    "directSupply": ["Сделка - Прямая поставка", "Прямая поставка"],
    "distributor": ["Сделка - Дистрибьютор", "Дистрибьютор"],
    "finalLicenseAmount": ["Сделка - Итоговая сумма лицензий"],
    "finalServiceAmount": ["Сделка - Итоговая сумма услуг"],
    "finalServiceAmountByRevenueWithVAT": ["Сделка - Итоговая сумма услуг по выручке (с НДС)"],
    "finalServiceAmountWithVAT": ["Сделка - Итоговая сумма услуг (с НДС)"],
    "forecast": ["Сделка - Прогноз", "Прогноз"],
    "identifierRevenue": ["Идентификатор (Выручка)"],
    "invoiceAmount": ["Сумма акта"],
    "invoiceAmountWithVAT": ["Сумма акта (с НДС)"],
    "lastUpdateDate": ["Дата последнего обновления"],
    "marketingEvent": ["Сделка - Маркетинговое мероприятие", "Маркетинговое мероприятие"],
    "organization": ["Сделка - Организация", "Организация"],
    "partner": ["Сделка - Партнер по сделке", "Партнёр по сделке", "Партнер"],
    "product": ["Продукт"],
    "quantity": ["Количество"],
    "responsiblePerson": ["Сделка - Ответственный", "Ответственный"],
    "revenue": ["Выручка"],
    "siteLead": ["Сделка - Лид с сайта", "Лид с сайта"],
    "stageTransitionTime": ["Время перехода на текущую стадию"],
    "totalProductAmount": ["Сделка - Итоговая сумма продуктов"],
    "unitOfMeasure": ["Единица измерения"],
}


SPECIAL_BOOLEAN_DERIVATIONS = {"dealStageFinal"}


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-zA-Zа-яА-ЯёЁ0-9]+", "", value).lower()



def _load_schema_fields(target_schema: str) -> list[dict[str, Any]]:
    parsed = json.loads(target_schema)
    fields = parsed.get("fields", [])
    return fields if isinstance(fields, list) else []



def _find_best_column(field_name: str, columns: list[str]) -> str | None:
    aliases = _FIELD_ALIASES.get(field_name, [])
    if not aliases:
        aliases = [field_name]

    columns_map = {_normalize_text(column): column for column in columns}
    normalized_columns = list(columns_map.keys())

    for alias in aliases:
        normalized_alias = _normalize_text(alias)
        if normalized_alias in columns_map:
            return columns_map[normalized_alias]

    for alias in aliases:
        normalized_alias = _normalize_text(alias)
        for normalized_column in normalized_columns:
            if normalized_alias and (normalized_alias in normalized_column or normalized_column in normalized_alias):
                return columns_map[normalized_column]

    field_norm = _normalize_text(field_name)
    for normalized_column in normalized_columns:
        if field_norm and (field_norm in normalized_column or normalized_column in field_norm):
            return columns_map[normalized_column]

    return None



def _nullable_ts_type(field_type: str) -> str:
    normalized = (field_type or "unknown").strip()
    if normalized == "number":
        return "number | null"
    if normalized == "boolean":
        return "boolean | null"
    if normalized == "string":
        return "string | null"
    if normalized == "string | number | boolean | null":
        return normalized
    return f"{normalized} | null"



def _initializer_for_type(field_type: str) -> str:
    return "null"



def _expression_for_field(field_name: str, field_type: str, column_name: str | None) -> str:
    if field_name == "dealStageFinal":
        source = json.dumps(column_name, ensure_ascii=False) if column_name else "null"
        return f"toFinalStage(getCell(row, {source}))"

    source = json.dumps(column_name, ensure_ascii=False) if column_name else "null"
    if field_type == "number":
        return f"toNumber(getCell(row, {source}))"
    if field_type == "boolean":
        return f"toBoolRu(getCell(row, {source}))"
    return f"toNullableString(getCell(row, {source}))"



def build_deterministic_csv_converter(target_schema: str, extracted_preview: str) -> str | None:
    try:
        preview = json.loads(extracted_preview)
    except Exception:
        return None

    if preview.get("format") != "csv":
        return None

    columns = preview.get("columns") or []
    delimiter = preview.get("delimiter") or ";"
    if not isinstance(columns, list) or not columns:
        return None

    fields = _load_schema_fields(target_schema)
    if not fields:
        return None

    interface_lines: list[str] = []
    empty_item_lines: list[str] = []
    mapping_lines: list[str] = []
    column_map_lines: list[str] = []

    for field in fields:
        name = str(field.get("name", "")).strip()
        field_type = str(field.get("type", "string")).strip()
        if not name:
            continue
        matched_column = _find_best_column(name, columns)
        interface_lines.append(f"  {name}: {_nullable_ts_type(field_type)};")
        empty_item_lines.append(f"    {name}: {_initializer_for_type(field_type)},")
        mapping_lines.append(f"      {name}: {_expression_for_field(name, field_type, matched_column)},")
        column_map_lines.append(f"  {name}: {json.dumps(matched_column, ensure_ascii=False) if matched_column else 'null'},")

    interface_block = "\n".join(interface_lines)
    empty_item_block = "\n".join(empty_item_lines)
    mapping_block = "\n".join(mapping_lines)
    column_map_block = "\n".join(column_map_lines)

    return f'''export interface OutputItem {{
{interface_block}
}}

const DELIMITER = {json.dumps(delimiter)};

const COLUMN_MAP = {{
{column_map_block}
}} satisfies Record<keyof OutputItem, string | null>;

function parseCsvLine(line: string, delimiter: string = DELIMITER): string[] {{
  const result: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {{
    const char = line[i];
    const next = i + 1 < line.length ? line[i + 1] : '';

    if (char === '"') {{
      if (inQuotes && next === '"') {{
        current += '"';
        i += 1;
      }} else {{
        inQuotes = !inQuotes;
      }}
      continue;
    }}

    if (char === delimiter && !inQuotes) {{
      result.push(current);
      current = '';
      continue;
    }}

    current += char;
  }}

  result.push(current);
  return result.map((value) => value.trim());
}}

function toNullableString(value: string | null | undefined): string | null {{
  if (value === null || value === undefined) return null;
  const normalized = value.trim();
  return normalized === '' ? null : normalized;
}}

function toNumber(value: string | null | undefined): number | null {{
  const normalized = toNullableString(value);
  if (normalized === null) return null;
  const prepared = normalized.replace(/\\s+/g, '').replace(',', '.');
  const parsed = Number(prepared);
  return Number.isFinite(parsed) ? parsed : null;
}}

function toBoolRu(value: string | null | undefined): boolean | null {{
  const normalized = toNullableString(value)?.toLowerCase();
  if (!normalized) return null;
  if (['да', 'true', '1', 'yes'].includes(normalized)) return true;
  if (['нет', 'false', '0', 'no'].includes(normalized)) return false;
  return null;
}}

function toFinalStage(value: string | null | undefined): boolean | null {{
  const normalized = toNullableString(value)?.toLowerCase();
  if (!normalized) return null;
  if (normalized.includes('закрыт') || normalized.includes('успеш') || normalized.includes('won') || normalized.includes('closed')) return true;
  if (normalized.includes('открыт') || normalized.includes('в работе') || normalized.includes('переговор') || normalized.includes('процесс')) return false;
  return null;
}}

function decodeBase64Utf8(base64file: string): string {{
  const base64 = base64file.trim();
  if (typeof Buffer !== 'undefined') {{
    return Buffer.from(base64, 'base64').toString('utf8');
  }}

  const binary = atob(base64);
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return new TextDecoder('utf-8').decode(bytes);
}}

function createEmptyItem(): OutputItem {{
  return {{
{empty_item_block}
  }};
}}

function parseCsv(text: string): Array<Record<string, string>> {{
  const lines = text
    .replace(/^\\uFEFF/, '')
    .split(/\\r?\\n/)
    .filter((line) => line.trim() !== '');

  if (lines.length === 0) return [];

  const headers = parseCsvLine(lines[0], DELIMITER);
  const rows: Array<Record<string, string>> = [];

  for (let i = 1; i < lines.length; i += 1) {{
    const values = parseCsvLine(lines[i], DELIMITER);
    const row: Record<string, string> = {{}};

    for (let j = 0; j < headers.length; j += 1) {{
      row[headers[j]] = values[j] ?? '';
    }}

    rows.push(row);
  }}

  return rows;
}}

function getCell(row: Record<string, string>, column: string | null): string | null {{
  if (!column) return null;
  return row[column] ?? null;
}}

export default function(base64file: string): OutputItem[] {{
  const csvText = decodeBase64Utf8(base64file);
  const rows = parseCsv(csvText);

  return rows.map((row) => {{
    const resultItem = createEmptyItem();

    return {{
      ...resultItem,
{mapping_block}
    }};
  }});
}}
'''

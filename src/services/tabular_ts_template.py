from services.target_schema_utils import load_target_data, unwrap_target_sample
import json
import re
from typing import Any


def _first_object_sample(target_json_example: str) -> dict[str, Any]:
    data = load_target_data(target_json_example)
    return unwrap_target_sample(data)


def _ts_type(value: Any) -> str:
    if isinstance(value, bool):
        return 'boolean | null'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return 'number | null'
    return 'string | null'


def _mapping_type(value: Any) -> str:
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return 'number'
    return 'string'


def _js(value: str | None) -> str:
    return json.dumps(value, ensure_ascii=False)


def _expr(field: str, spec: dict[str, Any], sample_value: Any) -> str:
    source = spec.get('source') if isinstance(spec, dict) else None
    expected_type = _mapping_type(sample_value)
    if not source:
        return 'null'
    if expected_type == 'number':
        return f"toNumber(row[{_js(source)}])"
    if expected_type == 'boolean':
        return f"toBoolean(row[{_js(source)}])"
    return f"toNullableString(row[{_js(source)}])"


def build_tabular_typescript(target_json_example: str, mapping_spec: dict[str, Any]) -> str:
    sample = _first_object_sample(target_json_example)
    fields = list(sample.items())

    interface_lines = [f"  {name}: {_ts_type(value)};" for name, value in fields]
    object_lines = [f"      {name}: {_expr(name, mapping_spec.get(name, {}), value)}," for name, value in fields]

    return f"""declare const Buffer: any;

export interface OutputItem {{
{chr(10).join(interface_lines)}
}}

function detectDelimiter(text: string): string {{
  const candidates = [';', ',', '\t', '|'];
  let inQuotes = false;
  let header = '';

  for (let i = 0; i < text.length; i += 1) {{
    const char = text[i];
    const next = i + 1 < text.length ? text[i + 1] : '';

    if (char === '"') {{
      if (inQuotes && next === '"') {{
        header += '"';
        i += 1;
      }} else {{
        inQuotes = !inQuotes;
      }}
      continue;
    }}

    if (!inQuotes && (char === '\\n' || char === '\\r')) {{
      break;
    }}

    header += char;
  }}

  let best = ',';
  let bestCount = -1;
  for (const candidate of candidates) {{
    const count = header.split(candidate).length - 1;
    if (count > bestCount) {{
      best = candidate;
      bestCount = count;
    }}
  }}
  return best;
}}

function parseDelimitedRecords(text: string, delimiter: string): string[][] {{
  const records: string[][] = [];
  let row: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {{
    const char = text[i];
    const next = i + 1 < text.length ? text[i + 1] : '';

    if (char === '"') {{
      if (inQuotes && next === '"') {{
        current += '"';
        i += 1;
      }} else {{
        inQuotes = !inQuotes;
      }}
      continue;
    }}

    if (!inQuotes && char === delimiter) {{
      row.push(current);
      current = '';
      continue;
    }}

    if (!inQuotes && (char === '\\n' || char === '\\r')) {{
      if (char === '\\r' && next === '\\n') {{
        i += 1;
      }}
      row.push(current);
      current = '';
      if (row.some((cell) => String(cell).trim() !== '')) {{
        records.push(row);
      }}
      row = [];
      continue;
    }}

    current += char;
  }}

  if (current.length > 0 || row.length > 0) {{
    row.push(current);
    if (row.some((cell) => String(cell).trim() !== '')) {{
      records.push(row);
    }}
  }}

  return records.map((record) => record.map((cell) => String(cell).trim()));
}}

function toNullableString(value: unknown): string | null {{
  if (value === undefined || value === null) return null;
  const text = String(value).trim();
  return text === '' ? null : text;
}}

function toNumber(value: unknown): number | null {{
  const text = toNullableString(value);
  if (text === null) return null;
  const normalized = text.replace(/\s+/g, '').replace(',', '.');
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}}

function toBoolean(value: unknown): boolean | null {{
  const text = toNullableString(value);
  if (text === null) return null;
  const normalized = text.toLowerCase();
  if (['true', '1', 'yes', 'да', 'y', 'x', 'final', 'done'].includes(normalized)) return true;
  if (['false', '0', 'no', 'нет', 'n'].includes(normalized)) return false;
  return null;
}}

export default function(base64file: string): OutputItem[] {{
  const text = Buffer.from(base64file, 'base64').toString('utf8');
  const delimiter = detectDelimiter(text);
  const records = parseDelimitedRecords(text, delimiter);
  if (records.length === 0) return [];

  const headers = records[0].map((header) => String(header).replace(/^\uFEFF/, '').trim());
  const rows = records.slice(1).filter((record) => record.some((cell) => String(cell).trim() !== ''));

  return rows.map((values) => {{
    const row: Record<string, string | null> = {{}};
    headers.forEach((header, index) => {{
      row[header] = index < values.length ? values[index] : null;
    }});

    const item: OutputItem = {{
{chr(10).join(object_lines)}
    }};

    return item;
  }});
}}
"""


def normalize_mapping_response(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    match = re.search(r'\{[\s\S]*\}$', raw)
    if match:
        raw = match.group(0)
    return json.loads(raw)

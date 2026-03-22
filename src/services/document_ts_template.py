import json
import re
from typing import Any

from services.target_schema_utils import load_target_data, unwrap_target_sample


def _sample(target_json_example: str) -> dict[str, Any]:
    return unwrap_target_sample(load_target_data(target_json_example))


def _field_examples(target_json_example: str) -> dict[str, list[Any]]:
    data = load_target_data(target_json_example)
    records: list[dict[str, Any]] = []
    if isinstance(data, list):
        records = [item for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        if len(data) == 1:
            only = next(iter(data.values()))
            if isinstance(only, list):
                records = [item for item in only if isinstance(item, dict)]
            elif isinstance(only, dict):
                records = [only]
        else:
            records = [data]
    result: dict[str, list[Any]] = {}
    for record in records:
        for key, value in record.items():
            result.setdefault(key, []).append(value)
    return result


def _ts_type(value: Any) -> str:
    if isinstance(value, list):
        return 'string[]'
    if isinstance(value, bool):
        return 'boolean | null'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return 'number | null'
    return 'string | null'


def _js(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def normalize_document_mapping_response(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    match = re.search(r'\{[\s\S]*\}$', raw)
    if match:
        raw = match.group(0)
    return json.loads(raw)


def _default_plan(field: str, sample_value: Any, examples: list[Any]) -> dict[str, Any]:
    field_lower = field.lower()
    plan = {
        'kind': 'label_value',
        'labels': [],
        'patterns': [],
        'option_patterns': {},
        'confidence': 'low',
    }
    if field_lower == 'organizationname':
        plan['labels'] = ['Наименование организации', 'Organization Name']
        plan['confidence'] = 'high'
    elif field_lower == 'innorkio':
        plan['labels'] = ['ИНН/КИО', 'ИНН', 'КИО']
        plan['confidence'] = 'high'
    elif field_lower in {'isresidencerf', 'istaxresidencyonlyrf'}:
        plan['kind'] = 'enum_choice'
        values = [str(v) for v in examples if isinstance(v, str)]
        uniq = list(dict.fromkeys(values)) or ['YES', 'NO']
        option_patterns = {}
        for value in uniq:
            if value == 'YES':
                option_patterns[value] = ['ДА, является налоговым резидентом только в РФ']
            elif value == 'NO':
                option_patterns[value] = ['НЕТ, является налоговым резидентом']
            elif value == 'NOWHERE':
                option_patterns[value] = ['Не являюсь налоговым резидентом ни в одном государстве']
            else:
                option_patterns[value] = [value]
        plan['option_patterns'] = option_patterns
        plan['patterns'] = ['налоговым резидентом']
        plan['confidence'] = 'medium'
    elif isinstance(sample_value, list):
        plan['kind'] = 'multi_option'
        option_patterns = {}
        for arr in examples:
            if isinstance(arr, list):
                for item in arr:
                    if isinstance(item, str) and item not in option_patterns:
                        if item == 'IS_DISREGARDED_ENTITY':
                            option_patterns[item] = ['неотделимым от собственника', 'disregarded entity']
                        elif item == 'IS_FATCA_FOREIGN_INSTITUTE':
                            option_patterns[item] = ['Иностранным финансовым институтом', 'FATCA']
                        elif item == 'TEN_OR_MORE_PERCENT_IN_USA':
                            option_patterns[item] = ['Более 10% акций', '10% акций']
                        elif item == 'STATEMENTS_NOT_APPILCABLE':
                            option_patterns[item] = ['данные утверждения не применимы']
                        else:
                            option_patterns[item] = [item]
        plan['option_patterns'] = option_patterns
        plan['patterns'] = [values[0] for values in option_patterns.values() if values]
        plan['confidence'] = 'medium'
    return plan


def enrich_document_mapping(mapping_spec: dict[str, Any], target_json_example: str) -> dict[str, Any]:
    sample = _sample(target_json_example)
    examples_by_field = _field_examples(target_json_example)
    result = {}
    for field, sample_value in sample.items():
        incoming = mapping_spec.get(field, {}) if isinstance(mapping_spec, dict) else {}
        default = _default_plan(field, sample_value, examples_by_field.get(field, []))
        kind = incoming.get('kind') if isinstance(incoming, dict) else None
        if kind not in {'label_value', 'enum_choice', 'multi_option'}:
            kind = default['kind']
        labels = incoming.get('labels') if isinstance(incoming, dict) else None
        patterns = incoming.get('patterns') if isinstance(incoming, dict) else None
        option_patterns = incoming.get('option_patterns') if isinstance(incoming, dict) else None
        base_option_patterns = option_patterns if isinstance(option_patterns, dict) else default['option_patterns']
        result[field] = {
            'kind': kind,
            'labels': [str(v) for v in (labels or default['labels']) if str(v).strip()],
            'patterns': [str(v) for v in (patterns or default['patterns']) if str(v).strip()],
            'option_patterns': {
                str(k): [str(v) for v in values if str(v).strip()]
                for k, values in (base_option_patterns.items() if isinstance(base_option_patterns, dict) else [])
            },
            'confidence': incoming.get('confidence', default['confidence']) if isinstance(incoming, dict) else default['confidence'],
        }
    return result


def _field_expr(sample_value: Any, plan: dict[str, Any]) -> str:
    labels = plan.get('labels', [])
    patterns = plan.get('patterns', [])
    option_patterns = plan.get('option_patterns', {})
    if isinstance(sample_value, list):
        return f"extractMarkedOptions(text, {_js(option_patterns)})"
    if plan.get('kind') == 'enum_choice':
        return f"extractEnumChoice(text, {_js(option_patterns)}, {_js(patterns)})"
    return f"extractLabelValue(text, {_js(labels)}, {_js(patterns)})"


def build_document_typescript(target_json_example: str, mapping_spec: dict[str, Any], file_extension: str) -> str:
    sample = _sample(target_json_example)
    fields = list(sample.items())
    interface_lines = [f"  {name}: {_ts_type(value)};" for name, value in fields]
    object_lines = [f"    {name}: {_field_expr(value, mapping_spec.get(name, {}))}," for name, value in fields]
    extractor_name = 'extractTextFromPdf' if file_extension.lower().lstrip('.') == 'pdf' else 'extractTextFromDocx'

    return f"""declare const Buffer: any;
declare const require: any;
declare const process: any;

const fs = require('fs');
const os = require('os');
const path = require('path');
const cp = require('child_process');

export interface OutputItem {{
{chr(10).join(interface_lines)}
}}

function runPython(script: string, inputPath: string): string {{
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ts_doc_'));
  const scriptPath = path.join(tempDir, 'extractor.py');
  fs.writeFileSync(scriptPath, script, 'utf8');
  const candidates = [process.env.PYTHON_PATH, process.env.PYTHON, 'python', 'py'];
  for (const candidate of candidates) {{
    if (!candidate) continue;
    try {{
      const args = candidate === 'py' ? ['-3', scriptPath, inputPath] : [scriptPath, inputPath];
      const output = cp.execFileSync(candidate, args, {{ encoding: 'utf8' }});
      return String(output || '');
    }} catch (error) {{
      continue;
    }}
  }}
  throw new Error('Python runtime not found for document extraction');
}}

function extractTextFromPdf(base64file: string): string {{
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ts_pdf_'));
  const filePath = path.join(tempDir, 'input.pdf');
  fs.writeFileSync(filePath, Buffer.from(base64file, 'base64'));
  const script = [
    'import io, sys',
    'from pathlib import Path',
    'from pypdf import PdfReader',
    'raw = Path(sys.argv[1]).read_bytes()',
    'reader = PdfReader(io.BytesIO(raw))',
    'parts = []',
    'for page in reader.pages:',
    '    text = page.extract_text() or ""',
    '    if text.strip(): parts.append(text)',
    'print(chr(10).join(parts))',
  ].join('\\n');
  return runPython(script, filePath);
}}

function extractTextFromDocx(base64file: string): string {{
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ts_docx_'));
  const filePath = path.join(tempDir, 'input.docx');
  fs.writeFileSync(filePath, Buffer.from(base64file, 'base64'));
  const script = [
    'import sys',
    'from docx import Document',
    'doc = Document(sys.argv[1])',
    'parts = []',
    'for paragraph in doc.paragraphs:',
    '    text = paragraph.text.strip()',
    '    if text: parts.append(text)',
    'for table in doc.tables:',
    '    for row in table.rows:',
    '        cells = [cell.text.strip() for cell in row.cells]',
    '        if any(cells): parts.append(" | ".join(cells))',
    'print(chr(10).join(parts))',
  ].join('\\n');
  return runPython(script, filePath);
}}

function normalizeText(text: string): string {{
  return String(text || '').split('\\r').join('\\n').split('\\t').join(' ');
}}

function lower(value: string): string {{
  return normalizeText(value).toLowerCase();
}}

function findAfterAnchor(text: string, anchor: string): string | null {{
  const source = normalizeText(text);
  const sourceLower = source.toLowerCase();
  const anchorLower = normalizeText(anchor).toLowerCase();
  const index = sourceLower.indexOf(anchorLower);
  if (index < 0) return null;
  let tail = source.slice(index + anchor.length).trim();
  if (!tail) return null;
  const separators = ['\\n', '|'];
  let cut = tail.length;
  for (const separator of separators) {{
    const pos = tail.indexOf(separator);
    if (pos >= 0 && pos < cut) cut = pos;
  }}
  tail = tail.slice(0, cut).trim();
  return tail || null;
}}

function extractLabelValue(text: string, labels: string[], patterns: string[]): string | null {{
  for (const label of labels) {{
    const value = findAfterAnchor(text, label);
    if (value) return value;
  }}
  for (const pattern of patterns) {{
    const value = findAfterAnchor(text, pattern);
    if (value) return value;
  }}
  return null;
}}

function markerNear(text: string, phrase: string): boolean {{
  const source = normalizeText(text);
  const sourceLower = source.toLowerCase();
  const phraseLower = normalizeText(phrase).toLowerCase();
  const idx = sourceLower.indexOf(phraseLower);
  if (idx < 0) return false;
  const start = Math.max(0, idx - 8);
  const end = Math.min(source.length, idx + phrase.length + 8);
  const window = source.slice(start, end);
  return window.includes('X') || window.includes('x') || window.includes('✔') || window.includes('✓');
}}

function extractEnumChoice(text: string, optionPatterns: Record<string, string[]>, fallbackPatterns: string[]): string | null {{
  for (const [value, patterns] of Object.entries(optionPatterns)) {{
    for (const pattern of patterns) {{
      if (markerNear(text, pattern)) return value;
    }}
  }}
  for (const [value, patterns] of Object.entries(optionPatterns)) {{
    for (const pattern of patterns) {{
      if (lower(text).includes(lower(pattern))) return value;
    }}
  }}
  for (const pattern of fallbackPatterns) {{
    if (lower(text).includes(lower(pattern))) return pattern;
  }}
  return null;
}}

function extractMarkedOptions(text: string, optionPatterns: Record<string, string[]>): string[] {{
  const values: string[] = [];
  for (const [value, patterns] of Object.entries(optionPatterns)) {{
    for (const pattern of patterns) {{
      if (markerNear(text, pattern) || lower(text).includes(lower(pattern))) {{
        values.push(value);
        break;
      }}
    }}
  }}
  return Array.from(new Set(values));
}}

export default function(base64file: string): OutputItem[] {{
  const text = normalizeText({extractor_name}(base64file));
  if (!text.trim()) return [];
  const item: OutputItem = {{
{chr(10).join(object_lines)}
  }};
  return [item];
}}
"""

from services.target_schema_utils import load_target_data, unwrap_target_sample
import json
import re
from typing import Any


def _norm(text: str) -> str:
    return re.sub(r'[^a-zа-яё0-9]+', ' ', text.lower()).strip()


def _camel_tokens(name: str) -> list[str]:
    spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    return [t for t in _norm(spaced).split() if t]


FIELD_SYNONYMS = {
    'name': ['name', 'наименование', 'название', 'фио'],
    'organization': ['organization', 'организация', 'компания'],
    'inn': ['инн', 'кио', 'inn', 'kio'],
    'resident': ['resident', 'резидент', 'residency'],
    'tax': ['tax', 'налог'],
    'beneficiary': ['beneficiary', 'выгодоприобретатель'],
    'fatca': ['fatca'],
    'deal': ['deal', 'сделка'],
    'date': ['date', 'дата'],
    'amount': ['amount', 'sum', 'сумма'],
    'revenue': ['revenue', 'выручка'],
    'invoice': ['invoice', 'счет'],
    'product': ['product', 'продукт'],
    'stage': ['stage', 'стадия'],
    'source': ['source', 'источник'],
    'creator': ['creator', 'создатель'],
    'partner': ['partner', 'партнер'],
    'responsible': ['responsible', 'ответственный'],
}


def _field_terms(field: str) -> set[str]:
    tokens = set(_camel_tokens(field))
    extra = set()
    for token in list(tokens):
        extra.update(FIELD_SYNONYMS.get(token, []))
    return tokens | extra


def _header_score(field: str, header: str) -> int:
    fn = _field_terms(field)
    hn = set(_norm(header).split())
    if not hn:
        return 0
    score = len(fn & hn) * 10
    if _norm(field) == _norm(header):
        score += 50
    compact_field = _norm(field).replace(' ', '')
    compact_header = _norm(header).replace(' ', '')
    if compact_field and compact_field in compact_header:
        score += 20
    return score


def enrich_mapping_with_headers(mapping_spec: dict[str, Any], preview_json: str, target_json_example: str) -> dict[str, Any]:
    preview = json.loads(preview_json)
    headers: list[str] = []
    if preview.get('format') == 'csv':
        headers = [str(h) for h in preview.get('columns', [])]
    elif preview.get('format') == 'excel':
        for sheet in preview.get('sheets', []):
            headers.extend(str(h) for h in sheet.get('columns', []))
    headers = list(dict.fromkeys(headers))

    result = {}
    target = load_target_data(target_json_example)
    sample = unwrap_target_sample(target)

    for field, value in sample.items():
        spec = mapping_spec.get(field, {}) if isinstance(mapping_spec, dict) else {}
        source = spec.get('source') if isinstance(spec, dict) else None
        if source not in headers:
            best_header = None
            best_score = 0
            for header in headers:
                score = _header_score(field, header)
                if score > best_score:
                    best_header = header
                    best_score = score
            if best_score >= 10:
                source = best_header
            else:
                source = None
        result[field] = {
            'source': source,
            'type': spec.get('type') if isinstance(spec, dict) else None,
            'confidence': spec.get('confidence') if isinstance(spec, dict) else None,
        }
    return result

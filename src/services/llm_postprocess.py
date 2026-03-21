import re


def extract_typescript_code(text: str) -> str:
    if not text:
        return ""

    cleaned = text.strip()

    fenced = re.findall(
        r"```(?:ts|typescript)?\\s*(.*?)```",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if fenced:
        cleaned = fenced[0].strip()

    cleaned = cleaned.replace("\\r\\n", "\\n").strip()

    export_idx = cleaned.find("export interface")
    if export_idx == -1:
        export_idx = cleaned.find("export type")
    if export_idx == -1:
        export_idx = cleaned.find("export default function")

    if export_idx > 0:
        cleaned = cleaned[export_idx:].strip()

    return cleaned


def normalize_typescript_code(code: str) -> str:
    code = extract_typescript_code(code)

    replacements = {
        "```typescript": "",
        "```ts": "",
        "```": "",
    }
    for old, new in replacements.items():
        code = code.replace(old, new)

    return code.strip()


def looks_like_typescript(code: str) -> bool:
    if not code:
        return False

    required_markers = [
        "export default function",
        "OutputItem",
    ]
    return all(marker in code for marker in required_markers)


def preview_is_informative(preview: str) -> tuple[bool, str]:
    preview_lower = preview.lower()

    if '"preview_quality": "poor"' in preview_lower:
        return False, "File preview is poor. The file does not provide enough structured data for reliable TypeScript generation."

    if '"format": "image"' in preview_lower:
        return False, "Image input is not supported as a reliable data source in MVP because OCR is not implemented."

    return True, ""
import re


def extract_typescript_code(text: str) -> str:
    if not text:
        return ""

    cleaned = text.strip()

    fenced = re.findall(
        r"```(?:ts|typescript)?\s*(.*?)```",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if fenced:
        cleaned = fenced[0].strip()

    cleaned = cleaned.replace("\r\n", "\n").strip()

    export_idx = cleaned.find("export interface")
    if export_idx == -1:
        export_idx = cleaned.find("export type")
    if export_idx == -1:
        export_idx = cleaned.find("export default function")

    if export_idx > 0:
        cleaned = cleaned[export_idx:].strip()

    return cleaned


def looks_like_typescript(code: str) -> bool:
    if not code:
        return False

    required_markers = [
        "export default function",
        "OutputItem",
    ]
    return all(marker in code for marker in required_markers)


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
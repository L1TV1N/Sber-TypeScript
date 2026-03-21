import base64
import csv
import io
import json
from pathlib import Path

import pandas as pd
from docx import Document
from pypdf import PdfReader


def _detect_csv_delimiter(sample_text: str) -> str:
    candidates = [";", ",", "\t", "|"]
    counts = {d: sample_text.count(d) for d in candidates}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else ","


def preview_csv_from_base64(base64file: str) -> str:
    raw = base64.b64decode(base64file)
    text = raw.decode("utf-8-sig", errors="ignore")

    sample = "\n".join(text.splitlines()[:5])
    delimiter = _detect_csv_delimiter(sample)

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)

    result = {
        "format": "csv",
        "delimiter": delimiter,
        "columns": reader.fieldnames or [],
        "sample_rows": rows[:5],
        "total_sampled_rows": min(len(rows), 5),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def preview_excel_from_base64(base64file: str) -> str:
    raw = base64.b64decode(base64file)
    bio = io.BytesIO(raw)

    excel = pd.ExcelFile(bio)
    sheets_result = []

    for sheet_name in excel.sheet_names[:3]:
        bio.seek(0)
        df = pd.read_excel(bio, sheet_name=sheet_name)
        df = df.fillna("")
        sheets_result.append(
            {
                "sheet_name": sheet_name,
                "columns": list(df.columns.astype(str)),
                "sample_rows": df.head(5).to_dict(orient="records"),
            }
        )

    result = {
        "format": "excel",
        "sheets": sheets_result,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def preview_pdf_from_base64(base64file: str) -> str:
    raw = base64.b64decode(base64file)
    bio = io.BytesIO(raw)

    reader = PdfReader(bio)
    pages_text = []
    for page in reader.pages[:5]:
        text = page.extract_text() or ""
        pages_text.append(text[:3000])

    result = {
        "format": "pdf",
        "pages_preview": pages_text,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def preview_docx_from_base64(base64file: str) -> str:
    raw = base64.b64decode(base64file)
    temp_path = Path("temp_preview.docx")
    temp_path.write_bytes(raw)

    doc = Document(str(temp_path))

    paragraphs = [p.text for p in doc.paragraphs[:30] if p.text.strip()]
    tables = []

    for table in doc.tables[:3]:
        rows = []
        for row in table.rows[:6]:
            rows.append([cell.text for cell in row.cells])
        tables.append(rows)

    try:
        temp_path.unlink(missing_ok=True)
    except Exception:
        pass

    result = {
        "format": "docx",
        "paragraphs": paragraphs[:20],
        "tables": tables,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def preview_image_from_base64(base64file: str) -> str:
    return json.dumps(
        {
            "format": "image",
            "note": "Image OCR is not implemented deeply in MVP.",
        },
        ensure_ascii=False,
        indent=2,
    )


def build_file_preview(file_name: str, base64file: str) -> str:
    extension = Path(file_name).suffix.lower()

    if extension == ".csv":
        return preview_csv_from_base64(base64file)

    if extension in [".xls", ".xlsx"]:
        return preview_excel_from_base64(base64file)

    if extension == ".pdf":
        return preview_pdf_from_base64(base64file)

    if extension == ".docx":
        return preview_docx_from_base64(base64file)

    if extension in [".png", ".jpg", ".jpeg"]:
        return preview_image_from_base64(base64file)

    return json.dumps(
        {
            "format": "unknown",
            "note": f"Unsupported extension: {extension}",
        },
        ensure_ascii=False,
        indent=2,
    )
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """
Ты senior data engineer. Верни только JSON mapping spec.

Правила:
- Никакого TypeScript.
- Никаких пояснений.
- Только один JSON-объект.
- Источник данных только extracted_preview.
- Для CSV/XLS/XLSX source должен быть названием реальной колонки.
- Для DOCX/PDF source должен быть реальным ключом или меткой из key_lines / kv_candidates.
- Если надёжного источника нет, ставь source = null.
- Формат каждого поля:
  {{
    "source": string | null,
    "type": "string" | "number" | "boolean",
    "confidence": "high" | "medium" | "low"
  }}
- Не придумывай поля и колонки.
"""

mapping_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "user",
            '''
Имя файла: {file_name}
Расширение: {file_extension}

Target schema:
{target_schema}

Extracted preview:
{extracted_preview}

Верни только JSON mapping spec.
'''.strip(),
        ),
    ]
)

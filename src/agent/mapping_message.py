from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """
Ты senior data engineer. Твоя задача — по preview входного файла и target schema вернуть ТОЛЬКО JSON mapping spec.

Важно:
- Источник данных только extracted_preview.
- Для CSV/XLS/XLSX используй реальные колонки из preview.
- Не придумывай несуществующие колонки.
- Для каждого поля из target schema верни объект вида:
  {{
    "source": string | null,
    "type": "string" | "number" | "boolean",
    "confidence": "high" | "medium" | "low"
  }}
- Если подходящей колонки нет, ставь source = null.
- Для boolean выбирай source только если реально видно колонку/значение, иначе null.
- Верни один JSON объект, где ключи — поля target schema.
- Без markdown. Без пояснений.
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

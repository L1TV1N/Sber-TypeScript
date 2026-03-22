from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """
Ты senior data engineer. Твоя задача — по preview PDF/DOCX документа и target schema вернуть ТОЛЬКО JSON extraction plan.

Верни JSON объект, где ключи — поля target schema.
Для каждого поля верни объект вида:
{{
  "kind": "label_value" | "enum_choice" | "multi_option",
  "labels": string[],
  "patterns": string[],
  "option_patterns": {{"VALUE": string[]}},
  "confidence": "high" | "medium" | "low"
}}

Правила:
- Источник данных только extracted_preview.
- Не придумывай отсутствующие значения.
- Для обычных строковых полей используй kind=label_value и labels.
- Для полей-выборов с YES/NO/NOWHERE и похожими значениями используй kind=enum_choice и option_patterns.
- Для полей-массивов используй kind=multi_option и option_patterns.
- labels, patterns и option_patterns должны содержать реальные фразы из preview или очень близкие к ним.
- Если поле не удалось уверенно сопоставить, верни пустые arrays и confidence=low.
- Верни только JSON. Без markdown. Без пояснений.
"""

document_mapping_prompt = ChatPromptTemplate.from_messages(
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

Верни только JSON extraction plan.
'''.strip(),
        ),
    ]
)

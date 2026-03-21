# Sber TypeScript Generator

Минималистичный backend + UI для кейса по генерации **TypeScript-кода преобразования табличных данных** в целевую JSON-структуру.

Проект принимает:

- файл с табличными данными
- пример целевого JSON

и возвращает:

- **TypeScript-конвертер**, который преобразует входной файл в массив объектов нужной структуры.

---

## О проекте

Сервис решает прикладную задачу:

1. пользователь загружает исходный файл с табличными данными
2. пользователь загружает пример целевого JSON
3. backend извлекает preview структуры данных
4. LLM генерирует TypeScript-код преобразования
5. результат отображается в UI и может быть скачан как `.ts`

---

## Возможности MVP

### Что уже реализовано

- генерация TypeScript-кода из файла + JSON-примера
- интеграция с **GigaChat**
- backend на **FastAPI**
- UI для демонстрации сценария кейса
- загрузка:
  - `CSV`
  - `XLS / XLSX`
  - `PDF`
  - `DOCX`
  - `PNG / JPG`  
    на уровне preview / расширяемой поддержки
- endpoint для генерации по загруженным файлам
- endpoint для генерации на встроенном demo-примере
- пост-обработка ответа LLM
- проверка, похож ли результат на валидный TypeScript
- сохранение результата в `generated_converter.ts`

---

## Стек

- Python 3.9
- FastAPI
- LangChain
- GigaChat
- pandas
- pypdf
- python-docx
- HTML/CSS/JS UI

---

## Архитектура

```text
src/
├── agent/
│   ├── __init__.py
│   ├── main.py
│   ├── message.py
│   └── state.py
├── api/
│   ├── chat/
│   │   └── routers.py
│   └── v1/
│       ├── routers.py
│       └── schemas.py
├── config/
│   ├── __init__.py
│   └── app/
│       └── config.py
├── services/
│   ├── file_preview.py
│   └── llm_postprocess.py
└── main.py

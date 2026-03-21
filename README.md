# 🚀 Sber TypeScript Generator

> Минималистичный backend + UI для **автоматической генерации TypeScript-кода** преобразования табличных данных в целевую JSON-структуру.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![GigaChat](https://img.shields.io/badge/GigaChat-LLM-orange)](https://gigachat.ru/)

---

## 📋 Возможности

### Что это делает?

Сервис принимает:
- 📄 Файл с табличными данными (CSV, Excel, PDF, Word, Images)
- 📝 Пример целевого JSON-формата

И возвращает:
- ✨ **Готовый TypeScript-код** для автоматического преобразования данных

### Сценарий использования

```
1️⃣  Загрузить исходный файл с табличными данными
        ↓
2️⃣  Загрузить пример целевого JSON
        ↓
3️⃣  Backend анализирует структуру данных
        ↓
4️⃣  LLM генерирует TypeScript-конвертер
        ↓
5️⃣  Скачать готовый .ts файл
```

---

## 🎨 User Interface

### Main Dashboard
*Главный экран приложения с загрузкой файлов*
<img width="1813" height="901" alt="image" src="https://github.com/user-attachments/assets/3a321b43-d9cd-469f-934f-b05a260234bb" />

### Мобильная версия
![photo_5330524795319292387_w](https://github.com/user-attachments/assets/b132aa32-2a0a-4d5a-b1c4-6f2672ffe029)


---

## ⚡ Быстрый старт

### Требования
- Python 3.9+
- GigaChat API credentials

### Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/L1TV1N/Sber-TypeScript.git
cd Sber-TypeScript

# 2. Создать виртуальное окружение
python -m venv .venv

# 3. Активировать окружение
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env и добавьте GIGACHAT_CREDENTIALS
```

### Запуск

```bash
# Установить PYTHONPATH
export PYTHONPATH=src

# Запустить приложение
python src/main.py
```

По умолчанию приложение будет доступно на: **http://localhost:8000**

---

## 🛠 Технологический стек

| Компонент | Технология |
|-----------|-----------|
| **Backend** | FastAPI |
| **Async Worker** | LangGraph |
| **LLM** | GigaChat (Sber) |
| **Data Processing** | pandas, pypdf, python-docx |
| **Frontend** | HTML/CSS/JS с FastUI |
| **Python** | 3.9+ |

---

## 🏗 Архитектура проекта

### Структура кода

```text
src/
├── agent/                    # LLM Agent логика
│   ├── __init__.py
│   ├── main.py              # Основной agent executor
│   ├── message.py           # Обработка сообщений
│   └── state.py             # Состояние conversation
│
├── api/                      # REST API endpoints
│   ├── chat/                # UI routes
│   │   └── routers.py
│   └── v1/                  # API routes
│       ├── routers.py       # Генерация кода endpoint
│       └── schemas.py       # Pydantic модели
│
├── config/                   # Конфигурация
│   ├── __init__.py
│   └── app/
│       └── config.py        # AppSettings
│
├── services/                 # Бизнес-логика
│   ├── file_preview.py      # Парсинг файлов
│   ├── json_schema.py       # JSON schema анализ
│   └── llm_postprocess.py   # Постобработка результатов
│
└── main.py                   # Entry point
```

### Data Flow

```
┌─────────────────┐
│  User Upload    │
│ (File + JSON)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  File Preview Service   │  ← Парсит CSV, PDF, Excel, Images
│   (Extract Samples)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  JSON Schema Analysis   │  ← Анализирует целевую структуру
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  LLM Prompt Builder     │  ← Формирует промпт для GigaChat
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  GigaChat Generation    │  ← Генерирует TypeScript код
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Post-processing        │  ← Валидация и очистка результата
│  (Validation)           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Return Generated Code  │
│  (Download as .ts)      │
└─────────────────────────┘
```

---

## 📦 Поддерживаемые форматы

### Входные файлы
- ✅ **CSV** — табличные данные
- ✅ **Excel** (XLS, XLSX) — электронные таблицы
- ✅ **PDF** — текстовые документы
- ✅ **Word** (DOCX) — текстовые документы
- ✅ **Images** (PNG, JPG) — OCR поддержка

### Выходные файлы
- 📝 **TypeScript** (.ts) — готовый к использованию функции

---

## 🔌 API Endpoints

### 1. Web UI
```
GET /
```
Главный веб-интерфейс приложения

### 2. Генерация кода
```
POST /api/v1/prediction
Content-Type: multipart/form-data

Parameters:
  - file: File (табличные данные)
  - json_example: str (JSON пример)
  - file_type: str (csv|excel|pdf|docx|image)
```

**Response:**
```json
{
  "generated_code": "export function convertData(...) { ... }",
  "status": "success",
  "filename": "generated_converter.ts"
}
```

---

## 🚀 Примеры использования

### Пример 1: CSV → TypeScript

**Входные данные (data.csv):**
```csv
id,name,email,age
1,John Doe,john@example.com,30
2,Jane Smith,jane@example.com,28
```

**JSON пример (target.json):**
```json
{
  "id": 1,
  "name": "string",
  "email": "string",
  "age": "number"
}
```

**Результат:**
```typescript
export function convertData(csvData: string): CsvRow[] {
  return csvData.split('\n').slice(1).map(line => {
    const [id, name, email, age] = line.split(',');
    return {
      id: parseInt(id),
      name: name.trim(),
      email: email.trim(),
      age: parseInt(age)
    };
  });
}
```

---

## 🔧 Конфигурация

### .env файл

```env
# Server
APP_HOST=0.0.0.0
APP_PORT=8000

# GigaChat
GIGACHAT_CREDENTIALS=your_credentials_here
GIGACHAT_SCOPE=GIGACHAT_API_CORP
GIGACHAT_VERIFY_SSL_CERTS=False
GIGACHAT_MODEL=GigaChat-2
```

---

## 📊 Возможности MVP

✅ **Реализовано:**
- Генерация TypeScript-кода из табличных данных + JSON примера
- Интеграция с GigaChat LLM
- Backend на FastAPI с async поддержкой
- Web UI для удобного использования
- Поддержка множества форматов файлов
- REST API для программной интеграции
- Post-processing и валидация результата
- Сохранение результата в файл

🚀 **Планируется:**
- [ ] Batch обработка множественных файлов
- [ ] История генераций
- [ ] Пользовательские правила трансформации
- [ ] Экспорт в другие языки (Python, Go, JS)
- [ ] WebSocket для real-time обновлений

---

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

## 👥 Команда

Проект разработан для **Sber Hackathon 2026**

---

## 🤝 Поддержка

Для вопросов и предложений создайте [issue](https://github.com/L1TV1N/Sber-TypeScript/issues)

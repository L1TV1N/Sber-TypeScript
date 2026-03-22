from pydantic import BaseModel, Field


class GenerateTsRequest(BaseModel):
    file_name: str = Field(description="Имя входного файла")
    file_base64: str = Field(description="Файл в base64")
    target_json_example: str = Field(description="Пример JSON-структуры результата")


class GenerateTsResponse(BaseModel):
    content: str = Field(description="Сгенерированный TypeScript-код")
    extracted_preview: str = Field(description="Извлечённый preview входных данных")
    target_schema: str = Field(description="Структура, извлечённая из JSON")
    status: str = Field(description="Статус обработки", default="ok")
    valid_ts: bool = Field(description="Похоже ли на валидный TS-ответ", default=True)
    message: str = Field(description="Служебное сообщение", default="")


class GenerateFromExampleResponse(BaseModel):
    content: str = Field(description="Сгенерированный TypeScript-код")
    extracted_preview: str = Field(description="Извлечённый preview входных данных")
    target_schema: str = Field(description="Структура, извлечённая из JSON")
    status: str = Field(description="Статус обработки", default="ok")
    valid_ts: bool = Field(description="Похоже ли на валидный TS-ответ", default=True)
    message: str = Field(description="Служебное сообщение", default="")


class LogsResponse(BaseModel):
    status: str = Field(description="Статус ответа", default="ok")
    lines: list[str] = Field(description="Последние строки файла логов", default_factory=list)


class ValidateTsRequest(BaseModel):
    file_name: str = Field(description="Имя исходного файла")
    file_base64: str = Field(description="Исходный файл в base64")
    target_json_example: str = Field(description="Пример JSON-структуры результата")
    ts_code: str = Field(description="TypeScript-код для проверки")


class ValidateTsResponse(BaseModel):
    status: str = Field(description="Статус проверки", default="ok")
    is_valid: bool = Field(description="Успешна ли проверка", default=False)
    message: str = Field(description="Краткий итог проверки", default="")
    details: list[str] = Field(description="Детали проверки", default_factory=list)
    compiler_output: str = Field(description="Вывод компилятора TypeScript", default="")
    runtime_output: str = Field(description="Вывод выполнения Node.js", default="")
    result_preview: str = Field(description="Превью результата выполнения TS", default="")
    source_record_count: int | None = Field(description="Оценка количества записей в исходном файле", default=None)
    output_record_count: int | None = Field(description="Количество записей, которое вернул TS", default=None)

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
    raw_content: str = Field(description="Сырой ответ LLM", default="")
    message: str = Field(description="Служебное сообщение", default="")


class GenerateFromExampleResponse(BaseModel):
    content: str = Field(description="Сгенерированный TypeScript-код")
    extracted_preview: str = Field(description="Извлечённый preview входных данных")
    target_schema: str = Field(description="Структура, извлечённая из JSON")
    status: str = Field(description="Статус обработки", default="ok")
    valid_ts: bool = Field(description="Похоже ли на валидный TS-ответ", default=True)
    message: str = Field(description="Служебное сообщение", default="")
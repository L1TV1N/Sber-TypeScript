from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class AppSettings(BaseSettings):
    app_host: str = Field(validation_alias="APP_HOST", default="0.0.0.0")
    app_port: int = Field(validation_alias="APP_PORT", default=8000)

    gigachat_credentials: str = Field(validation_alias="GIGACHAT_CREDENTIALS")
    gigachat_scope: str = Field(validation_alias="GIGACHAT_SCOPE", default="GIGACHAT_API_CORP")
    gigachat_verify_ssl_certs: bool = Field(
        validation_alias="GIGACHAT_VERIFY_SSL_CERTS",
        default=False,
    )
    gigachat_model: str = Field(validation_alias="GIGACHAT_MODEL", default="GigaChat-2")
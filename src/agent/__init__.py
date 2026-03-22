from langchain_core.output_parsers import StrOutputParser
from langchain_gigachat import GigaChat

from agent.message import agent_prompt
from agent.mapping_message import mapping_prompt
from config import APP_CONFIG


_llm = None
chain = None
mapping_chain = None


def _build_llm() -> GigaChat:
    credentials = APP_CONFIG.app.gigachat_credentials
    if not credentials:
        raise RuntimeError(
            "Не задан GIGACHAT_CREDENTIALS. Добавьте его в .env или переменные окружения."
        )

    return GigaChat(
        credentials=credentials,
        scope=APP_CONFIG.app.gigachat_scope,
        verify_ssl_certs=APP_CONFIG.app.gigachat_verify_ssl_certs,
        profanity_check=False,
        temperature=0.1,
        model=APP_CONFIG.app.gigachat_model,
    )


def get_llm() -> GigaChat:
    global _llm
    if _llm is None:
        _llm = _build_llm()
    return _llm


def get_chain():
    global chain
    if chain is None:
        chain = agent_prompt | get_llm() | StrOutputParser()
    return chain


def get_mapping_chain():
    global mapping_chain
    if mapping_chain is None:
        mapping_chain = mapping_prompt | get_llm() | StrOutputParser()
    return mapping_chain

from langchain_core.output_parsers import StrOutputParser
from langchain_gigachat import GigaChat

from agent.message import agent_prompt
from config import APP_CONFIG

llm = GigaChat(
    credentials=APP_CONFIG.app.gigachat_credentials,
    scope=APP_CONFIG.app.gigachat_scope,
    verify_ssl_certs=APP_CONFIG.app.gigachat_verify_ssl_certs,
    profanity_check=False,
    temperature=0.1,
    model=APP_CONFIG.app.gigachat_model,
)

chain = agent_prompt | llm | StrOutputParser()
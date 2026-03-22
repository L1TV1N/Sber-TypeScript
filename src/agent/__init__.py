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

from agent.mapping_message import mapping_prompt
mapping_chain = mapping_prompt | llm | StrOutputParser()

from agent.document_mapping_message import document_mapping_prompt
document_mapping_chain = document_mapping_prompt | llm | StrOutputParser()

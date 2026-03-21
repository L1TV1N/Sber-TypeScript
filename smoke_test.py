import os

from dotenv import load_dotenv
from langchain_gigachat import GigaChat

load_dotenv()

credentials = os.getenv("GIGACHAT_CREDENTIALS")
scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_CORP")
verify_ssl_certs = str(os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "False")).lower() == "true"
model = os.getenv("GIGACHAT_MODEL", "GigaChat-2")

print("GIGACHAT_SCOPE =", scope)
print("GIGACHAT_MODEL =", model)
print("GIGACHAT_VERIFY_SSL_CERTS =", verify_ssl_certs)
print("TOKEN EXISTS =", bool(credentials))
print("TOKEN LENGTH =", len(credentials) if credentials else 0)
print("TOKEN PREFIX =", credentials[:20] if credentials else "NO_TOKEN")
print("TOKEN SUFFIX =", credentials[-10:] if credentials else "NO_TOKEN")
print("TOKEN HAS SPACES =", " " in credentials if credentials else False)
print("TOKEN HAS NEWLINES =", "\n" in credentials if credentials else False)
print("TOKEN STARTS/ENDS CLEAN =", credentials == credentials.strip() if credentials else False)

llm = GigaChat(
    credentials=credentials,
    scope=scope,
    verify_ssl_certs=verify_ssl_certs,
    profanity_check=False,
    temperature=0.1,
    model=model,
)

result = llm.invoke("Скажи одним словом: работает")
print(result.content)
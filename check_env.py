import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GIGACHAT_CREDENTIALS")
print("RAW REPR:", repr(token))
print("LEN:", len(token) if token else 0)
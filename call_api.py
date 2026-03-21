import json
import requests

with open("request.json", "r", encoding="utf-8") as f:
    payload = json.load(f)

response = requests.post(
    "http://127.0.0.1:8000/api/v1/prediction",
    json=payload,
    timeout=180,
)

print("STATUS:", response.status_code)

data = response.json()
print(data)

if response.status_code == 200:
    with open("generated_converter.ts", "w", encoding="utf-8") as f:
        f.write(data["content"])
    print("generated_converter.ts saved")
import base64
import json

with open("crmData.csv", "rb") as f:
    file_base64 = base64.b64encode(f.read()).decode("utf-8")

with open("crm.json", "r", encoding="utf-8") as f:
    target_json = json.load(f)

request_data = {
    "file_name": "crmData.csv",
    "file_base64": file_base64,
    "target_json_example": json.dumps(target_json, ensure_ascii=False),
}

with open("request.json", "w", encoding="utf-8") as f:
    json.dump(request_data, f, ensure_ascii=False, indent=2)

print("request.json created")
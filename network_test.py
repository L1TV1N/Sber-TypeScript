import requests

try:
    response = requests.get(
        "https://gigachat.devices.sberbank.ru/",
        timeout=20,
        verify=False,
    )
    print("STATUS:", response.status_code)
    print(response.text[:500])
except Exception as e:
    print("ERROR:", repr(e))
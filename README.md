

# Create venv

```bash
uv venv
```

# Activating a virtual environment
```bash
source .venv/bin/activate
```

# Install dependencies

```bash
uv sync
```

# Run app

## Configure environments

```bash
mv .env.example .env
```

Add your creds `GIGACHAT_CREDENTIALS`. If creds personal, set `GIGACHAT_SCOPE=GIGACHAT_API_PERS`

More information about gigachat env look [here](GIGACHAT_SCOPE=GIGACHAT_API_CORP)


## Run in console
```bash
PYTHONPATH=src python src/main.py
```

## Run debug (vs code)

Just run Python Debugger: FastAPI

# Available endpoints
- `/` - simple chat (fastui)
- `/api/v1/prediction` - api

# Curl example

```bash
curl --location 'localhost:8000/api/v1/prediction' \
--header 'Content-Type: application/json' \
--data '{
    "message": "hello"
}'
```

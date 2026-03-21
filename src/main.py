import uvicorn

from api import app_main
from config import APP_CONFIG
from uvicorn_logging_config import LOGGING_CONFIG


def main():
    uvicorn.run(
        app_main,
        host=APP_CONFIG.app.app_host,
        port=APP_CONFIG.app.app_port,
        access_log=False,
        log_config=LOGGING_CONFIG,
        reload=False,
    )


if __name__ == "__main__":
    main()

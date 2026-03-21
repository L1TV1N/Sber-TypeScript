import contextlib

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import prebuilt_html

from api.chat.routers import ui_router
from api.v1.routers import api_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app_main = FastAPI(
    title="Covnerter agent service",
    lifespan=lifespan,
)


app_main.include_router(api_router, prefix="/api/v1")
app_main.include_router(ui_router)


@app_main.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    # prebuilt_html загружает готовый JS бандл с CDN
    return HTMLResponse(prebuilt_html(title="Agent UI", api_root_url="/api/ui"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import cotizaciones, oportunidades, sync

settings = get_settings()

app = FastAPI(
    title="Talinay Compras Públicas API",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oportunidades.router)
app.include_router(cotizaciones.router)
app.include_router(sync.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": settings.app_version}

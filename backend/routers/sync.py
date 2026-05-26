from fastapi import APIRouter

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/compras-agiles")
def sync_compras_agiles() -> dict:
    return {"sincronizadas": 0, "nuevas": 0, "errores": []}


@router.post("/licitaciones")
def sync_licitaciones() -> dict:
    return {"sincronizadas": 0, "nuevas": 0, "errores": []}

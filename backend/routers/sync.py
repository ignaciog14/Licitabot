from fastapi import APIRouter, HTTPException

from database import get_db
from services.apify import ApifyError, sincronizar_compras_agiles

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/compras-agiles")
def sync_compras_agiles() -> dict:
    errores: list[str] = []

    try:
        oportunidades = sincronizar_compras_agiles()
    except ApifyError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if not oportunidades:
        _registrar_sync_log("compras_agiles", 0, 0, errores)
        return {"sincronizadas": 0, "nuevas": 0, "errores": errores}

    try:
        db = get_db()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    codigos = [op["codigo"] for op in oportunidades]
    existentes = (
        db.table("oportunidades")
        .select("codigo")
        .in_("codigo", codigos)
        .execute()
    )
    set_existentes = {row["codigo"] for row in (existentes.data or [])}

    try:
        db.table("oportunidades").upsert(
            oportunidades, on_conflict="codigo"
        ).execute()
    except Exception as exc:
        errores.append(f"Error en upsert: {exc}")
        _registrar_sync_log("compras_agiles", len(oportunidades), 0, errores)
        raise HTTPException(status_code=500, detail=f"Error guardando en BD: {exc}")

    sincronizadas = len(oportunidades)
    nuevas = sum(1 for c in codigos if c not in set_existentes)

    _registrar_sync_log("compras_agiles", sincronizadas, nuevas, errores)

    return {
        "sincronizadas": sincronizadas,
        "nuevas": nuevas,
        "errores": errores,
    }


@router.post("/licitaciones")
def sync_licitaciones() -> dict:
    """Sync de licitaciones tradicionales (HU-05). Pendiente."""
    return {"sincronizadas": 0, "nuevas": 0, "errores": []}


def _registrar_sync_log(
    tipo: str, encontradas: int, nuevas: int, errores: list[str]
) -> None:
    """Best-effort: no tumbar el endpoint por fallar el log."""
    try:
        db = get_db()
        db.table("sync_log").insert(
            {
                "tipo": tipo,
                "oportunidades_encontradas": encontradas,
                "oportunidades_nuevas": nuevas,
                "errores": errores or None,
            }
        ).execute()
    except Exception:
        pass

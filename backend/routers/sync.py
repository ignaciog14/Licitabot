from fastapi import APIRouter, HTTPException

from database import get_db
from routers.configuracion import get_keywords
from services.keywords import calcular_score
from services.mercado_publico import MercadoPublicoError, sincronizar_licitaciones

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/compras-agiles")
def sync_compras_agiles() -> dict:
    try:
        oportunidades = sincronizar_licitaciones()
    except MercadoPublicoError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if not oportunidades:
        _registrar_sync_log("compras_agiles", 0, 0, [])
        return {"sincronizadas": 0, "nuevas": 0, "errores": []}

    try:
        db = get_db()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    keywords = get_keywords()

    # Enriquecer con score de keywords antes de guardar
    for op in oportunidades:
        resultado = calcular_score(op, keywords)
        op["score_relevancia"] = resultado["score"]
        op["keywords_matched"] = resultado["keywords_matched"]
        op["justificacion_ia"] = (
            f"Matcheó: {', '.join(resultado['keywords_matched'])}"
            if resultado["keywords_matched"]
            else "Sin coincidencias con palabras clave"
        )

    codigos = [op["codigo"] for op in oportunidades]
    existentes = (
        db.table("oportunidades").select("codigo").in_("codigo", codigos).execute()
    )
    set_existentes = {row["codigo"] for row in (existentes.data or [])}

    try:
        db.table("oportunidades").upsert(oportunidades, on_conflict="codigo").execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error guardando en BD: {exc}")

    nuevas = len([op for op in oportunidades if op["codigo"] not in set_existentes])
    _registrar_sync_log("compras_agiles", len(oportunidades), nuevas, [])

    return {"sincronizadas": len(oportunidades), "nuevas": nuevas, "errores": []}


@router.post("/licitaciones")
def sync_licitaciones() -> dict:
    return sync_compras_agiles()


def _registrar_sync_log(tipo: str, encontradas: int, nuevas: int, errores: list) -> None:
    try:
        db = get_db()
        db.table("sync_log").insert({
            "tipo": tipo,
            "oportunidades_encontradas": encontradas,
            "oportunidades_nuevas": nuevas,
            "errores": errores or None,
        }).execute()
    except Exception:
        pass

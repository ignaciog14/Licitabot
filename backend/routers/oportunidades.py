from fastapi import APIRouter, HTTPException

from database import get_db
from routers.configuracion import get_keywords
from services.keywords import calcular_score

router = APIRouter(prefix="/oportunidades", tags=["oportunidades"])


@router.get("")
def listar_oportunidades(min_score: int = 1) -> list[dict]:
    """Devuelve oportunidades con score >= min_score. Default 1 = solo las que matchean algo."""
    try:
        db = get_db()
        query = db.table("oportunidades").select("*")
        if min_score > 0:
            query = query.gte("score_relevancia", min_score)
        response = query.order("score_relevancia", desc=True).order("created_at", desc=True).execute()
        return response.data or []
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/recalcular-scores")
def recalcular_scores() -> dict:
    """Recalcula el score de TODAS las oportunidades con las keywords actuales."""
    try:
        db = get_db()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    keywords = get_keywords()
    items = db.table("oportunidades").select("id,nombre,descripcion,organismo").execute().data or []

    # Calcular scores en Python y hacer upsert en batch
    updates = []
    for op in items:
        resultado = calcular_score(op, keywords)
        updates.append({
            "id": op["id"],
            "score_relevancia": resultado["score"],
            "keywords_matched": resultado["keywords_matched"],
            "justificacion_ia": (
                f"Matcheó: {', '.join(resultado['keywords_matched'])}"
                if resultado["keywords_matched"]
                else "Sin coincidencias con palabras clave"
            ),
        })

    if updates:
        # Una sola llamada RPC que procesa todo en el servidor
        payload = [
            {
                "id": u["id"],
                "score": u["score_relevancia"],
                "keywords_matched": u["keywords_matched"],
                "justificacion_ia": u["justificacion_ia"],
            }
            for u in updates
        ]
        db.rpc("update_scores_bulk", {"updates": payload}).execute()

    return {"actualizadas": len(updates), "keywords_usadas": len(keywords)}


@router.post("/{oportunidad_id}/analizar")
def reanalizar_oportunidad(oportunidad_id: str) -> dict:
    db = _get_db_or_503()

    response = (
        db.table("oportunidades")
        .select("*")
        .eq("id", oportunidad_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")

    oportunidad = response.data[0]
    resultado = analizar_relevancia(oportunidad)

    db.table("oportunidades").update(
        {
            "score_relevancia": resultado["score"],
            "justificacion_ia": resultado["justificacion"],
            "categoria": resultado["categoria"],
        }
    ).eq("id", oportunidad_id).execute()

    return resultado


@router.post("/{oportunidad_id}/generar-cotizacion")
def generar_cotizacion_endpoint(oportunidad_id: str, force: bool = False) -> dict:
    db = _get_db_or_503()

    response = (
        db.table("oportunidades")
        .select("*")
        .eq("id", oportunidad_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")

    oportunidad = response.data[0]
    score = oportunidad.get("score_relevancia") or 0
    if score < SCORE_UMBRAL_RELEVANTE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Score {score} es menor al umbral {SCORE_UMBRAL_RELEVANTE}; "
                "esta oportunidad no es relevante para Talinay."
            ),
        )

    existente_resp = (
        db.table("cotizaciones")
        .select("*")
        .eq("oportunidad_id", oportunidad_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    existente = existente_resp.data[0] if existente_resp.data else None

    if existente and existente["estado"] == "aprobada":
        raise HTTPException(
            status_code=409,
            detail="La cotización ya está aprobada y no puede regenerarse.",
        )

    if existente and not force:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una cotización para esta oportunidad. Pasa ?force=true para regenerarla.",
        )

    try:
        texto = generar_cotizacion(oportunidad)
    except CotizacionIAError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if existente:
        cot_id = existente["id"]
        db.table("cotizaciones").update(
            {
                "borrador_ia": texto,
                "borrador_editado": None,
                "precio_ofertado": None,
                "plazo_entrega_dias": None,
                "estado": "borrador",
            }
        ).eq("id", cot_id).execute()
        actual = (
            db.table("cotizaciones")
            .select("*")
            .eq("id", cot_id)
            .limit(1)
            .execute()
        )
        return actual.data[0]

    nueva = (
        db.table("cotizaciones")
        .insert(
            {
                "oportunidad_id": oportunidad_id,
                "borrador_ia": texto,
                "estado": "borrador",
            }
        )
        .execute()
    )
    db.table("oportunidades").update({"estado_interno": "cotizado"}).eq(
        "id", oportunidad_id
    ).execute()
    return nueva.data[0]


@router.get("/{oportunidad_id}/cotizacion")
def obtener_cotizacion(oportunidad_id: str) -> dict:
    db = _get_db_or_503()
    response = (
        db.table("cotizaciones")
        .select("*")
        .eq("oportunidad_id", oportunidad_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="No hay cotización para esta oportunidad",
        )
    return response.data[0]


@router.get("/{oportunidad_id}")
def obtener_oportunidad(oportunidad_id: str) -> dict:
    db = _get_db_or_503()
    response = (
        db.table("oportunidades")
        .select("*")
        .eq("id", oportunidad_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    return response.data[0]


def _get_db_or_503():
    try:
        return get_db()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

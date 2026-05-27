from fastapi import APIRouter, HTTPException

from database import get_db
from services.ia import SCORE_UMBRAL_RELEVANTE, analizar_relevancia

router = APIRouter(prefix="/oportunidades", tags=["oportunidades"])


@router.get("")
def listar_oportunidades(min_score: int = SCORE_UMBRAL_RELEVANTE) -> list[dict]:
    try:
        db = get_db()
        response = (
            db.table("oportunidades")
            .select("*")
            .gte("score_relevancia", min_score)
            .order("score_relevancia", desc=True)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/{oportunidad_id}/analizar")
def reanalizar_oportunidad(oportunidad_id: str) -> dict:
    try:
        db = get_db()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

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

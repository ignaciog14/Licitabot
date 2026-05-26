from fastapi import APIRouter, HTTPException

from database import get_db

router = APIRouter(prefix="/oportunidades", tags=["oportunidades"])


@router.get("")
def listar_oportunidades() -> list[dict]:
    try:
        db = get_db()
        response = (
            db.table("oportunidades")
            .select("*")
            .order("score_relevancia", desc=True)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

from fastapi import APIRouter

from database import get_supabase

router = APIRouter(prefix="/oportunidades", tags=["oportunidades"])


@router.get("")
def listar_oportunidades() -> list[dict]:
    supabase = get_supabase()
    if supabase is None:
        return []
    try:
        response = supabase.table("oportunidades").select("*").execute()
        return response.data or []
    except Exception:
        return []

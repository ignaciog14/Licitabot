from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_db

router = APIRouter(prefix="/configuracion", tags=["configuracion"])

CLAVE_KEYWORDS = "keywords"
DEFAULT_KEYWORDS: list[str] = [
    "librería", "artículos de oficina", "insumos escolares", "papelería",
    "tinta", "tampón", "sello", "plumón", "lápiz", "cuaderno",
    "pintura", "acrílica", "tempera", "pintura tela", "pintura género",
    "brocha", "rodillo", "barniz",
    "manualidades", "materiales didácticos", "materiales escolares", "útiles escolares",
    "poliestireno", "plumavit", "foam", "espuma", "corte a medida",
    "fieltro", "disco de pulir", "paño industrial",
    "silicona", "aceite industrial", "emulsión", "lubricante",
]


class KeywordsPayload(BaseModel):
    keywords: list[str]


def get_keywords() -> list[str]:
    """Lee keywords de BD; devuelve defaults si no hay nada."""
    try:
        db = get_db()
        r = db.table("configuracion").select("valor").eq("clave", CLAVE_KEYWORDS).limit(1).execute()
        if r.data:
            return r.data[0]["valor"]
    except Exception:
        pass
    return DEFAULT_KEYWORDS


@router.get("/keywords")
def listar_keywords() -> dict:
    return {"keywords": get_keywords()}


@router.put("/keywords")
def actualizar_keywords(payload: KeywordsPayload) -> dict:
    keywords = [kw.strip() for kw in payload.keywords if kw.strip()]
    if not keywords:
        raise HTTPException(status_code=400, detail="Debe haber al menos una palabra clave")
    try:
        db = get_db()
        db.table("configuracion").upsert(
            {"clave": CLAVE_KEYWORDS, "valor": keywords},
            on_conflict="clave",
        ).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error guardando: {exc}")
    return {"keywords": keywords}

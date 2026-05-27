from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_db

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])

ESTADOS_VALIDOS = {"borrador", "aprobada", "enviada"}
ESTADOS_OPORTUNIDAD_VALIDOS = {
    "pendiente",
    "cotizado",
    "descartado",
    "ganado",
    "perdido",
}


class CotizacionUpdate(BaseModel):
    borrador_editado: Optional[str] = None
    precio_ofertado: Optional[float] = None
    plazo_entrega_dias: Optional[int] = None
    estado: Optional[str] = None
    estado_oportunidad: Optional[str] = None


@router.patch("/{cotizacion_id}")
def actualizar_cotizacion(cotizacion_id: str, payload: CotizacionUpdate) -> dict:
    try:
        db = get_db()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    response = (
        db.table("cotizaciones")
        .select("*")
        .eq("id", cotizacion_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    cotizacion = response.data[0]

    if cotizacion["estado"] == "aprobada":
        raise HTTPException(
            status_code=409,
            detail="La cotización ya está aprobada y no se puede modificar.",
        )

    if payload.estado is not None and payload.estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Permitidos: {sorted(ESTADOS_VALIDOS)}",
        )

    if (
        payload.estado_oportunidad is not None
        and payload.estado_oportunidad not in ESTADOS_OPORTUNIDAD_VALIDOS
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "estado_oportunidad inválido. Permitidos: "
                f"{sorted(ESTADOS_OPORTUNIDAD_VALIDOS)}"
            ),
        )

    update: dict = {}
    if payload.borrador_editado is not None:
        update["borrador_editado"] = payload.borrador_editado
    if payload.precio_ofertado is not None:
        update["precio_ofertado"] = payload.precio_ofertado
    if payload.plazo_entrega_dias is not None:
        update["plazo_entrega_dias"] = payload.plazo_entrega_dias
    if payload.estado is not None:
        update["estado"] = payload.estado

    if update:
        db.table("cotizaciones").update(update).eq("id", cotizacion_id).execute()

    if payload.estado_oportunidad is not None:
        db.table("oportunidades").update(
            {"estado_interno": payload.estado_oportunidad}
        ).eq("id", cotizacion["oportunidad_id"]).execute()

    actual = (
        db.table("cotizaciones")
        .select("*")
        .eq("id", cotizacion_id)
        .limit(1)
        .execute()
    )
    return actual.data[0]

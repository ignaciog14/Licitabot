from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from database import get_db
from services.pdf import generar_pdf_cotizacion

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])

ESTADOS_VALIDOS = {"borrador", "aprobada", "enviada"}
ESTADOS_OPORTUNIDAD_VALIDOS = {
    "pendiente",
    "cotizado",
    "descartado",
    "ganado",
    "perdido",
}

BUCKET_COTIZACIONES = "cotizaciones"


class CotizacionUpdate(BaseModel):
    borrador_editado: Optional[str] = None
    precio_ofertado: Optional[float] = None
    plazo_entrega_dias: Optional[int] = None
    estado: Optional[str] = None
    estado_oportunidad: Optional[str] = None


@router.patch("/{cotizacion_id}")
def actualizar_cotizacion(cotizacion_id: str, payload: CotizacionUpdate) -> dict:
    db = _get_db()

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


@router.get("/{cotizacion_id}/pdf")
def descargar_pdf(cotizacion_id: str):
    db = _get_db()

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

    if cotizacion["estado"] != "aprobada":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden generar PDFs de cotizaciones aprobadas.",
        )

    op_resp = (
        db.table("oportunidades")
        .select("*")
        .eq("id", cotizacion["oportunidad_id"])
        .limit(1)
        .execute()
    )
    if not op_resp.data:
        raise HTTPException(
            status_code=500, detail="Oportunidad asociada no encontrada"
        )
    oportunidad = op_resp.data[0]

    pdf_bytes = generar_pdf_cotizacion(cotizacion, oportunidad)
    filename = f"cotizacion-{oportunidad['codigo']}-talinay.pdf"

    # Best-effort: subir al bucket y persistir URL. Si Storage no está
    # configurado (bucket inexistente, RLS, etc.), igual devolvemos el PDF.
    _publicar_en_storage(db, filename, pdf_bytes, cotizacion_id)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


def _publicar_en_storage(db, filename: str, pdf_bytes: bytes, cotizacion_id: str) -> None:
    bucket = db.storage.from_(BUCKET_COTIZACIONES)
    try:
        try:
            bucket.upload(
                path=filename,
                file=pdf_bytes,
                file_options={
                    "content-type": "application/pdf",
                    "upsert": "true",
                },
            )
        except Exception:
            # Fallback si la versión del SDK no soporta upsert en file_options
            try:
                bucket.remove([filename])
            except Exception:
                pass
            bucket.upload(
                path=filename,
                file=pdf_bytes,
                file_options={"content-type": "application/pdf"},
            )

        pdf_url = bucket.get_public_url(filename)
        db.table("cotizaciones").update({"pdf_url": pdf_url}).eq(
            "id", cotizacion_id
        ).execute()
    except Exception:
        # Storage no disponible: el usuario igual recibe el PDF en la respuesta.
        return


def _get_db():
    try:
        return get_db()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

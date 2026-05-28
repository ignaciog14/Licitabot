"""Cliente para la API oficial de Mercado Público."""

from typing import Any

import httpx

from config import get_settings

MP_BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico"
MP_TIMEOUT = 30
MAX_RESULTADOS = 10
MAX_REINTENTOS = 4
ESPERA_REINTENTO = 8  # segundos entre reintentos por 429


class MercadoPublicoError(Exception):
    pass


def sincronizar_licitaciones() -> list[dict[str, Any]]:
    import time

    settings = get_settings()
    ticket = settings.mp_ticket
    if not ticket:
        raise MercadoPublicoError("MP_TICKET no configurado en backend/.env")

    url = f"{MP_BASE_URL}/licitaciones.json"
    params = {"estado": "publicada", "ticket": ticket}

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            r = httpx.get(url, params=params, timeout=MP_TIMEOUT)
        except httpx.HTTPError as exc:
            raise MercadoPublicoError(f"Error de red: {exc}") from exc

        if r.status_code == 429 or (r.status_code == 200 and r.json().get("Codigo") == 10500):
            if intento < MAX_REINTENTOS:
                time.sleep(ESPERA_REINTENTO)
                continue
            raise MercadoPublicoError("API de Mercado Público ocupada, intente de nuevo en unos segundos")

        if r.status_code >= 400:
            raise MercadoPublicoError(f"API respondió {r.status_code}: {r.text[:200]}")

        data = r.json()
        if data.get("Codigo") and data["Codigo"] not in (200, None):
            raise MercadoPublicoError(f"API error: {data.get('Mensaje')}")

        listado = data.get("Listado") or []
        return [_mapear(item) for item in listado[:MAX_RESULTADOS] if item.get("CodigoExterno")]

    raise MercadoPublicoError("No se pudo conectar a Mercado Público tras varios intentos")


def _mapear(item: dict) -> dict[str, Any]:
    comprador = item.get("Comprador") or {}
    fechas = item.get("Fechas") or {}

    return {
        "codigo": item["CodigoExterno"],
        "tipo": "licitacion",
        "nombre": item.get("Nombre") or "",
        "organismo": comprador.get("NombreOrganismo") or comprador.get("NombreUnidad") or "",
        "monto_disponible": None,
        "moneda": item.get("Moneda") or "CLP",
        "fecha_cierre": fechas.get("FechaCierre") or item.get("FechaCierre"),
        "descripcion": item.get("Descripcion") or "",
        "region": comprador.get("RegionUnidad") or "",
        "estado": item.get("Estado") or "Publicada",
        "raw_data": item,
    }

"""Cliente para el Actor de Apify `licify/mercadopublico-compraagil`.

Documentación del actor: https://apify.com/licify/mercadopublico-compraagil
"""

from typing import Any

import httpx

from config import get_settings

APIFY_ACTOR_ID = "mG8Eiq2gFtrM5JHdy"  # licify/mercadopublico-compraagil
APIFY_TIMEOUT_SECONDS = 120
MAX_RESULTADOS_POR_SYNC = 200


class ApifyError(Exception):
    """Error explícito al interactuar con Apify (red, auth, payload inválido)."""


def sincronizar_compras_agiles() -> list[dict[str, Any]]:
    """Ejecuta el Actor sincrónicamente y devuelve las Compras Ágiles Publicadas
    mapeadas al esquema de la tabla `oportunidades`.
    """
    settings = get_settings()
    if not settings.apify_api_token:
        raise ApifyError("APIFY_API_TOKEN no configurado en backend/.env")

    # `run-sync-get-dataset-items` corre el actor y devuelve los items en una
    # sola llamada — más simple que start + poll + fetch dataset.
    url = (
        f"https://api.apify.com/v2/acts/{APIFY_ACTOR_ID}"
        f"/run-sync-get-dataset-items"
    )
    headers = {"Authorization": f"Bearer {settings.apify_api_token}"}
    payload = {
        "action": "list-compraagil",
        "limit": MAX_RESULTADOS_POR_SYNC,
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=APIFY_TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException as exc:
        raise ApifyError(
            f"Timeout ({APIFY_TIMEOUT_SECONDS}s) ejecutando el Actor de Apify"
        ) from exc
    except httpx.HTTPError as exc:
        raise ApifyError(f"Error de red llamando a Apify: {exc}") from exc

    if response.status_code == 401:
        raise ApifyError("APIFY_API_TOKEN inválido o sin permisos sobre el Actor")
    if response.status_code >= 400:
        raise ApifyError(
            f"Apify respondió {response.status_code}: {response.text[:300]}"
        )

    try:
        items = response.json()
    except ValueError as exc:
        raise ApifyError("Apify devolvió una respuesta no JSON") from exc

    if not isinstance(items, list):
        raise ApifyError(
            f"Se esperaba una lista de items, vino {type(items).__name__}"
        )

    publicadas = [item for item in items if _estado(item) == "Publicada"]
    return [_mapear_oportunidad(item) for item in publicadas if _codigo(item)]


def _estado(item: dict) -> str:
    return (item.get("estado") or item.get("status") or "").strip()


def _codigo(item: dict) -> str:
    return (
        item.get("codigo")
        or item.get("id")
        or item.get("numero")
        or item.get("numeroAdquisicion")
        or ""
    )


def _mapear_oportunidad(item: dict) -> dict[str, Any]:
    return {
        "codigo": _codigo(item),
        "tipo": "compra_agil",
        "nombre": (
            item.get("nombre")
            or item.get("titulo")
            or item.get("name")
            or ""
        ),
        "organismo": (
            item.get("organismo")
            or item.get("comprador")
            or item.get("entidad")
            or ""
        ),
        "monto_disponible": (
            item.get("monto_disponible")
            or item.get("monto")
            or item.get("presupuesto")
            or item.get("montoDisponible")
        ),
        "moneda": item.get("moneda") or "CLP",
        "fecha_cierre": (
            item.get("fecha_cierre")
            or item.get("fechaCierre")
            or item.get("fechaPublicacion")
        ),
        "descripcion": (
            item.get("descripcion")
            or item.get("description")
            or ""
        ),
        "region": item.get("region") or "",
        "estado": "Publicada",
        "raw_data": item,
    }

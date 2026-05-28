"""Cliente para el Actor de Apify `licify/mercadopublico-compraagil`."""

import time
from typing import Any

import httpx

from config import get_settings

APIFY_ACTOR_ID = "mG8Eiq2gFtrM5JHdy"  # licify/mercadopublico-compraagil
MAX_RESULTADOS_POR_SYNC = 10
POLL_INTERVAL = 5   # segundos entre checks
MAX_WAIT = 300      # tiempo máximo de espera total


class ApifyError(Exception):
    pass


def sincronizar_compras_agiles() -> list[dict[str, Any]]:
    settings = get_settings()
    if not settings.apify_api_token:
        raise ApifyError("APIFY_API_TOKEN no configurado en backend/.env")

    headers = {"Authorization": f"Bearer {settings.apify_api_token}"}

    # 1. Iniciar el run
    run = _iniciar_run(headers)
    run_id = run["id"]
    dataset_id = run["defaultDatasetId"]

    # 2. Esperar a que termine
    _esperar_run(run_id, headers)

    # 3. Obtener los items del dataset
    items = _obtener_items(dataset_id, headers)

    publicadas = [item for item in items if _estado(item) == "Publicada"]
    return [_mapear_oportunidad(item) for item in publicadas if _codigo(item)]


def _iniciar_run(headers: dict) -> dict:
    url = f"https://api.apify.com/v2/acts/{APIFY_ACTOR_ID}/runs"
    payload = {
        "action": "list-compraagil",
        "limit": MAX_RESULTADOS_POR_SYNC,
    }
    try:
        r = httpx.post(url, json=payload, headers=headers, timeout=30)
    except httpx.HTTPError as exc:
        raise ApifyError(f"Error iniciando run de Apify: {exc}") from exc

    if r.status_code == 401:
        raise ApifyError("APIFY_API_TOKEN inválido o sin permisos")
    if r.status_code >= 400:
        raise ApifyError(f"Apify respondió {r.status_code}: {r.text[:300]}")

    data = r.json()
    return data.get("data", data)


def _esperar_run(run_id: str, headers: dict) -> None:
    url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    waited = 0
    while waited < MAX_WAIT:
        time.sleep(POLL_INTERVAL)
        waited += POLL_INTERVAL
        try:
            r = httpx.get(url, headers=headers, timeout=15)
            data = r.json().get("data", {})
            status = data.get("status", "")
        except Exception:
            continue

        if status in ("SUCCEEDED", "ABORTED"):
            return  # ABORTED puede tener resultados parciales válidos
        if status in ("FAILED", "TIMED-OUT"):
            raise ApifyError(f"El run de Apify terminó con estado: {status}")

    raise ApifyError(f"Timeout esperando el run de Apify ({MAX_WAIT}s)")


def _obtener_items(dataset_id: str, headers: dict) -> list[dict]:
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    try:
        r = httpx.get(url, headers=headers, params={"limit": MAX_RESULTADOS_POR_SYNC}, timeout=30)
    except httpx.HTTPError as exc:
        raise ApifyError(f"Error obteniendo items del dataset: {exc}") from exc

    if r.status_code >= 400:
        raise ApifyError(f"Error obteniendo dataset: {r.status_code}")

    items = r.json()
    if not isinstance(items, list):
        raise ApifyError(f"Se esperaba lista, vino {type(items).__name__}")
    return items


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
        "nombre": item.get("nombre") or item.get("titulo") or item.get("name") or "",
        "organismo": item.get("organismo") or item.get("comprador") or item.get("entidad") or "",
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
        "descripcion": item.get("descripcion") or item.get("description") or "",
        "region": item.get("region") or "",
        "estado": "Publicada",
        "raw_data": item,
    }

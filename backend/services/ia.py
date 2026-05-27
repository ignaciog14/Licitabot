"""Filtro de relevancia y generador de cotizaciones con Claude API."""

import json
import re
from typing import Any

from anthropic import Anthropic

from config import get_settings

MODELO = "claude-sonnet-4-20250514"
MAX_TOKENS_FILTRO = 1024
SCORE_UMBRAL_RELEVANTE = 50

PROMPT_FILTRO = """Eres un asistente especializado en compras públicas chilenas.

Empresa proveedora: Talinay (Industrial y Comercial Talinay Ltda.)
Rubros: artículos de librería, tintas, tampones, pinturas acrílicas y para tela,
materiales de manualidades, poliestireno/plumavit, fieltros, productos industriales
(silicones, aceites, emulsiones).

Analiza la siguiente Compra Ágil y determina si Talinay podría participar:

NOMBRE: {nombre}
DESCRIPCIÓN: {descripcion}
PRODUCTOS: {productos}
MONTO: {monto} CLP
REGIÓN: {region}
ORGANISMO: {organismo}

Responde SOLO con un objeto JSON (sin texto adicional, sin fences ```) en este formato exacto:
{{
  "score": <0-100>,
  "aplica": <true|false>,
  "categoria": "<librería|pinturas|manualidades|poliestireno|fieltro|industrial|ninguna>",
  "justificacion": "<máximo 2 oraciones explicando por qué aplica o no>",
  "productos_sugeridos": ["<producto Talinay 1>", "<producto Talinay 2>"]
}}

Score 0 = nada que ver con Talinay. Score 100 = perfecto match.
Umbral para notificar: score >= 50."""


RESULTADO_FALLBACK: dict[str, Any] = {
    "score": 0,
    "aplica": False,
    "categoria": "ninguna",
    "justificacion": "Error al analizar",
    "productos_sugeridos": [],
}


def analizar_relevancia(oportunidad: dict) -> dict:
    """Llama a Claude para obtener score + categoría + justificación.
    Nunca lanza: si algo falla, devuelve RESULTADO_FALLBACK.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        return {
            **RESULTADO_FALLBACK,
            "justificacion": "ANTHROPIC_API_KEY no configurado",
        }

    prompt = _armar_prompt(oportunidad)

    try:
        client = Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS_FILTRO,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = message.content[0].text if message.content else ""
    except Exception as exc:
        return {**RESULTADO_FALLBACK, "justificacion": f"Error Claude API: {exc}"}

    parsed = _parsear_json(texto)
    return parsed or RESULTADO_FALLBACK


def _armar_prompt(oportunidad: dict) -> str:
    raw = oportunidad.get("raw_data") or {}
    productos = (
        raw.get("productos")
        or raw.get("items")
        or raw.get("lineas")
        or "(no especificados en el listado)"
    )
    return PROMPT_FILTRO.format(
        nombre=oportunidad.get("nombre") or "(sin nombre)",
        descripcion=oportunidad.get("descripcion") or "(sin descripción)",
        productos=productos,
        monto=oportunidad.get("monto_disponible") or 0,
        region=oportunidad.get("region") or "(sin región)",
        organismo=oportunidad.get("organismo") or "(sin organismo)",
    )


def _parsear_json(texto: str) -> dict | None:
    """Extrae el primer objeto JSON del texto y normaliza sus campos."""
    if not texto:
        return None

    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    try:
        score = int(data.get("score", 0))
    except (TypeError, ValueError):
        score = 0
    score = max(0, min(100, score))

    return {
        "score": score,
        "aplica": bool(data.get("aplica", score >= SCORE_UMBRAL_RELEVANTE)),
        "categoria": data.get("categoria") or "ninguna",
        "justificacion": data.get("justificacion") or "",
        "productos_sugeridos": data.get("productos_sugeridos") or [],
    }

"""Scoring de oportunidades basado en palabras clave configuradas por el usuario."""

from __future__ import annotations

import unicodedata
from typing import Any


def normalizar(texto: str) -> str:
    """Lowercase + quitar tildes para comparación robusta."""
    return unicodedata.normalize("NFD", texto.lower()).encode("ascii", "ignore").decode()


def calcular_score(oportunidad: dict[str, Any], keywords: list[str]) -> dict:
    """Retorna score (0-100) y lista de keywords que matchearon."""
    if not keywords:
        return {"score": 0, "keywords_matched": []}

    texto = " ".join(filter(None, [
        oportunidad.get("nombre", ""),
        oportunidad.get("descripcion", ""),
        oportunidad.get("organismo", ""),
    ]))
    texto_norm = normalizar(texto)

    matched = [kw for kw in keywords if normalizar(kw) in texto_norm]

    # Score: cada match aporta puntos, cap en 100
    puntos_por_match = max(10, 100 // len(keywords))
    score = min(100, len(matched) * puntos_por_match)

    return {"score": score, "keywords_matched": matched}

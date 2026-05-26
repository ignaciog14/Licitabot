Implementa HU-07: filtro de relevancia con Claude API para analizar oportunidades de Mercado Público.

Lee el CLAUDE.md en la raíz antes de empezar — tiene el prompt exacto (`PROMPT_FILTRO`), las keywords de Talinay y el esquema de BD.

## Qué construir

### 1. Servicio IA (`backend/services/ia.py`)

Función `analizar_relevancia(oportunidad: dict) -> dict` que:
- Arma el prompt usando `PROMPT_FILTRO` del CLAUDE.md con los datos de la oportunidad
- Llama a Claude API con modelo `claude-sonnet-4-20250514`
- Parsea el JSON de respuesta
- Retorna dict con: `score`, `aplica`, `categoria`, `justificacion`, `productos_sugeridos`
- Si Claude no retorna JSON válido, retorna `{"score": 0, "aplica": false, "justificacion": "Error al analizar"}`

Usa el SDK oficial de Anthropic (`anthropic` ya está en requirements.txt).

### 2. Integración con sync

En `routers/sync.py`, después del upsert de cada oportunidad nueva:
- Llama a `analizar_relevancia()` para cada una
- Actualiza los campos `score_relevancia`, `justificacion_ia`, `categoria` en BD

### 3. Endpoint individual

`POST /oportunidades/{id}/analizar`:
- Re-analiza una oportunidad específica
- Actualiza BD con el nuevo score
- Retorna el resultado del análisis

## Umbral

`score >= 50` = oportunidad relevante para Talinay. Úsalo al consultar oportunidades para el dashboard.

## Al terminar

Crea el branch `feat/ia-filtro-relevancia`, haz commit con `feat: filtro de relevancia con Claude API`. Muestra un ejemplo de respuesta JSON del análisis.

Implementa HU-08 y HU-09: generación de cotizaciones con Claude API y endpoint de aprobación/edición.

Lee el CLAUDE.md en la raíz antes de empezar — tiene el prompt exacto (`PROMPT_COTIZACION`) y el esquema de las tablas `oportunidades` y `cotizaciones`.

## Qué construir

### 1. Generador en servicio IA (`backend/services/ia.py`)

Función `generar_cotizacion(oportunidad: dict) -> str` que:
- Arma el prompt usando `PROMPT_COTIZACION` del CLAUDE.md
- Llama a Claude API con modelo `claude-sonnet-4-20250514`
- Retorna el texto del borrador (string)

### 2. Endpoints en router (`backend/routers/oportunidades.py`)

**`POST /oportunidades/{id}/generar-cotizacion`**
- Verifica que `score_relevancia >= 50` (retorna 400 si no)
- Genera borrador via `generar_cotizacion()`
- Si ya existe cotización y no viene `?force=true`, retorna 409
- Crea registro en tabla `cotizaciones` con `estado = "borrador"` y `borrador_ia = texto`
- Retorna la cotización creada

**`GET /oportunidades/{id}/cotizacion`**
- Retorna la cotización activa de esa oportunidad (la más reciente)
- 404 si no existe

**`PATCH /cotizaciones/{id}`**
- Permite editar: `borrador_editado`, `precio_ofertado`, `plazo_entrega_dias`
- Si viene `{"estado": "aprobada"}`: cambia estado, no permite más ediciones (retorna 409 si ya estaba aprobada)
- Si viene `{"estado_oportunidad": "descartado"}`: actualiza `estado_interno` de la oportunidad relacionada

## Al terminar

Crea el branch `feat/ia-generador-cotizacion`, haz commit con `feat: generación y aprobación de cotizaciones con Claude API`. Muestra ejemplo curl para generar y aprobar.

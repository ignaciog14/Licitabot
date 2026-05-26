Implementa HU-04: integración con Apify para sincronizar Compras Ágiles de Mercado Público.

Lee el CLAUDE.md en la raíz antes de empezar — tiene la URL del Actor, las acciones disponibles y el esquema de BD donde se persisten los resultados.

## Qué construir

### 1. Servicio Apify (`backend/services/apify.py`)

Función `sincronizar_compras_agiles()` que:
- Llama al Actor `licify/mercadopublico-compraagil` via API de Apify con acción `list-compraagil`
- Filtra solo las que tienen `estado = "Publicada"`
- Retorna lista de dicts con los campos mapeados al esquema de `oportunidades`
- Timeout máximo de 120 segundos
- Si el Actor falla, lanza excepción descriptiva (no genérica)

Endpoint Apify: `https://api.apify.com/v2/acts/mG8Eiq2gFtrM5JHdy/runs`
Auth: header `Authorization: Bearer {APIFY_API_TOKEN}`

### 2. Router sync (`backend/routers/sync.py`)

`POST /sync/compras-agiles`:
- Llama a `sincronizar_compras_agiles()`
- Hace upsert en tabla `oportunidades` (clave de conflicto: `codigo`)
- Registra resultado en tabla `sync_log`
- Retorna `{"sincronizadas": N, "nuevas": M, "errores": []}`

### 3. Mapeo de campos

Mapea la respuesta de Apify al esquema de `oportunidades`:
- `codigo` ← identificador único de la Compra Ágil
- `nombre` ← título/nombre
- `organismo` ← entidad compradora
- `monto_disponible` ← presupuesto disponible
- `fecha_cierre` ← fecha límite para cotizar
- `descripcion` ← descripción completa
- `region` ← región del organismo
- `raw_data` ← respuesta completa sin modificar
- `tipo` ← siempre `"compra_agil"`
- `estado` ← siempre `"Publicada"` (ya filtrado)

## Al terminar

Crea el branch `feat/apify-sync`, haz commit con `feat: integración Apify para sync de Compras Ágiles`. Muestra un ejemplo de cómo probar el endpoint con curl.

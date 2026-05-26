Implementa HU-02: esquema de base de datos en Supabase y cliente de conexión para el proyecto Talinay.

Lee el CLAUDE.md en la raíz antes de empezar — tiene el esquema completo de las tablas con todos los campos.

## Qué construir

### 1. Migración SQL

Crea el archivo `docs/migrations/001_initial.sql` con:

- Tabla `oportunidades` (ver esquema en CLAUDE.md)
- Tabla `cotizaciones` (ver esquema en CLAUDE.md)
- Tabla `sync_log` (ver esquema en CLAUDE.md)
- Índices en: `oportunidades(estado_interno)`, `oportunidades(score_relevancia)`, `oportunidades(created_at)`, `oportunidades(codigo)`
- Row Level Security habilitado en las tres tablas (política permisiva para service role)
- Trigger `updated_at` en `oportunidades` y `cotizaciones`

### 2. Cliente en el backend

Actualiza `backend/database.py` para:
- Crear cliente Supabase usando `SUPABASE_URL` y `SUPABASE_SERVICE_KEY` del config
- Exponer una función `get_db()` que retorne el cliente

### 3. Verificación

Actualiza `GET /oportunidades` en `routers/oportunidades.py` para hacer una query real a Supabase y retornar la lista (vacía o con datos).

## Al terminar

Muestra el SQL completo listo para ejecutar en el editor SQL de Supabase. Crea el branch `feat/supabase-schema`, haz commit con mensaje `feat: esquema BD Supabase y cliente de conexión`.

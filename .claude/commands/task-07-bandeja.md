Implementa HU-10, HU-11 y HU-12: bandeja de oportunidades con filtros y botón de sync manual.

Lee el CLAUDE.md en la raíz antes de empezar — tiene el stack frontend y el esquema de datos de `oportunidades`.

## Qué construir

### Página Bandeja (`src/pages/Bandeja.jsx`)

Lista de oportunidades que muestra solo las que tienen `score_relevancia >= 50`, ordenadas por score descendente.

**Cada fila muestra:**
- Badge de score con color: verde (≥80), amarillo (50–79)
- Nombre de la oportunidad
- Organismo
- Monto en CLP formateado como `$1.250.000`
- Tiempo relativo al cierre: `"Cierra hoy"`, `"Cierra en 2 días"`, `"Cerrada"`
- Estado interno como badge: Pendiente / Cotizado / Descartado / Ganado
- Al hacer clic navega a `/oportunidad/:id`

**Filtros (en tiempo real, sin reload):**
- Por estado interno: Todos / Pendiente / Cotizado / Ganado / Descartado
- Por score mínimo: 50+ / 70+ / 90+
- Por tipo: Todos / Compra Ágil / Licitación
- Búsqueda por texto libre (nombre u organismo)
- Los filtros activos deben reflejarse en la URL como query params

**Botón "Sincronizar ahora":**
- Llama a `POST /sync/compras-agiles`
- Durante la llamada: spinner + texto "Buscando nuevas oportunidades..."
- Al terminar: toast con "Se encontraron N nuevas oportunidades" o "Sin novedades"
- Si hay error: mensaje descriptivo
- Deshabilitar el botón durante la sincronización
- Mostrar "Última sync: hace X minutos" debajo del botón

**Paginación:** 20 oportunidades por página.

### Componentes a crear

- `src/components/OpportunityRow.jsx` — fila individual de la lista
- `src/components/ScoreBadge.jsx` — badge verde/amarillo con el score
- `src/components/StatusBadge.jsx` — badge para estado interno
- `src/components/FilterBar.jsx` — barra de filtros

## Al terminar

Crea el branch `feat/dashboard-bandeja`, haz commit con `feat: bandeja de oportunidades con filtros y sync manual`.

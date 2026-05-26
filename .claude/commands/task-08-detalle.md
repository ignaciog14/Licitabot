Implementa HU-13 y HU-14: vista detalle de oportunidad con editor de cotización integrado.

Lee el CLAUDE.md en la raíz antes de empezar — tiene el stack, el esquema de `oportunidades` y `cotizaciones`, y el flujo del sistema.

## Qué construir

### Página Detalle (`src/pages/Detalle.jsx`)

Vista completa de una oportunidad en `/oportunidad/:id`.

**Sección de información de la oportunidad:**
- Nombre, organismo, unidad compradora
- Descripción completa
- Productos requeridos
- Monto disponible (formateado en CLP)
- Región y dirección de entrega
- Score de relevancia + justificación de la IA (en tarjeta destacada)
- Countdown al cierre: `"Cierra en 1 día, 4 horas"` (actualización en tiempo real)
- Link externo a mercadopublico.cl (abre en nueva pestaña)
- Breadcrumb: `Bandeja > [nombre de la oportunidad]`
- Botón "← Volver" que regresa a la bandeja con los filtros previos (usar `navigate(-1)`)

**Sección del editor de cotización:**

*Si no hay cotización:*
- Botón "Generar cotización con IA" prominente
- Durante la generación: spinner + "La IA está preparando tu cotización..."

*Si hay cotización en borrador:*
- `<textarea>` editable con el texto del borrador
- Campo numérico "Precio ofertado (CLP)"
- Campo numérico "Plazo de entrega (días hábiles)"
- Botón "Guardar cambios"
- Botón "Regenerar" (pide confirmación antes de sobreescribir)
- Botón "Aprobar cotización" (pide confirmación, luego bloquea edición)
- Botón "Descartar oportunidad" (pide confirmación)

*Si la cotización está aprobada:*
- Texto no editable (modo lectura)
- Indicador visual "Cotización aprobada"
- Botón "Descargar PDF" (si hay `pdf_url`) o "Generando PDF..." (si no)

**Estado visible del flujo:** `Borrador → Aprobada → PDF listo`

### Componentes a crear

- `src/components/CountdownTimer.jsx` — countdown en tiempo real
- `src/components/CotizacionEditor.jsx` — editor completo con todos los estados

## Al terminar

Crea el branch `feat/detalle-oportunidad`, haz commit con `feat: vista detalle con editor de cotización`.

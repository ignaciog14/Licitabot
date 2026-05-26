Implementa HU-15: generación de PDF profesional para cotizaciones aprobadas.

Lee el CLAUDE.md en la raíz antes de empezar — tiene el esquema de `cotizaciones` y la info de Talinay (dirección, razón social, rubros).

## Qué construir

### 1. Endpoint de generación (`backend/routers/oportunidades.py`)

`GET /cotizaciones/{id}/pdf`:
- Verifica que la cotización tenga `estado = "aprobada"` (retorna 400 si no)
- Genera el PDF
- Lo sube a Supabase Storage en bucket `cotizaciones`
- Guarda la URL en `cotizaciones.pdf_url`
- Retorna el PDF como descarga directa (`Content-Disposition: attachment`)
- Nombre del archivo: `cotizacion-{codigo_oportunidad}-talinay.pdf`

### 2. Contenido del PDF

El PDF debe tener este layout:

**Encabezado:**
- Razón social: Industrial y Comercial Talinay Ltda.
- Dirección: Iquique 3423, Estación Central, Santiago
- Web: talinay.cl

**Cuerpo:**
- Referencia de la Compra Ágil (código y nombre)
- Organismo destinatario
- Tabla de productos ofrecidos (del `borrador_editado` o `borrador_ia`)
- Precio total ofertado (formateado en CLP)
- Plazo de entrega en días hábiles
- Condiciones de despacho

**Pie:**
- "Cotización válida por 5 días hábiles"
- Fecha de generación

**Librería recomendada:** `reportlab` o `weasyprint`. Agrega la que elijas a `requirements.txt`.

### 3. Botón en frontend

En `src/components/CotizacionEditor.jsx`:
- Si `cotizacion.pdf_url` existe: botón "Descargar PDF" que abre la URL
- Si no existe y cotización está aprobada: botón "Generar PDF" que llama al endpoint y recarga
- Durante la generación: estado "Generando PDF..."

## Al terminar

Crea el branch `feat/pdf-cotizacion`, haz commit con `feat: generación de PDF de cotización con subida a Supabase Storage`.

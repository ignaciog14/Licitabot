# Backlog — Talinay Compras Públicas

Sistema semi-automático de detección y postulación a Compras Ágiles y licitaciones de Mercado Público para Industrial y Comercial Talinay Ltda.

---

## Contexto del producto

**Problema:** Talinay es una fábrica con 35+ años de historia que pierde oportunidades de venta al Estado porque nadie tiene tiempo de revisar el portal todos los días.

**Solución:** Un dashboard que monitorea automáticamente Mercado Público, filtra con IA las oportunidades relevantes para el rubro de Talinay, y genera borradores de cotización listos para aprobar. El humano solo revisa, edita si quiere, y sube el PDF al portal.

**Usuarios:** Equipo de Talinay (1–3 personas). Futuro: otras PYMEs chilenas (SaaS).

---

## Épicas

| ID | Épica | Descripción |
|----|-------|-------------|
| E1 | Infraestructura base | Repo, BD, backend y frontend inicializados |
| E2 | Ingesta de datos | Traer Compras Ágiles y licitaciones desde las APIs |
| E3 | Motor de IA | Filtro de relevancia y generación de cotizaciones |
| E4 | Dashboard — bandeja | Vista principal de oportunidades del día |
| E5 | Dashboard — detalle | Vista individual con editor de cotización |
| E6 | Documentos | Generación y descarga de PDF de cotización |
| E7 | Calidad y deploy | Tests, CI/CD y despliegue a producción |

---

## Historias de usuario

---

### E1 · Infraestructura base

---

#### HU-01 · Estructura base del backend

**Como** desarrollador,
**quiero** tener el proyecto FastAPI inicializado con la estructura de carpetas correcta,
**para que** pueda empezar a implementar los servicios sin decisiones de arquitectura pendientes.

**Criterios de aceptación:**
- `uvicorn main:app --reload` levanta sin errores desde `/backend`
- `GET /health` retorna `{"status": "ok", "version": "0.1.0"}`
- `GET /docs` muestra Swagger con los routers registrados
- Existe `/backend/services/` con `apify.py`, `mercado_publico.py`, `ia.py`
- Existe `/backend/routers/` con `oportunidades.py`, `sync.py`
- `config.py` lee todas las variables de entorno via pydantic-settings
- CORS configurado para `localhost:5173` y dominio de producción

**Stack:** FastAPI, uvicorn, pydantic-settings, python-dotenv

**Comando Claude Code:** `/task-01-backend`

**Branch:** `feat/backend-base`

---

#### HU-02 · Base de datos en Supabase

**Como** desarrollador,
**quiero** tener el esquema de la BD creado en Supabase con las tablas necesarias,
**para que** el backend pueda persistir oportunidades y cotizaciones.

**Criterios de aceptación:**
- Existe migración SQL en `docs/migrations/001_initial.sql`
- Tablas creadas: `oportunidades`, `cotizaciones`, `sync_log`
- Índices creados para las columnas más consultadas (`estado_interno`, `score_relevancia`, `created_at`)
- Row Level Security habilitado en las tres tablas
- El cliente Supabase en `backend/database.py` conecta sin errores
- `GET /oportunidades` retorna `[]` (vacío pero sin error) desde la BD real

**Comando Claude Code:** `/task-02-supabase`

**Branch:** `feat/supabase-schema`

---

#### HU-03 · Estructura base del frontend

**Como** desarrollador,
**quiero** tener React + Vite + TailwindCSS inicializado con el routing y el cliente HTTP configurados,
**para que** pueda construir las pantallas sin configuración pendiente.

**Criterios de aceptación:**
- `npm run dev` levanta en `localhost:5173` sin errores ni warnings
- React Router configurado con rutas: `/` (Bandeja) y `/oportunidad/:id` (Detalle)
- React Query inicializado en `main.jsx`
- Cliente axios en `src/lib/api.js` apuntando a `VITE_API_URL`
- Layout con navbar visible que muestra "Talinay Compras"
- TailwindCSS funcionando (clases aplicadas correctamente)

**Comando Claude Code:** `/task-06-frontend`

**Branch:** `feat/frontend-base`

---

### E2 · Ingesta de datos

---

#### HU-04 · Sincronización de Compras Ágiles

**Como** usuario de Talinay,
**quiero** que el sistema traiga automáticamente las Compras Ágiles publicadas en Mercado Público,
**para** no tener que revisarlas manualmente en el portal.

**Criterios de aceptación:**
- `POST /sync/compras-agiles` ejecuta el Actor de Apify y retorna resultado
- Se traen todas las Compras Ágiles con estado `Publicada` (hasta 200 por sync)
- Cada resultado se persiste en la tabla `oportunidades` con upsert (clave: `codigo`)
- El resultado de la sync se registra en `sync_log`
- La respuesta incluye `{"sincronizadas": N, "nuevas": M, "errores": []}`
- Timeout máximo de 120 segundos por llamada a Apify
- Si el Actor falla, retorna error descriptivo (no 500 genérico)

**APIs:** Apify Actor `licify/mercadopublico-compraagil`

**Comando Claude Code:** `/task-03-apify`

**Branch:** `feat/apify-sync`

---

#### HU-05 · Sincronización de licitaciones tradicionales

**Como** usuario de Talinay,
**quiero** que el sistema también traiga licitaciones L1 de la API oficial de Mercado Público,
**para** no perder oportunidades de mayor monto.

**Criterios de aceptación:**
- `POST /sync/licitaciones` trae licitaciones del día actual via API oficial MP
- Se filtran por las mismas categorías de rubros de Talinay
- Se persisten en `oportunidades` con `tipo = 'licitacion'`
- Se registra en `sync_log`
- Maneja paginación si hay más de 100 resultados

**APIs:** API oficial Mercado Público (`api.mercadopublico.cl`)

**Branch:** `feat/mp-licitaciones-sync`

**Nota:** Implementar después de HU-04 (misma estructura de BD).

---

#### HU-06 · Sync automático periódico

**Como** usuario de Talinay,
**quiero** que el sistema sincronice automáticamente sin que yo tenga que hacer nada,
**para** no depender de recordar ejecutarlo manualmente.

**Criterios de aceptación:**
- El backend ejecuta sync de Compras Ágiles automáticamente cada 6 horas
- El scheduler corre al levantar el servidor y también en intervalos fijos
- Se puede configurar el intervalo via variable de entorno `SYNC_INTERVAL_HOURS`
- Los errores de sync no tumban el servidor (se loguean y continúan)

**Implementación:** APScheduler o BackgroundTasks de FastAPI

**Branch:** `feat/sync-scheduler`

**Nota:** Implementar después de HU-04.

---

### E3 · Motor de IA

---

#### HU-07 · Filtro de relevancia con IA

**Como** usuario de Talinay,
**quiero** que la IA analice cada Compra Ágil y le asigne un score de relevancia,
**para** ver solo las oportunidades que realmente aplican al rubro de Talinay.

**Criterios de aceptación:**
- Cada oportunidad sincronizada recibe un score de 0 a 100
- El score se calcula con Claude API usando el prompt definido en CLAUDE.md
- Se persisten en BD: `score_relevancia`, `justificacion_ia`, `categoria`
- Solo se muestran al usuario oportunidades con `score >= 50`
- El análisis incluye productos sugeridos de Talinay para esa oportunidad
- `POST /oportunidades/{id}/analizar` permite re-analizar una oportunidad individual
- El análisis se ejecuta automáticamente después de cada sync

**APIs:** Claude API (`claude-sonnet-4-20250514`)

**Comando Claude Code:** `/task-04-filtro-ia`

**Branch:** `feat/ia-filtro-relevancia`

---

#### HU-08 · Generación de borrador de cotización

**Como** usuario de Talinay,
**quiero** que la IA genere un borrador de cotización para cada oportunidad relevante,
**para** no tener que redactarla desde cero cada vez.

**Criterios de aceptación:**
- `POST /oportunidades/{id}/generar-cotizacion` genera un borrador via Claude API
- El borrador incluye: descripción de productos Talinay, precio estimado, plazo de entrega, condiciones
- El borrador se guarda en tabla `cotizaciones` con `estado = 'borrador'`
- Solo se puede generar si `score_relevancia >= 50`
- `GET /oportunidades/{id}/cotizacion` retorna la cotización activa
- Si ya existe una cotización, la sobreescribe solo si se pasa `force=true`

**APIs:** Claude API (`claude-sonnet-4-20250514`)

**Comando Claude Code:** `/task-05-cotizacion-ia`

**Branch:** `feat/ia-generador-cotizacion`

---

#### HU-09 · Edición y aprobación de cotización

**Como** usuario de Talinay,
**quiero** poder editar el borrador generado por la IA antes de aprobarlo,
**para** ajustar precios y condiciones según lo que realmente puedo ofrecer.

**Criterios de aceptación:**
- `PATCH /cotizaciones/{id}` permite editar: `borrador_editado`, `precio_ofertado`, `plazo_entrega_dias`
- `PATCH /cotizaciones/{id}` con `{"aprobar": true}` cambia estado a `aprobada`
- Una cotización aprobada no puede editarse (retorna 409 si se intenta)
- `PATCH /cotizaciones/{id}` con `{"descartar_oportunidad": true}` cambia estado de la oportunidad a `descartado`

**Branch:** `feat/cotizacion-aprobacion`

**Nota:** Implementar junto con HU-08.

---

### E4 · Dashboard — bandeja

---

#### HU-10 · Vista principal de oportunidades

**Como** usuario de Talinay,
**quiero** ver todas las oportunidades relevantes del día en una lista clara,
**para** saber rápidamente qué oportunidades tengo que revisar hoy.

**Criterios de aceptación:**
- La bandeja muestra oportunidades con `score >= 50` ordenadas por score descendente
- Cada fila muestra: score (badge de color), nombre, organismo, monto en CLP, fecha de cierre, estado interno
- Los colores del score son: verde (≥80), amarillo (50–79)
- El monto se formatea como "$1.250.000" (pesos chilenos)
- La fecha de cierre muestra tiempo relativo: "cierra en 2 días", "cierra hoy"
- Hacer clic en una fila navega al detalle de esa oportunidad
- La lista tiene paginación o infinite scroll (máximo 20 por página)

**Comando Claude Code:** `/task-07-bandeja`

**Branch:** `feat/dashboard-bandeja`

---

#### HU-11 · Filtros en la bandeja

**Como** usuario de Talinay,
**quiero** filtrar las oportunidades por estado y score,
**para** enfocarme en las que más me interesan.

**Criterios de aceptación:**
- Filtro por estado interno: Todos / Pendiente / Cotizado / Ganado / Descartado
- Filtro por score mínimo: 50+ / 70+ / 90+
- Filtro por tipo: Compra Ágil / Licitación / Todos
- Búsqueda por texto libre en nombre y organismo
- Los filtros se aplican en tiempo real (sin reload)
- Los filtros se mantienen al volver desde el detalle (query params en la URL)

**Branch:** `feat/dashboard-filtros`

**Nota:** Implementar junto con HU-10.

---

#### HU-12 · Sincronización manual desde el dashboard

**Como** usuario de Talinay,
**quiero** poder ejecutar una sincronización manual desde el dashboard,
**para** ver las oportunidades más recientes sin esperar el sync automático.

**Criterios de aceptación:**
- Botón "Sincronizar ahora" visible en la bandeja
- Al hacer clic muestra spinner con texto "Buscando nuevas oportunidades..."
- Al terminar muestra toast: "Se encontraron N nuevas oportunidades" o "Sin novedades"
- Si hay error muestra mensaje descriptivo (no solo "Error")
- El botón se deshabilita durante la sincronización para evitar doble click
- Muestra la hora del último sync exitoso

**Branch:** `feat/sync-manual`

---

### E5 · Dashboard — detalle

---

#### HU-13 · Vista detalle de una oportunidad

**Como** usuario de Talinay,
**quiero** ver todos los detalles de una Compra Ágil en una pantalla dedicada,
**para** entender exactamente qué pide el organismo antes de cotizar.

**Criterios de aceptación:**
- Muestra: nombre, organismo, unidad, descripción completa, productos requeridos, monto, región, dirección de entrega
- Muestra el score de relevancia y la justificación de la IA
- Muestra un countdown hasta la fecha de cierre ("Cierra en 1 día, 4 horas")
- Incluye link externo a la Compra Ágil en mercadopublico.cl (abre en nueva pestaña)
- Breadcrumb de navegación: Bandeja > [nombre de la oportunidad]
- Botón "← Volver" regresa a la bandeja con los filtros previos

**Comando Claude Code:** `/task-08-detalle`

**Branch:** `feat/detalle-oportunidad`

---

#### HU-14 · Editor de cotización en el detalle

**Como** usuario de Talinay,
**quiero** ver el borrador de cotización generado por la IA y poder editarlo antes de aprobar,
**para** personalizar la propuesta según los precios reales que manejo.

**Criterios de aceptación:**
- Si no hay cotización: botón "Generar cotización con IA" prominente
- Durante la generación: spinner con texto "La IA está preparando tu cotización..."
- Si hay cotización en borrador: textarea editable con el texto, campo de precio (CLP), campo de plazo (días)
- Botón "Aprobar cotización" que bloquea la edición y habilita descarga de PDF
- Botón "Regenerar" que sobreescribe el borrador con uno nuevo de la IA
- Botón "Descartar oportunidad" que marca la oportunidad y la saca de la bandeja
- Estado de la cotización visible: Borrador → Aprobada → PDF listo

**Branch:** `feat/editor-cotizacion`

**Nota:** Implementar junto con HU-13.

---

### E6 · Documentos

---

#### HU-15 · Generación de PDF de cotización

**Como** usuario de Talinay,
**quiero** descargar un PDF profesional de mi cotización aprobada,
**para** subirlo directamente al portal de Mercado Público.

**Criterios de aceptación:**
- `GET /cotizaciones/{id}/pdf` genera el PDF y lo retorna como descarga directa
- El PDF incluye: logo/encabezado de Talinay, datos del organismo, referencia de la Compra Ágil, tabla de productos, precio total, plazo, condiciones, pie con validez
- El PDF se sube a Supabase Storage y se guarda la URL en BD
- El nombre del archivo es `cotizacion-[codigo]-talinay.pdf`
- Solo se puede generar PDF de cotizaciones con estado `aprobada`
- En el frontend, el botón "Descargar PDF" dispara la descarga automáticamente

**Comando Claude Code:** `/task-09-pdf`

**Branch:** `feat/pdf-cotizacion`

---

#### HU-16 · Historial de cotizaciones

**Como** usuario de Talinay,
**quiero** ver un historial de todas las cotizaciones que he enviado,
**para** hacer seguimiento de qué gané, qué perdí y cuánto he cotizado en total.

**Criterios de aceptación:**
- Página `/historial` accesible desde el navbar
- Lista de todas las oportunidades con estado `cotizado`, `ganado` o `perdido`
- Permite marcar una oportunidad como `ganado` o `perdido` manualmente
- Muestra KPIs básicos en la parte superior: total cotizado (CLP), tasa de adjudicación, oportunidades ganadas

**Branch:** `feat/historial`

---

### E7 · Calidad y deploy

---

#### HU-17 · Variables de entorno y configuración de producción

**Como** desarrollador,
**quiero** tener la configuración de producción lista antes del deploy,
**para** que el sistema funcione correctamente en Vercel y Railway desde el primer día.

**Criterios de aceptación:**
- `frontend/.env.example` y `backend/.env.example` documentados y actualizados
- Variables de producción configuradas en Vercel (frontend) y Railway (backend)
- CORS del backend actualizado con el dominio de producción de Vercel
- Supabase con URL de producción configurada
- `.gitignore` correctamente configurado (ningún `.env` commiteado)

**Branch:** `chore/prod-config`

---

#### HU-18 · Deploy frontend en Vercel

**Como** desarrollador,
**quiero** que el frontend esté desplegado en Vercel,
**para** que el equipo de Talinay pueda usarlo desde el navegador sin instalar nada.

**Criterios de aceptación:**
- Frontend deployado en Vercel y accesible via URL pública
- Deploy automático al hacer push a `main`
- Preview deploy automático en cada Pull Request
- Variables de entorno configuradas en Vercel dashboard

**Branch:** `chore/deploy-vercel`

---

#### HU-19 · Deploy backend en Railway

**Como** desarrollador,
**quiero** que el backend FastAPI esté desplegado en Railway,
**para** que el frontend de producción pueda conectarse a la API.

**Criterios de aceptación:**
- Backend deployado en Railway y accesible via URL pública
- `GET /health` retorna 200 en producción
- Deploy automático al hacer push a `main`
- Variables de entorno configuradas en Railway dashboard
- Logs accesibles desde Railway para debugging

**Branch:** `chore/deploy-railway`

---

## Orden de implementación (sprints sugeridos)

### Sprint 1 — Base (días 1–3)
| HU | Título | Responsable |
|----|--------|-------------|
| HU-01 | Backend base FastAPI | Ignacio |
| HU-02 | Base de datos Supabase | Ignacio |
| HU-03 | Frontend base React | Hermano |

### Sprint 2 — Datos e IA (días 4–7)
| HU | Título | Responsable |
|----|--------|-------------|
| HU-04 | Sync Compras Ágiles (Apify) | Hermano |
| HU-07 | Filtro de relevancia IA | Ignacio |
| HU-08 | Generación de cotización IA | Ignacio |
| HU-09 | Edición y aprobación | Hermano |

### Sprint 3 — Dashboard (días 8–11)
| HU | Título | Responsable |
|----|--------|-------------|
| HU-10 | Bandeja de oportunidades | Hermano |
| HU-11 | Filtros en la bandeja | Hermano |
| HU-12 | Sync manual desde UI | Cualquiera |
| HU-13 | Vista detalle | Ignacio |
| HU-14 | Editor de cotización | Ignacio |

### Sprint 4 — Cierre (días 12–14)
| HU | Título | Responsable |
|----|--------|-------------|
| HU-15 | PDF de cotización | Cualquiera |
| HU-16 | Historial | Cualquiera |
| HU-17 | Config producción | Ignacio |
| HU-18 | Deploy Vercel | Ignacio |
| HU-19 | Deploy Railway | Ignacio |

### Backlog futuro (post-MVP)
| HU | Título |
|----|--------|
| HU-05 | Sync licitaciones tradicionales |
| HU-06 | Sync automático periódico |
| — | Multi-tenant (otras PYMEs) |
| — | Notificaciones WhatsApp/email |
| — | Análisis de competencia (quién más cotizó) |
| — | Historial de precios por rubro |

---

## Convención de branches y commits

```
feat/hu-XX-descripcion-corta   ← nueva funcionalidad
fix/hu-XX-descripcion-corta    ← corrección de bug
chore/descripcion-corta        ← configuración, deps, infra
docs/descripcion-corta         ← documentación
```

Commits en español:
```
feat: agregar filtro de relevancia con Claude API
fix: corregir timeout en llamada a Apify
chore: configurar variables de entorno producción
```

Flujo de trabajo:
1. Crear branch desde `main`
2. Desarrollar con Claude Code usando el slash command correspondiente
3. Hacer commit al terminar
4. Abrir Pull Request hacia `main`
5. El otro revisa y mergea

---

## Custom slash commands disponibles

Ejecutar en Claude Code desde la raíz del repo:

| Comando | HU | Descripción |
|---------|----|-------------|
| `/task-01-backend` | HU-01 | Backend base FastAPI |
| `/task-02-supabase` | HU-02 | Supabase schema y cliente |
| `/task-03-apify` | HU-04 | Integración Apify |
| `/task-04-filtro-ia` | HU-07 | Filtro de relevancia IA |
| `/task-05-cotizacion-ia` | HU-08/09 | Generador y aprobación cotización |
| `/task-06-frontend` | HU-03 | Frontend base |
| `/task-07-bandeja` | HU-10/11/12 | Bandeja y filtros |
| `/task-08-detalle` | HU-13/14 | Detalle y editor |
| `/task-09-pdf` | HU-15 | Generación PDF |


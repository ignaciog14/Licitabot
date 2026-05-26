# CLAUDE.md — Talinay Compras Públicas

Contexto persistente para Claude Code. Leer antes de cualquier tarea.

---

## Qué es este proyecto

Sistema semi-automático de detección y postulación a **Compras Ágiles** y licitaciones de Mercado Público, desarrollado para **Industrial y Comercial Talinay Ltda.** (talinay.cl).

El problema: Talinay es una fábrica con 35+ años de historia que pierde oportunidades de venta al Estado simplemente porque nadie tiene tiempo de revisar el portal todos los días. Este sistema automatiza el monitoreo, el análisis de relevancia con IA, y la generación de cotizaciones. El humano solo aprueba y sube la cotización final.

Objetivo futuro: monetizar como SaaS para otras PYMEs chilenas.

---

## Empresa cliente — Talinay

- **Razón social**: Industrial y Comercial Talinay Ltda.
- **Dirección**: Iquique 3423, Estación Central, Santiago
- **Web**: https://talinay.cl
- **Rubros / productos**:
  - Artículos de librería (tintas, tampones, sellos, artículos de oficina)
  - Pinturas (acrílicas, temperas, pinturas para género/tela)
  - Manualidades (materiales creativos, escolares)
  - Poliestireno / Plumavit (planchas, cortes a medida)
  - Fieltros (mantas, discos de pulir, productos dimensionados)
  - Industrial (silicones, aceites, emulsiones, pastas)
- **Clientes objetivo en MP**: colegios, municipalidades, hospitales, organismos públicos

---

## Flujo del sistema

```
[Apify Actor]          [API MP oficial]       [Perfil Talinay]
Compras Ágiles    +    Licitaciones L1    +   rubros/precios
      └────────────────────┬────────────────────┘
                           ↓
              [Filtro de relevancia — Claude API]
              ¿aplica al rubro de Talinay? score 0-100
                           ↓ (si score > umbral)
              [Generador de cotización — Claude API]
              borrador editable con productos Talinay
                           ↓
              [Dashboard web — React + Supabase]
              Bandeja → Vista detalle → Aprobar/Editar
                           ↓ (acción humana)
              [PDF descargable → subir a mercadopublico.cl]
```

---

## Stack técnico

### Frontend
- React + Vite + TailwindCSS
- React Router para navegación
- React Query para fetching/cache
- Carpeta: `/frontend`

### Backend
- Python (FastAPI) o Node.js — TBD según preferencia del equipo
- Carpeta: `/backend`

### Base de datos
- **Supabase** (PostgreSQL + Auth + Storage)
- Auth para el usuario admin de Talinay

### APIs externas
- **Apify Actor** `licify/mercadopublico-compraagil` — scraper de Compras Ágiles
  - Endpoint: `https://api.apify.com/v2/acts/mG8Eiq2gFtrM5JHdy/runs`
  - Costo: ~$0.10 / 1,000 resultados
  - Acciones: `list-compraagil`, `get-compraagil`, `list-files`
  - Status relevante: `Publicada` (abiertas para cotizar)
- **API oficial Mercado Público** — licitaciones tradicionales
  - Base URL: `https://api.mercadopublico.cl/servicios/v1/`
  - Auth: ticket en query param `?ticket=TU_TICKET`
  - Ticket de prueba: `F8537A18-6766-4DEF-9E59-426B4FEE2844`
- **Claude API** (Anthropic) — motor de IA
  - Modelo: `claude-sonnet-4-20250514`
  - Uso: filtro de relevancia + generación de cotizaciones
- **Supabase** — BD y auth

### Infraestructura
- Frontend: Vercel
- Backend: Railway o Render
- Variables de entorno: nunca hardcodeadas, siempre en `.env`

---

## Esquema de base de datos (Supabase)

### `oportunidades`
```sql
id uuid primary key default gen_random_uuid()
codigo text unique not null          -- ej: "3888-244-COT26"
tipo text not null                   -- 'compra_agil' | 'licitacion'
nombre text not null
organismo text not null
monto_disponible numeric
moneda text default 'CLP'
fecha_cierre timestamptz
estado text                          -- 'Publicada' | 'Cerrada' | 'Adjudicada'
descripcion text
region text
raw_data jsonb                       -- respuesta completa de la API
score_relevancia integer             -- 0-100, calculado por IA
justificacion_ia text                -- por qué la IA lo consideró relevante
estado_interno text default 'pendiente'  -- 'pendiente'|'cotizado'|'descartado'|'ganado'|'perdido'
created_at timestamptz default now()
updated_at timestamptz default now()
```

### `cotizaciones`
```sql
id uuid primary key default gen_random_uuid()
oportunidad_id uuid references oportunidades(id)
borrador_ia text                     -- texto generado por Claude
borrador_editado text                -- versión final aprobada por usuario
precio_ofertado numeric
plazo_entrega_dias integer
estado text default 'borrador'       -- 'borrador'|'aprobada'|'enviada'
pdf_url text                         -- URL en Supabase Storage
created_at timestamptz default now()
updated_at timestamptz default now()
```

### `sync_log`
```sql
id uuid primary key default gen_random_uuid()
tipo text                            -- 'compras_agiles' | 'licitaciones'
oportunidades_encontradas integer
oportunidades_nuevas integer
errores jsonb
created_at timestamptz default now()
```

---

## Palabras clave para el filtro de relevancia

La IA debe comparar el texto de cada oportunidad contra estos términos:

```python
KEYWORDS_TALINAY = [
    # Librería / oficina
    "librería", "artículos de oficina", "insumos escolares", "papelería",
    "tinta", "tampón", "sello", "plumón", "lápiz", "cuaderno",
    # Pinturas
    "pintura", "acrílica", "tempera", "pintura tela", "pintura género",
    "brocha", "rodillo", "barniz",
    # Manualidades / educación
    "manualidades", "materiales didácticos", "arte", "creatividad",
    "materiales escolares", "útiles escolares",
    # Poliestireno
    "poliestireno", "plumavit", "foam", "espuma", "plancha",
    "corte a medida", "aislante",
    # Fieltro
    "fieltro", "disco de pulir", "paño industrial",
    # Industrial
    "silicona", "aceite industrial", "emulsión", "pasta industrial",
    "lubricante", "sellador",
]
```

---

## Prompt base para filtro de relevancia

```python
PROMPT_FILTRO = """
Eres un asistente especializado en compras públicas chilenas.

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

Responde en JSON con este formato exacto:
{{
  "score": <0-100>,
  "aplica": <true|false>,
  "categoria": "<librería|pinturas|manualidades|poliestireno|fieltro|industrial|ninguna>",
  "justificacion": "<máximo 2 oraciones explicando por qué aplica o no>",
  "productos_sugeridos": ["<producto Talinay 1>", "<producto Talinay 2>"]
}}

Score 0 = nada que ver con Talinay. Score 100 = perfecto match.
Umbral para notificar: score >= 50.
"""
```

---

## Prompt base para generación de cotización

```python
PROMPT_COTIZACION = """
Eres un asistente que ayuda a Talinay a preparar cotizaciones para Mercado Público.

Talinay es fabricante chileno con 35+ años de experiencia en:
tintas, tampones, pinturas, manualidades, poliestireno, fieltros y productos industriales.

Genera un borrador de cotización formal para la siguiente Compra Ágil:

NOMBRE: {nombre}
DESCRIPCIÓN: {descripcion}
PRODUCTOS REQUERIDOS: {productos}
MONTO DISPONIBLE: {monto} CLP
PLAZO CIERRE: {fecha_cierre}
ORGANISMO: {organismo}

El borrador debe incluir:
1. Descripción de los productos que Talinay ofrecería
2. Precio estimado (conservador, dentro del monto disponible)
3. Plazo de entrega sugerido (en días hábiles)
4. Condiciones de despacho
5. Texto profesional listo para copiar en el portal

Sé directo y profesional. El usuario editará los precios exactos antes de enviar.
"""
```

---

## Convenciones de código

- Commits en español, formato: `tipo: descripción corta`
  - Tipos: `feat`, `fix`, `refactor`, `docs`, `chore`
  - Ejemplo: `feat: agregar filtro de relevancia con Claude API`
- Variables de entorno siempre en `.env`, nunca hardcodeadas
- Componentes React en PascalCase, archivos en kebab-case
- Funciones utilitarias en `/frontend/src/lib/` o `/backend/utils/`
- Toda lógica de IA en `/backend/services/ia.py` (o `.js`)
- Toda lógica de Apify en `/backend/services/apify.py`
- Toda lógica de MP oficial en `/backend/services/mercado_publico.py`

---

## Variables de entorno requeridas

### Frontend (`/frontend/.env`)
```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_URL=http://localhost:8000
```

### Backend (`/backend/.env`)
```
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
ANTHROPIC_API_KEY=
APIFY_API_TOKEN=
MP_TICKET=
```

---

## Estado actual del proyecto

- [ ] Repo creado y estructura base
- [ ] Supabase: proyecto creado y tablas migradas
- [ ] Apify: cuenta creada y Actor probado
- [ ] Backend: endpoint `/sync` que trae Compras Ágiles
- [ ] IA: filtro de relevancia funcionando
- [ ] IA: generador de cotizaciones funcionando
- [ ] Frontend: bandeja de oportunidades
- [ ] Frontend: vista detalle + editor de cotización
- [ ] Frontend: generación de PDF
- [ ] Deploy: Vercel (frontend) + Railway (backend)

---

## Contacto del proyecto

- Cliente: Industrial y Comercial Talinay Ltda.
- Web: https://talinay.cl
- Correo: talinay@talinay.cl

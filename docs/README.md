# Talinay — Sistema de Compras Públicas

Sistema semi-automático para detectar oportunidades en Mercado Público (Compras Ágiles y licitaciones), analizar relevancia con IA, y generar cotizaciones listas para enviar.

Desarrollado para **Industrial y Comercial Talinay Ltda.** (https://talinay.cl)

---

## El problema

Talinay es una fábrica con 35+ años de historia que pierde oportunidades de venta al Estado porque nadie tiene tiempo de revisar el portal todos los días. Este sistema automatiza el monitoreo y la generación de cotizaciones — el humano solo aprueba y sube el documento final.

## Cómo funciona

1. El sistema consulta Compras Ágiles (via Apify) y licitaciones (API oficial MP) automáticamente
2. La IA analiza cada oportunidad y le asigna un score de relevancia para Talinay
3. Las oportunidades relevantes aparecen en el dashboard con un borrador de cotización generado
4. El usuario revisa, edita si quiere, y descarga el PDF para subir a Mercado Público

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | React + Vite + TailwindCSS |
| Backend | FastAPI (Python) |
| Base de datos | Supabase (PostgreSQL) |
| IA | Claude API (Anthropic) |
| Scraping Compras Ágiles | Apify Actor `licify/mercadopublico-compraagil` |
| Licitaciones | API oficial Mercado Público |
| Deploy frontend | Vercel |
| Deploy backend | Railway |

## Estructura del repo

```
talinay-compras/
├── frontend/          # React + Vite
│   ├── src/
│   └── .env.example
├── backend/           # FastAPI
│   ├── services/
│   └── .env.example
├── docs/              # Documentación adicional
├── CLAUDE.md          # Contexto para Claude Code
└── README.md
```

## Setup local

### Requisitos
- Node.js 18+
- Python 3.11+
- Cuenta en Supabase
- API key de Anthropic
- API token de Apify
- Ticket de Mercado Público

### Instalación

```bash
# Clonar
git clone https://github.com/TU_USUARIO/talinay-compras.git
cd talinay-compras

# Frontend
cd frontend
cp .env.example .env   # completar variables
npm install
npm run dev

# Backend (otra terminal)
cd backend
cp .env.example .env   # completar variables
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Variables de entorno

Ver `.env.example` en `/frontend` y `/backend`.

**Nunca commitear archivos `.env` con valores reales.**

## Colaboradores

| Nombre | Rol |
|--------|-----|
| Ignacio | Desarrollo full-stack, PM |
| [Hermano] | Desarrollo full-stack |

---

> Para contexto completo del proyecto ver `CLAUDE.md`

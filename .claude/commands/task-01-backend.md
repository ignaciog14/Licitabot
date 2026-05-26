Implementa HU-01: estructura base del backend FastAPI para el proyecto Talinay.

Lee el CLAUDE.md en la raíz antes de empezar — tiene el contexto completo del proyecto, el stack, las variables de entorno y las convenciones de código.

## Qué construir

Inicializa el proyecto FastAPI en `/backend` con esta estructura:

```
backend/
├── main.py               # FastAPI app, CORS, routers registrados
├── config.py             # Variables de entorno via pydantic-settings
├── database.py           # Cliente Supabase
├── requirements.txt      # Dependencias
├── routers/
│   ├── __init__.py
│   ├── oportunidades.py  # CRUD de oportunidades
│   └── sync.py           # Endpoints de sincronización
└── services/
    ├── __init__.py
    ├── apify.py           # (vacío por ahora, solo el esqueleto)
    ├── mercado_publico.py # (vacío por ahora, solo el esqueleto)
    └── ia.py              # (vacío por ahora, solo el esqueleto)
```

## Criterios de aceptación

- `uvicorn main:app --reload` levanta sin errores desde `/backend`
- `GET /health` retorna `{"status": "ok", "version": "0.1.0"}`
- `GET /docs` muestra Swagger con los routers registrados
- `config.py` lee todas las variables de entorno del `backend/.env.example`
- CORS configurado para `http://localhost:5173` y variable `FRONTEND_URL` para producción
- `GET /oportunidades` retorna `[]` sin error (aunque BD esté vacía)

## Dependencias a incluir en requirements.txt

```
fastapi
uvicorn[standard]
pydantic-settings
python-dotenv
supabase
anthropic
httpx
```

## Al terminar

Crea el branch `feat/backend-base`, haz commit con mensaje `feat: estructura base FastAPI con health check y routers` y muestra cómo correr el servidor.

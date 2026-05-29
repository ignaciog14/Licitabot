Levanta el proyecto Licitabot completo: backend FastAPI + frontend React. Sigue estos pasos en orden.

## Paso 1 — Liberar puertos

Mata cualquier proceso que esté usando los puertos 8000 y 5173:

```bash
fuser -k 8000/tcp 2>/dev/null; fuser -k 5173/tcp 2>/dev/null; echo "puertos liberados"
```

## Paso 2 — Levantar el backend

```bash
cd /home/ignacio/proyectos/licitabot/backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000 > /tmp/backend.log 2>&1 &
```

Espera 3 segundos y verifica que responde:

```bash
sleep 3 && curl -s http://localhost:8000/health
```

Si falla (no hay respuesta), muestra el log de error:

```bash
cat /tmp/backend.log
```

Si el error dice que falta `.venv`, ejecuta primero:

```bash
cd /home/ignacio/proyectos/licitabot/backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt -q
```

Y luego repite el Paso 2.

## Paso 3 — Levantar el frontend

```bash
cd /home/ignacio/proyectos/licitabot/frontend && npm run dev -- --host > /tmp/frontend.log 2>&1 &
```

Espera 3 segundos y verifica:

```bash
sleep 3 && curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
```

Si devuelve `200`, está corriendo. Si falla, muestra el log:

```bash
cat /tmp/frontend.log
```

## Paso 4 — Reportar estado

Informa al usuario con este formato exacto:

---

**Proyecto levantado**

- Backend: http://localhost:8000 — [ok / ERROR: detalle]
- Frontend: http://localhost:5173 — [ok / ERROR: detalle]

Abrí **http://localhost:5173** en el browser para usar la app.

> Si el `ANTHROPIC_API_KEY` está vacío en `backend/.env`, las funciones de IA (filtro y cotizaciones) no van a funcionar hasta que lo configures.

---

Si algún servicio falló, explica el error y cómo resolverlo. No marques el task como exitoso si alguno no levantó.

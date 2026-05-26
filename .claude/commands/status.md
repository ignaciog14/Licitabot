Genera un reporte de estado del proyecto Talinay. Ejecuta los siguientes pasos y presenta un resumen claro.

## Paso 1 — Lee el contexto

Lee `docs/BACKLOG.md` para tener la lista completa de HUs y sprints.

## Paso 2 — Revisa el estado real del código

Ejecuta estos comandos para ver qué existe realmente:

```bash
git log --oneline -20
git branch -a
find backend -type f -name "*.py" 2>/dev/null | sort
find frontend/src -type f 2>/dev/null | sort
```

## Paso 3 — Determina el estado de cada HU

Para cada HU del backlog, determina si está:
- **Completa** — el código existe y cumple los criterios de aceptación
- **En progreso** — hay código parcial o un branch abierto
- **Pendiente** — no hay código todavía

Basa tu evaluación en los archivos que existen, no en suposiciones.

## Paso 4 — Presenta el reporte en este formato exacto

---

## Estado del proyecto Talinay — [fecha de hoy]

### Último trabajo realizado
[Qué se hizo, basado en los commits más recientes y los archivos existentes]

### Lo que está completo
[Lista de HUs completadas con ✅]

### En progreso
[Lo que está a medias, si hay algo]

### Próximo paso
**[Nombre del task]** — [una línea explicando qué es y por qué es lo siguiente lógico]

Para ejecutarlo: `/task-XX-nombre`

### Sprint actual
[Sprint 1/2/3/4] — [N de M HUs completadas]

---

Sé directo y preciso. No inventes progreso — si no hay archivos de código, el proyecto está en cero y lo dices.

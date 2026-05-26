Implementa HU-03: estructura base del frontend React + Vite + TailwindCSS para el proyecto Talinay.

Lee el CLAUDE.md en la raíz antes de empezar — tiene el stack completo y las variables de entorno del frontend.

## Qué construir

Inicializa el proyecto en `/frontend` con esta estructura:

```
frontend/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── package.json
└── src/
    ├── main.jsx           # React Query provider + Router
    ├── App.jsx            # Rutas principales
    ├── lib/
    │   └── api.js         # Cliente axios apuntando a VITE_API_URL
    ├── components/
    │   └── Layout.jsx     # Navbar + contenido
    └── pages/
        ├── Bandeja.jsx    # Ruta "/" — placeholder "Bandeja de oportunidades"
        └── Detalle.jsx    # Ruta "/oportunidad/:id" — placeholder
```

## Criterios de aceptación

- `npm run dev` levanta en `http://localhost:5173` sin errores ni warnings de consola
- React Router configurado: `/` va a `Bandeja`, `/oportunidad/:id` va a `Detalle`
- React Query (`@tanstack/react-query`) inicializado como provider en `main.jsx`
- `src/lib/api.js` exporta instancia de axios con `baseURL: import.meta.env.VITE_API_URL`
- Navbar visible con texto "Talinay Compras" y links a Bandeja e Historial
- TailwindCSS funcionando (el navbar debe tener clases de Tailwind aplicadas)
- Las páginas placeholder muestran el nombre de la vista en `<h1>`

## Dependencias

```json
"dependencies": {
  "react": "^18",
  "react-dom": "^18",
  "react-router-dom": "^6",
  "@tanstack/react-query": "^5",
  "axios": "^1"
}
```

## Al terminar

Crea el branch `feat/frontend-base`, haz commit con `feat: estructura base React con routing y React Query`. Muestra cómo verificar que levanta.

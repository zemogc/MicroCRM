# MicroCRM · Frontend

Interfaz web de MicroCRM construida con **React 19**, **Vite** y **Bootstrap 5**.

```bash
cp .env.example .env    # VITE_API_URL=http://localhost:8000
npm install
npm run dev             # http://localhost:5173
```

| Script | Descripción |
|---|---|
| `npm run dev` | Servidor de desarrollo con recarga en caliente |
| `npm run build` | Compilación de producción en `dist/` |
| `npm run preview` | Sirve la compilación localmente |
| `npm run lint` | Revisión con ESLint |

## Estructura

```
src/
├── components/   # Layout, Sidebar, PrivateRoute, ThemeToggle, StatusBadge
├── constants/    # Catálogos de estados (tareas y clientes)
├── context/      # AuthContext (sesión JWT) y ThemeContext (claro/oscuro)
├── modules/      # Pantallas: Auth, Inicio, Clientes, Proyectos, Tareas, Equipo
├── services/     # Cliente axios con token e interceptor de 401
├── styles/       # Estilos globales
└── utils/        # Formato de fechas y mensajes de error
```

La documentación completa del proyecto está en el [README principal](../../README.md).

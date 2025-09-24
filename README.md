# Proyecto Final — Entregable 1 (Semana 3)
## Especificación + Vertical Slice (MVP Alpha)

Este primer entregable consiste en una **definición clara del proyecto** para validar que el alcance está bien acotado.

> **Stack:** React + Vite (frontend), FastAPI + uvicorn (backend), `uv` para gestión de paquetes en Python

---

## 1) Objetivos de aprendizaje
- Definir con precisión **qué** se va a construir (problema, usuarios, alcance, datos y API).
- Comprobar de forma temprana la **integración** React ↔ FastAPI con una entidad real y validaciones.
- Practicar **buenas prácticas**: documentación clara, estructura de proyecto.

---

## 2) Qué deben entregar (en un solo repositorio)
> Estructura sugerida al final del documento.

1. **README del proyecto (ejecutivo y accionable)**  
   Incluya:
   - *Elevator pitch* (3–5 líneas): problema, solución, para quién.
   - Usuarios/segmentos y principales **casos de uso**.
   - **Objetivos** y **No‑objetivos** (lo que explícitamente no harán).
   - Métricas/KPIs de éxito (cómo sabrán que funciona).
   - Variables de entorno y puertos (p. ej. `VITE_API_URL`).
   - Enlace al **roadmap** (Semana 3 → 5 → 7).

2. **Historias de usuario y alcance (MVP)**  
   - 6–10 historias priorizadas (MoSCoW o por valor).  
   - Cada historia con **criterios de aceptación** y, si aplica, **escenarios** (Given/When/Then).  
   - **Mapa de versiones**: qué entra en el MVP (Semana 5) vs. qué se posterga para el final (Semana 7).

3. **Modelo de datos (borrador inicial)**  
   - Diagrama ERD sencillo (PNG o markdown).

4. **Plan del proyecto**  
   - Roadmap con hitos hasta **Semana 5** (Entregable 2) y **Semana 7** (final).  
 
---

## 3) Rúbrica de evaluación (100 pts)
**Especificación y diseño (50 pts)**  
- Historias y alcance priorizado (30)  
- Modelo de datos (20)  

**Documentación y calidad (50 pts)**  
- README, claridad de instrucciones (50)  

---

## 4) Estructura sugerida del repositorio
```
project/
├─ backend/
│  ├─ app/
│  │  ├─ api/routes/    # endpoints
│  │  ├─ models/        # pydantic schemas
│  │  ├─ core/          # config (CORS, settings)
│  │  └─ main.py
│  ├─ requirements.txt
│  └─ tests/            # pytest + httpx
└─ frontend/
   ├─ src/
   │  ├─ components/    # componente de la entidad
   │  ├─ api.js
   │  ├─ App.jsx
   │  └─ main.jsx
   ├─ .env.development
   ├─ package.json
   └─ vite.config.js
```

---
## 5) Entrega y formato
- **Nombre del documento/zip**: `proy-<equipo>-entregable1-semana3`.

> **Fecha de entrega:** Miercoles 24 de septiembre 23:59.  
> **Zona horaria:** America/Bogota.

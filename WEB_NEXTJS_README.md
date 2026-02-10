# Web Next.js + API para el modelo de sentimiento

El modelo de NLP (sklearn + joblib) sigue en **Python**. Next.js solo consume una **API REST** que carga ese modelo.

## Arquitectura

```
┌─────────────────┐         HTTP          ┌─────────────────┐
│   Next.js       │  POST /api/valorar   │   FastAPI        │
│   (puerto 3000)  │ ──────────────────► │   (puerto 8000)  │
│   Frontend      │  GET /api/resenas    │   + model .joblib│
└─────────────────┘ ◄────────────────── └─────────────────┘
```

## Cómo ejecutarlo

### 1. Backend (API Python)

Desde la raíz del proyecto:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Comprueba: [http://localhost:8000/api/health](http://localhost:8000/api/health) → `{"ok": true, "modelo_cargado": true}`.

### 2. Frontend (Next.js)

En otra terminal:

```bash
cd web
npm install
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000). La app llama a `NEXT_PUBLIC_API_URL` (por defecto `http://localhost:8000`).

### 3. Variables de entorno

- **Backend**: no necesita variables; usa la ruta relativa al proyecto para `model/sentiment_pipeline.joblib` y `data/barcelona_solo_espanol.csv`.
- **Web**: en `web/.env.local` puedes cambiar la URL de la API:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```
  En producción, pon aquí la URL donde esté desplegada la API.

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado de la API y si el modelo está cargado |
| POST | `/api/valorar` | Body: `{"texto": "..."}` → devuelve estrellas, puntuación media y valoración |
| GET | `/api/resenas?limite=200` | Lista de reseñas del CSV con valoración aplicada |

## Despliegue

- **API**: puedes desplegarla en cualquier servidor que ejecute Python (Railway, Render, Fly.io, VPS con Gunicorn+Uvicorn, etc.). Sube la carpeta `backend`, el directorio `model/` (con el `.joblib`) y `data/` (con el CSV).
- **Next.js**: Vercel, Netlify, etc. Configura `NEXT_PUBLIC_API_URL` con la URL pública de tu API para que el navegador pueda llamarla (CORS ya está permitido para el origen que uses).

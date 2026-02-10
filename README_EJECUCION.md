# Guía de ejecución del proyecto NLP Airbnb

Pasos para ejecutar el proyecto completo en local: entrenamiento del modelo, API y web.

---

## Requisitos previos

- **Python 3.9+** (recomendado 3.10 o 3.11)
- **Node.js 18+** y npm
- Git (opcional)

---

## 1. Clonar o abrir el proyecto

```bash
cd C:\ruta\al\proyecto\nlp_airbnb
```

---

## 2. Entorno Python y dependencias (raíz del proyecto)

En la **raíz** del repositorio (donde está `train_model.py`):

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno
# Windows (CMD):
venv\Scripts\activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

Dependencias de la raíz: `pandas`, `scikit-learn`, `joblib` (para entrenar el modelo).

---

## 3. Entrenar el modelo

Desde la **raíz** del proyecto, con el entorno virtual activado:

```bash
python train_model.py
```

- Lee datos de `data/barcelona_solo_espanol.csv`
- Usa `data/diccionario_extenso.csv` y `data/frases_sentimiento.csv` para etiquetar
- Entrena un pipeline TF-IDF + LogisticRegression
- Guarda el modelo en `model/sentiment_pipeline.joblib`

Si no existe la carpeta `model`, se crea automáticamente. Es necesario tener ya los CSV en `data/`.

### Añadir más reseñas neutras y negativas (opcional)

Si el dataset tiene muchas reseñas positivas y pocas negativas/neutras, puedes generar reseñas sintéticas y añadirlas al CSV:

```bash
python scripts/generar_resenas_negativas_neutras.py
```

- Crea una copia de seguridad en `data/barcelona_solo_espanol.backup.csv`
- Añade unas **40 reseñas neutras** y **80 negativas** (en español) a `data/barcelona_solo_espanol.csv`
- Después conviene **volver a entrenar** el modelo: `python train_model.py`

---

## 4. Backend (API FastAPI)

En una terminal, desde la **raíz**:

```bash
# Mismo entorno virtual activado
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

O desde la carpeta `backend`:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

La API quedará en **http://localhost:8000**.

- `GET /api/health` — estado y si el modelo está cargado
- `POST /api/valorar` — body `{"texto": "..."}` → estrellas y valoración
- `GET /api/resenas?limite=200` — lista de reseñas con valoración

El backend espera:
- `model/sentiment_pipeline.joblib` (relativo a la raíz del proyecto)
- `data/diccionario_extenso.csv`
- `data/frases_sentimiento.csv`
- `data/barcelona_solo_espanol.csv` (para `/api/resenas`)

---

## 5. Frontend (Next.js)

En **otra terminal**:

```bash
cd web
npm install
npm run dev
```

La web quedará en **http://localhost:3000**.

Por defecto la app usa la API en `http://localhost:8000`. Para cambiar la URL:

```bash
# Windows (PowerShell)
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"; npm run dev

# Linux/macOS
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

O crea un archivo `web/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 6. Resumen de comandos (dos terminales)

**Terminal 1 — Backend**

```bash
cd C:\ruta\al\proyecto\nlp_airbnb
.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend**

```bash
cd C:\ruta\al\proyecto\nlp_airbnb\web
npm run dev
```

Abre **http://localhost:3000** en el navegador.

---

## Estructura de carpetas relevante

```
nlp_airbnb/
├── data/
│   ├── barcelona_solo_espanol.csv   # Reseñas para listar y entrenar
│   ├── diccionario_extenso.csv      # Palabras con sentimiento (-3 a +3)
│   └── frases_sentimiento.csv       # Frases ambiguas (ej. "buena mierda")
├── model/
│   └── sentiment_pipeline.joblib   # Modelo entrenado (generado por train_model.py)
├── backend/
│   ├── main.py                      # API FastAPI
│   ├── sentiment_engine.py          # Lógica de valoración
│   └── requirements.txt
├── web/                             # Next.js
│   ├── app/page.tsx
│   ├── lib/api.ts                   # Llamadas a la API (usa NEXT_PUBLIC_API_URL)
│   └── package.json
├── train_model.py                   # Script de entrenamiento
├── requirements.txt                 # Dependencias Python raíz
├── README_EJECUCION.md              # Este archivo
└── README_MODELO.md                 # Explicación del modelo
```

---

## Solución de problemas

| Problema | Qué comprobar |
|----------|----------------|
| "No se encontró el archivo de datos" | Que existan los CSV en `data/` y que el backend se ejecute desde la raíz o que `BASE_DIR` apunte a la raíz del proyecto. |
| "Modelo no cargado" | Que exista `model/sentiment_pipeline.joblib` (ejecutar antes `python train_model.py`). |
| Error de CORS | Backend permite `http://localhost:3000` y `http://127.0.0.1:3000`. Si usas otro origen, añádelo en `backend/main.py` en `allow_origins`. |
| La web no conecta con la API | Que el backend esté en marcha en el puerto 8000 y que `NEXT_PUBLIC_API_URL` sea `http://localhost:8000` (o la URL correcta). |

---

## Build de producción (web)

```bash
cd web
npm run build
npm start
```

La variable `NEXT_PUBLIC_API_URL` debe apuntar a la URL pública del backend en producción.

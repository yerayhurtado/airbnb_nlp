# NLP Airbnb — Valoración de reseñas con sentimiento

Proyecto de **NLP** que valora reseñas de Airbnb en español: clasifica el sentimiento (positivo, neutro, negativo) y lo mapea a una puntuación de **0 a 5 estrellas**. El modelo alcanza **94,69% de accuracy** en test (validación cruzada 5-fold ~91%). Incluye pipeline TF-IDF + regresión logística, API en FastAPI y web tipo Airbnb en Next.js.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js&logoColor=white)

---

## Qué hace el proyecto

- **Clasifica el sentimiento** de reseñas en español (Positivo / Neutro / Negativo) con **~94,7% accuracy** en test.
- **Asigna estrellas (0–5)** a partir de las probabilidades del modelo.
- **Lista reseñas** de un CSV de Barcelona con su valoración y permite **buscar, filtrar y ordenar**.
- **Valorar tu propia reseña**: escribe un texto y el modelo devuelve estrellas y etiqueta.
- Usa un **diccionario de intensidad** (-3 a +3) y **frases ambiguas** (ej. "buena mierda" → positivo) para etiquetar datos y corregir inferencia.

---

## Stack

| Parte        | Tecnología |
|-------------|------------|
| **Modelo**  | Python, scikit-learn (TF-IDF + Logistic Regression), diccionario + frases para etiquetado |
| **Backend** | FastAPI, uvicorn, pandas, joblib |
| **Frontend**| Next.js 14 (App Router), React, Tailwind CSS, Iconify |

---

## Estructura del repositorio

```
nlp_airbnb/
├── data/
│   ├── barcelona_solo_espanol.csv   # Reseñas (entrenamiento + listado)
│   ├── diccionario_extenso.csv      # Palabras con sentimiento (-3 a +3)
│   └── frases_sentimiento.csv       # Frases ambiguas (ej. "buena mierda")
├── model/
│   └── sentiment_pipeline.joblib   # Modelo serializado (generado al entrenar)
├── backend/                         # API FastAPI
│   ├── main.py
│   ├── sentiment_engine.py
│   └── requirements.txt
├── web/                             # App Next.js
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── icon.svg
│   └── lib/api.ts
├── scripts/
│   └── generar_resenas_negativas_neutras.py  # Añade reseñas neutras/negativas al CSV
├── train_model.py                   # Entrena el pipeline y guarda el modelo
├── requirements.txt                 # Dependencias Python (raíz)
├── README.md                        # Este archivo
├── README_EJECUCION.md              # Guía paso a paso para ejecutar todo
└── README_MODELO.md                # Explicación detallada del modelo
```

---

## Inicio rápido

### Requisitos

- **Python 3.9+** y **Node.js 18+**

### 1. Clonar e instalar

```bash
git clone https://github.com/TU_USUARIO/nlp_airbnb.git
cd nlp_airbnb
```

### 2. Entrenar el modelo (Python)

```bash
python -m venv venv
# Windows (PowerShell): .\venv\Scripts\Activate.ps1
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python train_model.py
```

Genera `model/sentiment_pipeline.joblib`. Los datos deben estar en `data/` (ver [README_EJECUCION.md](README_EJECUCION.md)).

### 3. Levantar el backend

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

API en **http://localhost:8000** (`/api/health`, `/api/valorar`, `/api/resenas`).

### 4. Levantar el frontend

En otra terminal:

```bash
cd web
npm install
npm run dev
```

Abre **http://localhost:3000**. La web usa por defecto la API en `http://localhost:8000` (configurable con `NEXT_PUBLIC_API_URL`).

---

## Documentación adicional

- **[README_EJECUCION.md](README_EJECUCION.md)** — Pasos detallados para ejecutar el proyecto (entorno, entrenamiento, backend, frontend, variables de entorno, problemas frecuentes).
- **[README_MODELO.md](README_MODELO.md)** — Cómo funciona el modelo: datos, etiquetado con diccionario y frases, pipeline TF-IDF + Logistic Regression, inferencia y corrección por frases.

---

## Opcional: más reseñas neutras/negativas

Si el dataset tiene muchas positivas y pocas negativas o neutras:

```bash
python scripts/generar_resenas_negativas_neutras.py
python train_model.py   # reentrenar
```

---

## Licencia

Proyecto de uso educativo. Ajusta la licencia según prefieras.

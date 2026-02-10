"""
API FastAPI para el modelo de sentimiento de reseñas Airbnb.
Arrancar: uvicorn main:app --reload --port 8000
"""
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sentiment_engine import valorar_reseña, get_pipeline

app = FastAPI(title="Airbnb Sentiment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "barcelona_solo_espanol.csv"


class ValorarRequest(BaseModel):
    texto: str


class ValorarResponse(BaseModel):
    estrellas: int
    puntuacion_media: float
    valoracion: str
    estrellas_emoji: str


@app.get("/api/health")
def health():
    """Comprueba si la API y el modelo están listos."""
    pipeline = get_pipeline()
    return {"ok": True, "modelo_cargado": pipeline is not None}


@app.post("/api/valorar", response_model=ValorarResponse)
def valorar(body: ValorarRequest):
    """Valora una reseña y devuelve estrellas (0-5), puntuación media y etiqueta."""
    if not (body.texto or "").strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
    return valorar_reseña(body.texto)


@app.get("/api/resenas")
def listar_resenas(limite: int = 200):
    """
    Devuelve reseñas del CSV de Barcelona con su valoración.
    Opcional: ?limite=100 para limitar resultados (por rendimiento).
    """
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="No se encontró el archivo de datos")
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["comments"])
    df = df.head(limite)
    rows = []
    for _, r in df.iterrows():
        v = valorar_reseña(str(r.get("comments", "")))
        rows.append({
            "id": str(r.get("id", "")),
            "comments": str(r.get("comments", "")),
            "reviewer_name": str(r.get("reviewer_name", "")),
            "date": str(r.get("date", "")),
            "estrellas": v["estrellas"],
            "puntuacion_media": v["puntuacion_media"],
            "valoracion": v["valoracion"],
            "estrellas_emoji": v["estrellas_emoji"],
        })
    return {"resenas": rows, "total": len(rows)}

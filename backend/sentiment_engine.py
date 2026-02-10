"""
Motor de valoración de reseñas: carga el modelo y expone valorar_reseña().
La intensidad de las palabras viene del diccionario (-3 a +3).
Frases ambiguas (ej. "buena mierda" = positivo) se corrigen con data/frases_sentimiento.csv.
"""
import re
import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "sentiment_pipeline.joblib"
DATA_DIR = BASE_DIR / "data"

PUNTUACION_POR_CLASE = {"Negativo": 0, "Neutro": 2.5, "Positivo": 5}

_pipeline = None
_lexico = None
_frases_lexico = None


def _cargar_lexicos():
    global _lexico, _frases_lexico
    if _lexico is not None:
        return
    _lexico = {}
    _frases_lexico = {}
    try:
        dicc = pd.read_csv(DATA_DIR / "diccionario_extenso.csv")
        _lexico = dict(zip(dicc["Palabra"].str.lower().str.strip(), dicc["Sentimiento"]))
    except Exception:
        pass
    try:
        frases_df = pd.read_csv(DATA_DIR / "frases_sentimiento.csv")
        for _, row in frases_df.iterrows():
            palabras_frase = tuple(str(row["Frase"]).lower().strip().split())
            if len(palabras_frase) >= 2:
                _frases_lexico[palabras_frase] = int(row["Sentimiento"])
    except Exception:
        pass


def _score_lexico_con_frases(texto):
    """Devuelve la puntuación del texto usando diccionario + frases (misma lógica que entrenamiento)."""
    _cargar_lexicos()
    palabras = re.findall(r"\b\w+\b", str(texto).lower())
    if not palabras:
        return 0
    used = set()
    score = 0
    for n in (3, 2):
        if n > len(palabras):
            continue
        for i in range(len(palabras) - n + 1):
            if any(i + k in used for k in range(n)):
                continue
            ngram = tuple(palabras[i : i + n])
            if ngram in _frases_lexico:
                score += _frases_lexico[ngram]
                for k in range(n):
                    used.add(i + k)
    for i, p in enumerate(palabras):
        if i not in used:
            score += _lexico.get(p, 0)
    return score


def get_pipeline():
    global _pipeline
    if _pipeline is None and MODEL_PATH.exists():
        _pipeline = joblib.load(MODEL_PATH)
    return _pipeline


def valorar_reseña(texto):
    pipeline = get_pipeline()
    t = str(texto).strip().lower() or " "
    if pipeline is None:
        score = _score_lexico_con_frases(t)
        if score > 0:
            estrellas, valoracion = 4, "Positivo"
        elif score < 0:
            estrellas, valoracion = 1, "Negativo"
        else:
            estrellas, valoracion = 3, "Neutro"
        return {
            "estrellas": estrellas,
            "puntuacion_media": 2.5 if valoracion == "Neutro" else (5.0 if valoracion == "Positivo" else 0.0),
            "valoracion": valoracion,
            "estrellas_emoji": "★" * estrellas + "☆" * (5 - estrellas),
        }

    proba = pipeline.predict_proba([t])[0]
    clases = pipeline.classes_
    puntuacion_media = sum(
        PUNTUACION_POR_CLASE.get(clases[i], 2.5) * proba[i] for i in range(len(clases))
    )
    estrellas = round(puntuacion_media)
    estrellas = max(0, min(5, estrellas))
    if estrellas <= 1:
        valoracion = "Negativo"
    elif estrellas <= 3:
        valoracion = "Neutro"
    else:
        valoracion = "Positivo"

    # Corrección por frases ambiguas: si el lexico+frases sugiere lo contrario, corregir
    score_frases = _score_lexico_con_frases(t)
    if score_frases >= 2 and valoracion == "Negativo":
        estrellas, puntuacion_media, valoracion = 4, 4.0, "Positivo"
    elif score_frases <= -2 and valoracion == "Positivo":
        estrellas, puntuacion_media, valoracion = 1, 1.0, "Negativo"

    estrellas_emoji = "★" * estrellas + "☆" * (5 - estrellas)
    return {
        "estrellas": estrellas,
        "puntuacion_media": round(puntuacion_media, 2),
        "valoracion": valoracion,
        "estrellas_emoji": estrellas_emoji,
    }

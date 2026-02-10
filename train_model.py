"""
Entrena un modelo de NLP para clasificar el sentimiento de reseñas Airbnb (español).
Usa el diccionario de sentimiento para etiquetar los datos y un pipeline TF-IDF + LogisticRegression.
Objetivo: accuracy >= 90%.
"""
import re
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

DATA_DIR = Path(__file__).parent / "data"
MODEL_DIR = Path(__file__).parent / "model"
MODEL_DIR.mkdir(exist_ok=True)


def cargar_datos():
    df = pd.read_csv(DATA_DIR / "barcelona_solo_espanol.csv")
    dicc = pd.read_csv(DATA_DIR / "diccionario_extenso.csv")
    lexico = dict(zip(dicc["Palabra"].str.lower().str.strip(), dicc["Sentimiento"]))
    # Frases que deshacen ambigüedades (ej. "buena mierda" = positivo, "una mierda" = negativo)
    frase_path = DATA_DIR / "frases_sentimiento.csv"
    frases_lexico = {}
    if frase_path.exists():
        frases_df = pd.read_csv(frase_path)
        for _, row in frases_df.iterrows():
            palabras_frase = tuple(str(row["Frase"]).lower().strip().split())
            if len(palabras_frase) >= 2:
                frases_lexico[palabras_frase] = int(row["Sentimiento"])
    return df, lexico, frases_lexico


def etiquetar_con_lexico(texto, lexico, frases_lexico=None):
    """
    Etiqueta por suma del diccionario. Si hay frases_lexico, primero aplica
    las frases (2 o 3 palabras) y no suma las palabras que forman parte de una
    frase coincidente. Así "buena mierda" → positivo y "una mierda" / "es una mierda" → negativo.
    """
    palabras = re.findall(r"\b\w+\b", str(texto).lower())
    if not palabras:
        return "Neutro"
    used = set()
    score = 0
    if frases_lexico:
        # Primero trigramas, luego bigramas (prioridad a frases más largas)
        for n in (3, 2):
            for i in range(len(palabras) - n + 1):
                if any(i + k in used for k in range(n)):
                    continue
                ngram = tuple(palabras[i : i + n])
                if ngram in frases_lexico:
                    score += frases_lexico[ngram]
                    for k in range(n):
                        used.add(i + k)
    for i, p in enumerate(palabras):
        if i not in used:
            score += lexico.get(p, 0)
    if score > 0:
        return "Positivo"
    if score < 0:
        return "Negativo"
    return "Neutro"


def main():
    print("Cargando datos...")
    df, lexico, frases_lexico = cargar_datos()
    df = df.dropna(subset=["comments"])
    df["comments"] = df["comments"].astype(str).str.strip()
    df = df[df["comments"].str.len() > 0]
    if frases_lexico:
        print(f"  Léxico de frases: {len(frases_lexico)} frases (ej. 'buena mierda' → positivo)")

    print("Generando etiquetas con el diccionario y frases...")
    df["sentimiento"] = df["comments"].apply(lambda t: etiquetar_con_lexico(t, lexico, frases_lexico))

    X = df["comments"]
    y = df["sentimiento"]

    # Eliminar clases con muy pocas muestras para estratificar
    counts = y.value_counts()
    min_samples = 5
    valid_labels = counts[counts >= min_samples].index.tolist()
    mask = y.isin(valid_labels)
    X, y = X[mask], y[mask]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nPipeline: TF-IDF + LogisticRegression")
    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=8000,
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    C=2.0,
                    solver="lbfgs",
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    print("Entrenando...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy en test: {acc:.4f} ({acc*100:.2f}%)")

    if acc < 0.90:
        print("Probando validación cruzada para ajuste...")
        scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
        print(f"CV accuracy: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")
        # Probar con más features o otro C
        for C in [1.0, 3.0, 5.0]:
            pipeline.set_params(clf__C=C)
            pipeline.fit(X_train, y_train)
            acc_c = accuracy_score(y_test, pipeline.predict(X_test))
            if acc_c > acc:
                acc = acc_c
                print(f"  C={C} -> test accuracy {acc_c:.4f}")
        pipeline.set_params(clf__C=2.0)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
    else:
        scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
        print(f"Validación cruzada (5-fold): {scores.mean():.4f} (+/- {scores.std()*2:.4f})")

    print("\nClassification report (test):")
    print(classification_report(y_test, y_pred))
    print("Confusion matrix (test):")
    print(confusion_matrix(y_test, y_pred, labels=pipeline.classes_))

    joblib.dump(pipeline, MODEL_DIR / "sentiment_pipeline.joblib")
    print(f"\nModelo guardado en {MODEL_DIR / 'sentiment_pipeline.joblib'}")

    if acc >= 0.90:
        print("\nObjetivo cumplido: accuracy >= 90%")
    else:
        print(f"\nAccuracy actual {acc*100:.2f}%. Revisa datos o hiperparámetros.")


if __name__ == "__main__":
    main()

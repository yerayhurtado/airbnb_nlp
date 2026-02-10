# Explicación del modelo de sentimiento (NLP Airbnb)

Este documento describe cómo funciona el sistema de valoración de reseñas: datos, etiquetado, entrenamiento e inferencia.

---

## Objetivo

Predecir el **sentimiento** de una reseña de Airbnb en español y mapearlo a una valoración tipo **estrellas (0–5)** y etiqueta (**Positivo / Neutro / Negativo**), sin usar estrellas reales en los datos de entrenamiento.

---

## Arquitectura general

1. **Etiquetado automático**: se usa un diccionario de sentimiento y un léxico de frases para etiquetar reseñas como Positivo, Neutro o Negativo.
2. **Entrenamiento**: un pipeline **TF-IDF + Logistic Regression** aprende a clasificar texto a partir de esas etiquetas.
3. **Inferencia**: el modelo predice probabilidades por clase; se convierte a puntuación media y estrellas, y se aplica una **corrección por frases** para casos ambiguos.

---

## 1. Datos de entrada

### 1.1 Reseñas

- **Archivo**: `data/barcelona_solo_espanol.csv`
- Contiene reseñas de Airbnb (campo `comments`) en español.
- No se usan estrellas reales; las etiquetas se generan con el diccionario y las frases.

### 1.2 Diccionario de sentimiento

- **Archivo**: `data/diccionario_extenso.csv`
- Columnas: `Palabra`, `Sentimiento`
- **Sentimiento**: valor entero de **-3** (muy negativo) a **+3** (muy positivo).
  - Negativos: -3, -2, -1  
  - Positivos: +1, +2, +3  
  - No hay 0; las palabras no listadas se consideran neutras en el léxico.

Ejemplos:

| Palabra   | Sentimiento |
|-----------|-------------|
| excelente | 3           |
| amable    | 2           |
| una mierda| (frase, no palabra suelta) |
| horrible  | -2          |

El diccionario da **intensidad**: palabras más fuertes suman o restan más en el score de léxico.

### 1.3 Frases de sentimiento (ambiguas)

- **Archivo**: `data/frases_sentimiento.csv`
- Columnas: `Frase`, `Sentimiento`
- Sirve para **deshacer ambigüedades**: la misma palabra en distinto contexto puede cambiar el sentido.

Ejemplos:

| Frase              | Sentimiento | Motivo                    |
|--------------------|-------------|---------------------------|
| buena mierda       | 2           | Expresión positiva        |
| de puta madre      | 2           | Muy positivo (coloquial)  |
| una mierda         | -3          | Muy negativo              |
| es una puta mierda | -3          | Muy negativo              |
| no está mal        | 1           | Ligeramente positivo      |

En el código se usan como **bigramas y trigramas**: secuencias de 2 o 3 palabras. Tienen prioridad sobre la suma palabra a palabra del diccionario.

---

## 2. Etiquetado para el entrenamiento

En `train_model.py`, la función `etiquetar_con_lexico(texto, lexico, frases_lexico)` asigna la etiqueta **Positivo**, **Neutro** o **Negativo** a cada reseña.

### 2.1 Proceso

1. **Tokenización**: se extraen palabras con `\b\w+\b` en minúsculas.
2. **Frases primero** (para no contar dos veces):
   - Se buscan **trigramas** en `frases_lexico`; si coinciden, se suma su sentimiento y se marcan esas palabras como “usadas”.
   - Luego **bigramas** con la misma lógica.
3. **Palabras restantes**: para cada palabra no usada en una frase, se suma `lexico.get(palabra, 0)`.
4. **Etiqueta**:
   - `score > 0` → **Positivo**
   - `score < 0` → **Negativo**
   - `score == 0` → **Neutro**

Así, “buena mierda” cuenta como frase positiva y no se suma por separado “buena” y “mierda” del diccionario, evitando errores.

### 2.2 Balance de clases

- Se filtran clases con muy pocas muestras (< 5) para poder estratificar en train/test.
- En el entrenamiento se usa `class_weight="balanced"` en la regresión logística para compensar desbalance.

---

## 3. Pipeline de entrenamiento

### 3.1 Esquema

```
Texto (reseña) → TF-IDF (vectorización) → Logistic Regression → Positivo / Neutro / Negativo
```

### 3.2 TF-IDF (`TfidfVectorizer`)

- **max_features=8000**: se mantienen los 8000 términos más informativos.
- **ngram_range=(1, 2)**: unigramas y bigramas (palabras sueltas y pares).
- **min_df=2**: ignora términos que aparecen en menos de 2 documentos.
- **max_df=0.95**: ignora términos que aparecen en más del 95% de los documentos (evita ruido muy común).
- **sublinear_tf=True**: se usa log(tf) para no dar tanto peso a repeticiones excesivas.

### 3.3 Clasificador (Logistic Regression)

- **solver="lbfgs"**, **max_iter=1000**
- **C=2.0**: regularización.
- **class_weight="balanced"**: pesos inversos a la frecuencia de cada clase.
- Salida: **probabilidades** por clase (Negativo, Neutro, Positivo).

### 3.4 Guardado

- Se guarda el **pipeline completo** (TF-IDF + modelo) en `model/sentiment_pipeline.joblib`.
- Así en inferencia se aplica la misma vectorización y el mismo modelo.

---

## 4. Inferencia (valorar una reseña)

Lógica en `backend/sentiment_engine.py`, función `valorar_reseña(texto)`.

### 4.1 Si no hay modelo cargado

Se usa solo el **diccionario + frases**:

- Se calcula `score = _score_lexico_con_frases(texto)` (misma lógica que en etiquetado).
- `score > 0` → Positivo (ej. 4 estrellas).
- `score < 0` → Negativo (ej. 1 estrella).
- `score == 0` → Neutro (ej. 3 estrellas).

### 4.2 Con modelo cargado

1. **Predicción**:  
   `pipeline.predict_proba([texto])[0]` → probabilidades para Negativo, Neutro, Positivo.

2. **Puntuación media (0–5)**:
   - Se mapea cada clase a un valor:  
     Negativo → 0, Neutro → 2.5, Positivo → 5.
   - `puntuacion_media = Σ (valor_clase × probabilidad)`.
   - Se redondea a entero para obtener **estrellas** (0–5).

3. **Etiqueta**:
   - estrellas ≤ 1 → **Negativo**
   - 2–3 → **Neutro**
   - 4–5 → **Positivo**

4. **Corrección por frases ambiguas**:
   - Se calcula de nuevo `score_frases = _score_lexico_con_frases(texto)`.
   - Si `score_frases >= 2` y el modelo dio **Negativo** → se fuerza **Positivo** (4 estrellas, 4.0).
   - Si `score_frases <= -2` y el modelo dio **Positivo** → se fuerza **Negativo** (1 estrella, 1.0).

Con esto se corrige que expresiones como “buena mierda” o “de puta madre” no queden valoradas como negativas.

### 4.3 Salida de la API

- **estrellas**: 0–5 (entero).
- **puntuacion_media**: valor float 0–5.
- **valoracion**: "Positivo" | "Neutro" | "Negativo".
- **estrellas_emoji**: cadena tipo "★★★★☆" para mostrar en la UI.

---

## 5. Flujo de datos resumido

```
                    ENTRENAMIENTO
┌─────────────────────────────────────────────────────────────┐
│  barcelona_solo_espanol.csv  +  diccionario  +  frases      │
│           ↓                                                  │
│  Etiquetar cada reseña → Positivo / Neutro / Negativo        │
│           ↓                                                  │
│  TF-IDF (unigramas + bigramas) → Logistic Regression         │
│           ↓                                                  │
│  sentiment_pipeline.joblib                                    │
└─────────────────────────────────────────────────────────────┘

                    INFERENCIA
┌─────────────────────────────────────────────────────────────┐
│  Texto nuevo → pipeline.predict_proba()                      │
│           ↓                                                  │
│  Probabilidades → puntuación 0–5 y estrellas                 │
│           ↓                                                  │
│  (Opcional) Corrección con score de frases si hay ambigüedad  │
│           ↓                                                  │
│  estrellas, puntuacion_media, valoracion, estrellas_emoji     │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Archivos clave

| Archivo | Rol |
|---------|-----|
| `data/diccionario_extenso.csv` | Palabras con intensidad -3 a +3. |
| `data/frases_sentimiento.csv` | Frases (bigramas/trigramas) para ambigüedades. |
| `data/barcelona_solo_espanol.csv` | Corpus de reseñas para entrenar y listar. |
| `train_model.py` | Etiquetado, entrenamiento y guardado del pipeline. |
| `model/sentiment_pipeline.joblib` | Modelo serializado (TF-IDF + Logistic Regression). |
| `backend/sentiment_engine.py` | Carga del modelo, valoración y corrección por frases. |

---

## 7. Posibles mejoras

- Añadir más frases en `frases_sentimiento.csv` cuando se detecten errores sistemáticos.
- Revisar y ampliar el diccionario para palabras coloquiales o de la zona.
- Probar otros clasificadores (SVM, Random Forest) o otros vectores (p. ej. embeddings).
- Incluir negación explícita (p. ej. “no bueno”) si hace falta.

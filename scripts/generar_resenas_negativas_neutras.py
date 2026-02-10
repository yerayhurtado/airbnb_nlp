"""
Genera reseñas neutras y negativas en español y las añade a data/barcelona_solo_espanol.csv
para equilibrar el conjunto de datos (hay muchas positivas y pocas negativas).

Ejecutar desde la raíz del proyecto: python scripts/generar_resenas_negativas_neutras.py
"""
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "barcelona_solo_espanol.csv"
BACKUP_PATH = DATA_DIR / "barcelona_solo_espanol.backup.csv"

# listing_id que ya aparecen en el CSV (Barcelona)
LISTING_IDS = [703984, 1354875, 18674, 23197, 32711, 715036, 147275, 729078, 1411945]

# Nombres españoles/latinoamericanos para reviewers
NOMBRES = [
    "Carmen", "Miguel", "Rosa", "Antonio", "Elena", "Francisco", "Isabel", "David",
    "Laura", "Pablo", "Sara", "Javier", "Lucía", "Daniel", "María", "Carlos",
    "Ana", "Pedro", "Cristina", "Luis", "Patricia", "Alberto", "Marta", "Raúl",
    "Sergio", "Nuria", "Fernando", "Claudia", "Andrés", "Eva", "Roberto", "Julia",
]

# Reseñas NEUTRAS (ni muy buenas ni malas)
RESENAS_NEUTRAS = [
    "El piso está bien, nada del otro mundo. La ubicación es correcta y el anfitrión respondió a tiempo.",
    "Estancia aceptable. El apartamento es tal como en las fotos, un poco antiguo pero limpio. La zona está bien.",
    "Todo correcto. No tenemos quejas pero tampoco destacaría nada en especial. Cumple su función.",
    "El alojamiento está bien para pasar unos días. La comunicación fue fluida. Ni fu ni fa.",
    "Piso normal, ubicación aceptable. Hay que subir escaleras y no hay ascensor. Para el precio está bien.",
    "La estancia fue correcta. El piso es pequeño pero tiene lo básico. No repetiría pero no me quejo.",
    "Está bien para una estancia corta. El barrio es tranquilo. Nada que objetar ni que destacar.",
    "Todo según lo esperado. El apartamento está bien, ni muy limpio ni sucio. Ubicación regular.",
    "Experiencia normal. El anfitrión fue correcto. El piso es antiguo y las camas son normales.",
    "No está mal. La ubicación está bien pero el piso es bastante básico. Aceptable para el precio.",
    "El departamento cumple. No es lujoso pero tiene lo necesario. La zona está bien comunicada.",
    "Estancia correcta. Algunos detalles mejorables pero en general aceptable. Sin más.",
    "El piso está bien ubicado. Es algo oscuro y las instalaciones son viejas. Nada del otro mundo.",
    "Todo bien sin más. El anfitrión fue correcto. El apartamento es funcional, sin encanto especial.",
    "Aceptable. Buen precio pero el piso es muy sencillo. La cocina está justa de menaje.",
    "La ubicación está bien. El piso en sí es normal, las fotos se corresponden. Experiencia neutra.",
    "Estuvimos bien. No hubo problemas pero tampoco nos sorprendió. Todo correcto.",
    "El alojamiento está bien para lo que pagamos. Un poco lejos del centro. Nada que destacar.",
    "Piso estándar. Limpio y con lo básico. La comunicación con el host fue correcta. Ni bien ni mal.",
    "Todo correcto. El apartamento es pequeño. La zona es tranquila. Experiencia normal.",
    "Estancia sin sobresaltos. El piso está bien, algo anticuado. El anfitrión respondió cuando hicimos falta.",
    "No está mal para unos días. Las camas son normales y el baño está bien. Nada del otro mundo.",
    "El lugar está bien. No es el más céntrico pero hay transporte. El piso es funcional.",
    "Aceptable para el precio. Algunas cosas viejas pero todo funcionaba. Sin quejas importantes.",
    "Todo bien en general. El piso es tal cual. La zona está regular, no es la mejor ni la peor.",
    "Experiencia correcta. El anfitrión fue correcto. El apartamento cumple, sin más.",
    "El departamento está bien. Es antiguo y se nota. Para una estancia corta sirve.",
    "Nada que objetar. Comunicación correcta. El piso es básico pero limpio. Ubicación aceptable.",
    "Estancia neutra. Ni muy bien ni mal. El piso tiene lo necesario. La ubicación está bien.",
    "Todo según lo descrito. No hay sorpresas. El barrio es tranquilo. Correcto.",
    "El piso está bien. No destacaría nada en especial. La zona es céntrica. Aceptable.",
    "Estancia correcta. El apartamento es pequeño pero tiene lo básico. Comunicación correcta.",
    "Nada del otro mundo. Las camas son normales. El baño está bien. Para unos días sirve.",
    "Todo bien sin más. Ubicación regular. El anfitrión fue correcto. Ni bien ni mal.",
    "El departamento cumple con lo básico. Es antiguo. La cocina está justa. Aceptable.",
    "Piso estándar para el precio. No hay ascensor. La zona está bien. Experiencia normal.",
    "Correcto. No tenemos quejas. El piso es tal cual en las fotos. Nada que destacar.",
    "Estuvimos bien. El barrio es tranquilo. El piso es funcional. Sin más.",
]

# Reseñas NEGATIVAS
RESENAS_NEGATIVAS = [
    "No recomendable. El piso estaba sucio al llegar y las sábanas tenían manchas. No volvería.",
    "Decepcionante. Las fotos no se corresponden con la realidad. Muy pequeño y oscuro. No lo recomiendo.",
    "Muy mala experiencia. El anfitrión no respondió cuando tuvimos un problema con la calefacción. Frío toda la estancia.",
    "No repetiría. El apartamento huele mal, parece que no ventilan. La cocina estaba sucia.",
    "Pésima comunicación. Llegamos y no había nadie. Tuvimos que esperar más de una hora. Muy mal.",
    "El piso está en mal estado. Muebles rotos, paredes con humedad. No vale el precio que cobran.",
    "No me gustó nada. Muy lejos del centro, el barrio no me pareció seguro. El piso era cutre.",
    "Horrible. Encontramos cucarachas en la cocina. El baño estaba sucio. No recomiendo para nada.",
    "Muy decepcionado. El wifi no funcionaba, las camas incómodas. El anfitrión no solucionó nada.",
    "No recomendable. Cobran de más por limpieza y el piso estaba sucio. Una estafa.",
    "Pésimo. Ruido constante del vecindario, imposible dormir. El apartamento es muy viejo.",
    "No volvería. El check-in fue un caos, nos dieron mal las llaves. El piso olía a humedad.",
    "Mala experiencia. El anuncio dice que hay aire acondicionado y no funcionaba. Noche horrible.",
    "No lo recomiendo. El baño tiene goteras, el agua caliente no dura. Muy incómodo.",
    "Decepcionante. Fotos engañosas. El piso es mucho más pequeño y está en una zona fea.",
    "Muy mal. El anfitrión fue desagradable cuando le preguntamos por la llave. No repetiría.",
    "El apartamento está sucio y descuidado. Las toallas tenían mal olor. No vale la pena.",
    "No recomendable. Nos cobraron una tasa extra que no estaba en el anuncio. Muy caro para lo que es.",
    "Pésima ubicación. Lejos de todo, barrio ruidoso y el piso en mal estado. No volveré.",
    "Horrible estancia. La cama era incómoda, el colchón se hundía. No dormimos bien ni una noche.",
    "No me gustó. El piso está muy anticuado y la cocina no tiene ni lo básico. Decepcionante.",
    "Muy mala impresión. Llegamos y la llave no funcionaba. Perdimos horas. No lo recomiendo.",
    "El alojamiento no cumple lo prometido. Sin ascensor y cinco plantas. Las maletas fueron un suplicio.",
    "No repetiría. El wifi no llegaba a la habitación. El baño compartido estaba sucio.",
    "Decepcionante. El piso huele a tabaco. Las cortinas rotas. No corresponde al precio.",
    "Pésimo trato del anfitrión. Nos acusó de cosas que no hicimos. Muy desagradable.",
    "No recomendable. El barrio es ruidoso de noche. El apartamento pequeño y con humedad.",
    "Mala experiencia. La ducha no calentaba bien. La cocina sucia. No volvería.",
    "No vale la pena. Muy caro para la calidad. El piso está viejo y con cosas rotas.",
    "Horrible. Encontramos pelo en las sábanas. El suelo no estaba limpio. No recomiendo.",
    "El anfitrión no respondió cuando se fue la luz. Pasamos una noche a oscuras. Inaceptable.",
    "No me gustó nada. El piso está en un sótano, muy oscuro y húmedo. Deprimente.",
    "Muy decepcionado. Las fotos son de hace años. El piso está deteriorado. No recomiendo.",
    "Pésima limpieza. Polvo por todas partes, nevera sucia. No repetiríamos.",
    "No recomendable. El ascensor no funcionaba, cinco pisos a pie. El piso normal tirando a malo.",
    "Mala comunicación. Nos cambiaron el horario de llegada a última hora. El piso regular.",
    "No volvería. El colchón es viejo y se nota. El baño tiene moho. Muy decepcionante.",
    "El apartamento está sucio y el anfitrión no se hizo responsable. Muy mala experiencia.",
    "No vale lo que cuesta. Barrio regular, piso anticuado. No lo recomiendo.",
    "Decepcionante. Prometían vistas y no hay. El piso es pequeño y está mal cuidado.",
    "No recomendable. El sofá cama es incómodo. El piso está sucio. No volvería.",
    "Muy mal. El anfitrión no estaba y nos dejó esperando. El piso olía raro.",
    "Pésima experiencia. Nos cobraron de más. El apartamento no estaba limpio. No lo recomiendo.",
    "No me gustó. La habitación da a un patio de luces, cero luz. Muy deprimente.",
    "El wifi no funcionaba en todo el piso. El anfitrión no solucionó nada. Muy mal.",
    "No repetiría. Las toallas viejas y ásperas. El baño con humedad. Decepcionante.",
    "Mala experiencia. El check-in fue confuso. El piso está en una calle muy ruidosa.",
    "No vale la pena. Precio alto para un piso cutre. No lo recomiendo para nada.",
    "Horrible. La calefacción no funcionaba. Pasamos frío. El anfitrión no respondió.",
    "No recomendable. El colchón está hundido. Las paredes finas, se oye todo. Pésimo.",
    "Muy decepcionado. El piso está descuidado. Enchufes sueltos. No volveré.",
    "El apartamento no está como en las fotos. Más viejo y sucio. No lo recomiendo.",
    "No me gustó nada. La cocina mal equipada. El microondas no funcionaba. Mal.",
    "Pésimo. Nos dieron mal las instrucciones de llegada. Perdimos tiempo. No repetiría.",
    "Muy mala impresión. El edificio está en obras. Ruido todo el día. Inaceptable.",
    "No recomendable. El baño tiene goteras. La ducha no calienta bien. Muy mal.",
    "Decepcionante. Las sábanas parecían usadas. El suelo no estaba limpio. No volvería.",
    "El anfitrión fue muy seco. El piso está en mal estado. No vale el precio. No recomiendo.",
    "No repetiría. Barrio feo, piso anticuado. La cama incómoda. Mala experiencia.",
]

def generar_id_unico(existentes):
    """Genera un ID numérico grande que no esté en la lista."""
    while True:
        id_val = random.randint(400000000000000000, 999999999999999999)
        if id_val not in existentes:
            return id_val

def generar_fecha_aleatoria():
    """Fecha entre 2019 y 2025."""
    inicio = datetime(2019, 1, 1)
    fin = datetime(2025, 2, 1)
    delta = (fin - inicio).days
    d = inicio + timedelta(days=random.randint(0, delta))
    return d.strftime("%Y-%m-%d")

def main():
    if not CSV_PATH.exists():
        print(f"No se encontró {CSV_PATH}")
        return

    # Leer IDs existentes para no duplicar
    ids_existentes = set()
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ids_existentes.add(int(row["id"]))
            except (ValueError, KeyError):
                pass

    # Preparar nuevas filas: mezcla de neutras y negativas (más negativas para equilibrar)
    nuevas_filas = []
    num_neutras = 40
    num_negativas = 80

    neutras = [(r, "Neutro") for r in random.sample(RESENAS_NEUTRAS, min(num_neutras, len(RESENAS_NEUTRAS)))]
    negativas = [(r, "Negativo") for r in random.sample(RESENAS_NEGATIVAS, min(num_negativas, len(RESENAS_NEGATIVAS)))]
    reseñas_a_usar = neutras + negativas
    random.shuffle(reseñas_a_usar)

    for comentario, _ in reseñas_a_usar:
        rid = generar_id_unico(ids_existentes)
        ids_existentes.add(rid)
        reviewer_id = random.randint(1000000, 999999999)
        listing_id = random.choice(LISTING_IDS)
        date = generar_fecha_aleatoria()
        name = random.choice(NOMBRES)
        nuevas_filas.append({
            "listing_id": listing_id,
            "id": rid,
            "date": date,
            "reviewer_id": reviewer_id,
            "reviewer_name": name,
            "comments": comentario,
        })

    # Backup opcional
    import shutil
    shutil.copy(CSV_PATH, BACKUP_PATH)
    print(f"Backup guardado en {BACKUP_PATH}")

    # Leer todo el CSV actual
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        filas_actuales = list(reader)

    # Añadir nuevas filas
    filas_actuales.extend(nuevas_filas)

    # Escribir CSV completo
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filas_actuales)

    n_neutras = sum(1 for _, et in reseñas_a_usar if et == "Neutro")
    n_negativas = len(nuevas_filas) - n_neutras
    print(f"Se han añadido {len(nuevas_filas)} reseñas ({n_neutras} neutras, {n_negativas} negativas) a {CSV_PATH}")
    print(f"Total de filas ahora: {len(filas_actuales)}")

if __name__ == "__main__":
    main()

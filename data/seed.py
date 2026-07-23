import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_connection, execute_script


def seed():

    # Crear estructura
    execute_script ("d:\missions\data\squema.sql")

    conn = get_connection()
    cursor = conn.cursor()


    # =========================
    # FAMÍLIA
    # =========================

    cursor.execute("""
        INSERT INTO families (name)
        VALUES ('RoigAlvarez')
    """)

    family_id = cursor.lastrowid


    # =========================
    # USUARIS
    # =========================

    users = [
        ("Laura", "admin", "purple"),
        ("Rachel", "admin", "orange"),
        ("Iris", "child", "blue"),
        ("Roc", "child", "green")
    ]

    user_ids = {}

    for name, role, color in users:

        cursor.execute("""
            INSERT INTO users
            (family_id,name,role,favorite_color)
            VALUES (?,?,?,?)
        """,
        (family_id,name,role,color))

        user_ids[name] = cursor.lastrowid


    # =========================
    # CATEGORIES
    # =========================

    categories = [
        ("Casa","🏠"),
        ("Escola","📚"),
        ("Extraescolars","🏑"),
        ("Mascotes","🐶"),
        ("Piscina","🏊"),
        ("Hàbits","💪"),
        ("Especials","🎉")
    ]

    category_ids={}

    for name,icon in categories:

        cursor.execute("""
            INSERT INTO categories
            (name,icon)
            VALUES (?,?)
        """,
        (name,icon))

        category_ids[name]=cursor.lastrowid



    # =========================
    # TIPUS MISSIÓ
    # =========================

    types=[
        ("Individual","Només un nen"),
        ("Compartida","Qualsevol assignat pot fer-la"),
        ("Col·laborativa","Han de participar tots"),
        ("Rotativa","Canvia per torns"),
        ("Lliure","Sense assignació fixa")
    ]

    type_ids={}

    for name,desc in types:

        cursor.execute("""
        INSERT INTO mission_types
        (name,description)
        VALUES (?,?)
        """,
        (name,desc))

        type_ids[name]=cursor.lastrowid



    # =========================
    # MISSIONS
    # =========================

    missions=[

    ("Fer el llit",
     "Deixar habitació preparada",
     "🛏️",
     "Casa",
     "Individual",
     10),

    ("Recollir habitació",
     "Tenir l'espai ordenat",
     "🧹",
     "Casa",
     "Individual",
     20),

    ("Parar taula",
     "Preparar el sopar",
     "🍽️",
     "Casa",
     "Compartida",
     15),

    ("Desparar taula",
     "Recollir després de menjar",
     "🍴",
     "Casa",
     "Compartida",
     15),

    ("Treure escombraries",
     "Baixar bosses",
     "🗑️",
     "Casa",
     "Compartida",
     20),


    ("Donar menjar mascotes",
     "Menjar i aigua",
     "🐾",
     "Mascotes",
     "Rotativa",
     15),

    ("Passejar gos",
     "Fer passeig",
     "🐶",
     "Mascotes",
     "Compartida",
     30),

    ("Treure caques",
     "Netejar zona mascotes",
     "💩",
     "Mascotes",
     "Individual",
     20),


    ("Netejar fons piscina",
     "Neteja del fons",
     "🏊",
     "Piscina",
     "Col·laborativa",
     50),

    ("Netejar superfície piscina",
     "Treure fulles i brutícia",
     "🪣",
     "Piscina",
     "Col·laborativa",
     30),


    ("Deures",
     "Treball escolar",
     "📚",
     "Escola",
     "Individual",
     40),

    ("Llegir 20 minuts",
     "Lectura diària",
     "📖",
     "Hàbits",
     "Individual",
     20),

    ("Fer gimnàs",
     "Activitat física",
     "💪",
     "Hàbits",
     "Individual",
     30),


    ("Preparar bossa hoquei",
     "Material preparat",
     "🏑",
     "Extraescolars",
     "Individual",
     20),

    ("Assistir hoquei",
     "Entrenament",
     "🏑",
     "Extraescolars",
     "Individual",
     30)

    ]


    mission_ids={}


    for title,desc,icon,category,mtype,points in missions:

        cursor.execute("""
        INSERT INTO missions
        (
        family_id,
        category_id,
        title,
        description,
        icon,
        mission_type_id,
        points
        )
        VALUES (?,?,?,?,?,?,?)
        """,
        (
        family_id,
        category_ids[category],
        title,
        desc,
        icon,
        type_ids[mtype],
        points
        ))

        mission_ids[title]=cursor.lastrowid



    # =========================
    # ASSIGNACIONS
    # =========================

    assignments=[

        ("Fer el llit","Iris","owner"),
        ("Fer el llit","Roc","owner"),

        ("Passejar gos","Iris","shared"),
        ("Passejar gos","Roc","shared"),

        ("Donar menjar mascotes","Iris","shared"),
        ("Donar menjar mascotes","Roc","shared"),

        ("Netejar fons piscina","Iris","team"),
        ("Netejar superfície piscina","Roc","team"),

        ("Deures","Iris","owner"),
        ("Deures","Roc","owner"),

        ("Preparar bossa hoquei","Iris","owner"),
        ("Preparar bossa hoquei","Roc","owner"),

        ("Assistir hoquei","Iris","owner"),
        ("Assistir hoquei","Roc","owner")
    ]


    for mission,user,atype in assignments:

        cursor.execute("""
        INSERT INTO mission_assignments
        (
        mission_id,
        user_id,
        assignment_type
        )
        VALUES (?,?,?)
        """,
        (
        mission_ids[mission],
        user_ids[user],
        atype
        ))


    # =========================
    # ACTIVITAT HOQUEI
    # =========================

    cursor.execute("""
    INSERT INTO activities
    (family_id,name,icon)
    VALUES (?,?,?)
    """,
    (
    family_id,
    "Hoquei",
    "🏑"
    ))

    hockey_id=cursor.lastrowid


    cursor.execute("""
    INSERT INTO activity_users
    VALUES (?,?)
    """,
    (hockey_id,user_ids["Iris"]))


    cursor.execute("""
    INSERT INTO activity_users
    VALUES (?,?)
    """,
    (hockey_id,user_ids["Roc"]))



    # =========================
    # RECOMPENSES
    # =========================

    rewards=[
        ("Escollir sopar",150),
        ("Gelat",200),
        ("Temps extra pantalla",300),
        ("Nit de cinema",400),
        ("Activitat especial",800)
    ]


    for name,cost in rewards:

        cursor.execute("""
        INSERT INTO rewards
        (family_id,name,points_required)
        VALUES (?,?,?)
        """,
        (family_id,name,cost))


        # Exemples d'assignacions amb estats predefinits
            # (mission_title, user_name, type, status)
        test_assignments = [
            ("Fer el llit", "Iris", "owner", "completed"),      # Ja feta
            ("Deures", "Iris", "owner", "pending"),             # Pendent
            ("Passejar gos", "Iris", "shared", "pending"),      # Disponible (compartida)
            ("Netejar fons piscina", "Roc", "team", "pending"), # Pendent
            ("Treure escombraries", "Roc", "shared", "pending") # Disponible
        ]

        for title, user, atype, status in test_assignments:
            cursor.execute("""
            INSERT INTO mission_assignments
            (mission_id, user_id, assignment_type, status)
            VALUES (?, ?, ?, ?)
            """, (mission_ids[title], user_ids[user], atype, status))

            
    conn.commit()
    conn.close()

    print("✅ Missions RoigAlvarez creada correctament")


if __name__=="__main__":
    seed()
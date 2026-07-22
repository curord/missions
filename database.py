import sqlite3
from pathlib import Path
from config import Config
from datetime import datetime
import logging
import os

DB_PATH = Path(Config.DATABASE)

# Determinar tipus de base de dades a partir d'entorn o config
DATABASE_URL = os.environ.get("DATABASE_URL") or getattr(Config, "DATABASE_URL", None)
IS_POSTGRES = DATABASE_URL and (DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"))


class PostgresCursorWrapper:
    """
    Wrapper per a cursors de PostgreSQL que proporciona compatibilitat amb SQLite (com 'lastrowid' i '?').
    """
    def __init__(self, real_cursor):
        self.cursor = real_cursor
        self._lastrowid = None

    def execute(self, sql, params=None):
        sql_upper = sql.strip().upper()
        is_insert = sql_upper.startswith("INSERT")

        # Convertir placeholders de ? a %s
        sql_prepared = sql.replace("?", "%s")

        if is_insert and "RETURNING" not in sql_upper:
            sql_prepared = sql_prepared.rstrip("; \n") + " RETURNING id"

        if params is not None:
            self.cursor.execute(sql_prepared, params)
        else:
            self.cursor.execute(sql_prepared)

        if is_insert:
            try:
                row = self.cursor.fetchone()
                if row:
                    self._lastrowid = row[0]
            except Exception:
                pass
        return self

    @property
    def lastrowid(self):
        return self._lastrowid

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def __iter__(self):
        return iter(self.cursor)

    def __getattr__(self, name):
        return getattr(self.cursor, name)


class PostgresConnectionWrapper:
    """
    Wrapper per a connexions de PostgreSQL que proporciona mètodes i gestió de context compatibles amb SQLite.
    """
    def __init__(self, real_conn):
        self.conn = real_conn

    def cursor(self, *args, **kwargs):
        import psycopg2.extras
        # Per defecte fem servir DictCursor per obtenir un comportament de tipus diccionari per a les files
        if "cursor_factory" not in kwargs:
            kwargs["cursor_factory"] = psycopg2.extras.DictCursor
        real_cursor = self.conn.cursor(*args, **kwargs)
        return PostgresCursorWrapper(real_cursor)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()


def init_database():
    """
    Comprova que existeix la carpeta data per a SQLite o valida la connexió de PostgreSQL.
    """
    if IS_POSTGRES:
        try:
            conn = get_connection()
            conn.close()
            logging.info("Connexió inicial amb PostgreSQL establerta correctament.")
        except Exception as e:
            logging.error("Error connectant amb PostgreSQL: %s", e)
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """
    Retorna una connexió activa adaptada (SQLite o PostgreSQL).
    """
    if IS_POSTGRES:
        import psycopg2
        real_conn = psycopg2.connect(DATABASE_URL)
        return PostgresConnectionWrapper(real_conn)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn


def query(sql, params=()):
    """
    SELECT que retorna una llista de diccionaris.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def query_one(sql, params=()):
    """
    SELECT que retorna un únic registre com a diccionari.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None


def execute(sql, params=()):
    """
    INSERT / UPDATE / DELETE. Retorna l'ID de la darrera fila inserida o modificada.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid


def _translate_sqlite_sql_to_postgres(sql):
    """
    Tradueix un script SQL de SQLite a PostgreSQL.
    """
    lines = []
    for line in sql.splitlines():
        if line.strip().upper().startswith("PRAGMA"):
            continue
        lines.append(line)
    sql = "\n".join(lines)
    sql = sql.replace("AUTOINCREMENT", "")
    sql = sql.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
    sql = sql.replace("DATETIME", "TIMESTAMP")
    return sql


def execute_script(filename):
    """
    Executa un fitxer SQL complet en lot.
    """
    filename = Path(filename)

    if not filename.is_absolute():
        filename = Path(Config.BASE_DIR) / filename

    with open(filename, "r", encoding="utf-8") as f:
        script = f.read()

    if IS_POSTGRES:
        script = _translate_sqlite_sql_to_postgres(script)
        with get_connection() as conn:
            import psycopg2
            real_cursor = conn.conn.cursor()
            real_cursor.execute(script)
    else:
        with get_connection() as conn:
            conn.executescript(script)


def ensure_reward_delivery_schema():
    """
    S'assegura que la taula rewards i reward_history tenen les columnes d'icona i auditoria de lliurament.
    """
    try:
        execute("ALTER TABLE rewards ADD COLUMN icon TEXT DEFAULT '🎁'")
    except Exception:
        pass

    try:
        execute("ALTER TABLE reward_history ADD COLUMN delivered_by INTEGER")
    except Exception:
        pass

    try:
        execute("ALTER TABLE reward_history ADD COLUMN delivered_at DATETIME")
    except Exception:
        pass

    try:
        execute("ALTER TABLE reward_history ADD COLUMN comment TEXT")
    except Exception:
        pass

# Executar automàticament al carregar la base de dades
try:
    ensure_reward_delivery_schema()
except Exception:
    pass


def table_exists(table_name):

    """
    Comprova si existeix una taula.
    """
    if IS_POSTGRES:
        sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = ?
        )
        """
        res = query_one(sql, (table_name,))
        return res is not None and list(res.values())[0]
    else:
        sql = """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """
        return query_one(sql, (table_name,)) is not None


def count(table_name):
    """
    Nombre de registres d'una taula.
    """
    sql = f"SELECT COUNT(*) AS total FROM {table_name}"
    row = query_one(sql)
    return row["total"]


def create_user(family_id, name, role, avatar="👤", favorite_color="#3b82f6"):
    return execute(
        """
        INSERT INTO users (family_id, name, role, avatar, favorite_color)
        VALUES (?, ?, ?, ?, ?)
        """,
        (family_id, name, role, avatar, favorite_color)
    )

def update_user(user_id, name, role, avatar="👤", favorite_color="#3b82f6"):
    execute(
        """
        UPDATE users
        SET name = ?, role = ?, avatar = ?, favorite_color = ?
        WHERE id = ?
        """,
        (name, role, avatar, favorite_color, user_id)
    )
    return True

def get_user(user_id):

    """
    Retorna un usuari.
    """
    return query_one(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )


def get_all_users():
    """
    Llista d'usuaris.
    """
    return query(
        """
        SELECT *
        FROM users
        ORDER BY role,name
        """
    )

def get_user_missions(user_id):

    return query(
        """
        SELECT

            ma.id AS assignment_id,

            ma.status,

            ma.assignment_type,

            ma.completed_by,

            ma.due_date,

            ma.assigned_date,

            m.id AS mission_id,

            m.title,

            m.description,

            m.icon,

            m.points,

            m.requires_validation,

            c.name AS category,

            c.color,

            c.icon AS category_icon,

            u.name AS completed_by_name


        FROM mission_assignments ma


        INNER JOIN missions m
            ON m.id = ma.mission_id


        INNER JOIN categories c
            ON c.id = m.category_id


        LEFT JOIN users u
            ON u.id = ma.completed_by


        WHERE ma.user_id = ?

          AND m.active = 1
          AND ma.status <> 'cancelled'


        ORDER BY
            CASE ma.status
                WHEN 'pending' THEN 1
                WHEN 'waiting_validation' THEN 2
                WHEN 'completed' THEN 3
                ELSE 4
            END,

            c.sort_order,

            m.title

        """,

        (user_id,)
    )

def start_mission(assignment_id, user_id):
    """
    Inicia una missió assignada passant el seu estat de 'pending' a 'in_progress'.
    """
    execute(
        """
        UPDATE mission_assignments
        SET status = 'in_progress'
        WHERE id = ? AND user_id = ? AND status = 'pending'
        """,
        (assignment_id, user_id)
    )
    return True

def complete_mission(assignment_id, user_id):
    execute(
        """
        UPDATE mission_assignments
        SET
            status=?,
            completed_at=?,
            completed_by=?
        WHERE id=?
          AND user_id=?
          AND status IN ('pending', 'in_progress', 'rejected')
        """,
        (
            "waiting_validation",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id,
            assignment_id,
            user_id
        )
    )


def retry_rejected_mission(assignment_id, user_id):
    """
    Torna una missió rebutjada a l'estat 'pending' per a poder-la reintentar.
    """
    execute(
        """
        UPDATE mission_assignments
        SET status = 'pending', comment = NULL
        WHERE id = ? AND user_id = ? AND status = 'rejected'
        """,
        (assignment_id, user_id)
    )
     
def get_waiting_validations():

    return query(
        """
        SELECT

            ma.id AS assignment_id,

            ma.status,

            ma.assignment_type,

            ma.completed_at,

            m.title as title,

            m.description,

            m.icon,

            m.points,

            c.name AS category,

            u.name AS gamer_name

        FROM mission_assignments ma

        INNER JOIN missions m
            ON m.id = ma.mission_id

        INNER JOIN categories c
            ON c.id = m.category_id

        INNER JOIN users u
            ON u.id = ma.user_id

        WHERE ma.status='waiting_validation'

        ORDER BY ma.completed_at
        """
    )
def approve_mission(assignment_id, admin_id):
    data = query_one(
        """
        SELECT
            ma.user_id,
            ma.mission_id,
            ma.assignment_type,
            COALESCE(m.points, 10) AS points,
            COALESCE(NULLIF(ma.coins, 0), COALESCE(m.points, 10) / 10) AS coins

        FROM mission_assignments ma
        JOIN missions m
            ON m.id = ma.mission_id
        WHERE ma.id = ?
          AND ma.status = 'waiting_validation'
        """,
        (assignment_id,)
    )


    if not data:
        return False

    execute(
        """
        UPDATE mission_assignments
        SET
            status='completed',
            validated_at=?,
            validated_by=?,
            coins=?,
            completed_points=?
        WHERE id=?
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            admin_id,
            int(data["coins"]),
            data["points"],
            assignment_id
        )
    )

    # Si la missió és de tipus Compartida, cancel·lar les assignacions dels altres membres
    if data.get("assignment_type") == "shared":
        execute(
            """
            UPDATE mission_assignments
            SET status = 'cancelled', comment = 'Completada per un altre membre de la família'
            WHERE mission_id = ? AND id <> ? AND status IN ('pending', 'waiting_validation')
            """,
            (data["mission_id"], assignment_id)
        )

    # Obtenir els punts actuals per actualitzar el nivell
    user_row = query_one("SELECT points FROM users WHERE id = ?", (data["user_id"],))
    current_points = user_row["points"] if user_row else 0
    new_points = current_points + data["points"]
    new_level = (new_points // 100) + 1

    execute(
        "UPDATE users SET points = ?, level = ? WHERE id = ?",
        (new_points, new_level, data["user_id"])
    )

    # Registrar a l'historial de punts
    execute(
        "INSERT INTO points_history (user_id, mission_id, points, reason) VALUES (?, ?, ?, ?)",
        (data["user_id"], data["mission_id"], data["points"], "Missió completada")
    )


    return True


def reject_mission(assignment_id, admin_id, comment=None):
    execute(
        """
        UPDATE mission_assignments
        SET
            status='rejected',
            comment=?,
            validated_at=?,
            validated_by=?
        WHERE id=?
        """,
        (
            comment,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            admin_id,
            assignment_id
        )
    )
    return True


def count_waiting_validations():

    row = query_one(
        """
        SELECT COUNT(*) AS total
        FROM mission_assignments
        WHERE status='waiting_validation'
        """
    )

    return row["total"]

# ==========================
# MISSIONS
# ==========================

def get_all_missions():
   
    return query(
        """
        SELECT

            m.*,

            c.name AS category_name,

            c.icon AS category_icon,

            c.color AS category_color,

            mt.name AS mission_type

        FROM missions m

        INNER JOIN categories c
            ON c.id = m.category_id

        LEFT JOIN mission_types mt
            ON mt.id = m.mission_type_id

        ORDER BY

            c.sort_order,

            m.title
        """
    )

def get_mission(mission_id):

    return query_one("""
        SELECT *
        FROM missions
        WHERE id = ?
    """, (mission_id,))

def get_categories():

    return query("""
        SELECT *
        FROM categories
        ORDER BY name
    """)


def get_family_users(family_id=1):

    return query("""
        SELECT *
        FROM users
        WHERE family_id = ?
        ORDER BY role DESC, name
    """, (family_id,))


def get_user_mission_history(user_id):
    """
    Retorna l'historial complet d'assignacions d'un usuari (aprovades, rebutjades i cancel·lades).
    """
    return query(
        """
        SELECT
            ma.id AS assignment_id,
            ma.status,
            ma.assignment_type,
            ma.completed_at,
            ma.validated_at,
            ma.comment,
            COALESCE(ma.coins, COALESCE(m.points, 10) / 10, 0) AS coins,
            COALESCE(ma.completed_points, m.points, 10) AS points,
            m.id AS mission_id,
            m.title,
            m.description,
            m.icon,
            c.name AS category,
            c.color,
            c.icon AS category_icon,
            u.name AS completed_by_name,
            v.name AS validated_by_name

        FROM mission_assignments ma
        INNER JOIN missions m
            ON m.id = ma.mission_id
        INNER JOIN categories c
            ON c.id = m.category_id
        LEFT JOIN users u
            ON u.id = ma.completed_by
        LEFT JOIN users v
            ON v.id = ma.validated_by
        WHERE ma.user_id = ?
          AND ma.status IN ('completed', 'rejected', 'cancelled')
        ORDER BY
            COALESCE(ma.validated_at, ma.completed_at, ma.assigned_date) DESC
        """,
        (user_id,)
    )

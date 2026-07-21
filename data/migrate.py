import sys
import os
from pathlib import Path

# Afegir directori arrel del projecte al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database

def migrate():
    """
    Executa totes les migracions pendents sobre la base de dades activa (SQLite o PostgreSQL).
    """
    # Inicialitza connexió / estructura
    database.init_database()

    # Crear taula de control de migracions si no existeix
    if not database.table_exists("schema_migrations"):
        if database.IS_POSTGRES:
            database.execute("""
            CREATE TABLE schema_migrations(
                filename VARCHAR(255) PRIMARY KEY,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        else:
            database.execute("""
            CREATE TABLE schema_migrations(
                filename TEXT PRIMARY KEY,
                executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)

    # Obtenir migracions ja aplicades
    rows = database.query("SELECT filename FROM schema_migrations")
    executed = {row["filename"] for row in rows}

    # Aplicar migracions pendents de la carpeta data/migrations
    migrations_dir = Path("data/migrations")
    for file in sorted(migrations_dir.glob("*.sql")):
        if file.name in executed:
            continue

        print(f"Applying {file.name}")
        database.execute_script(file)

        database.execute(
            "INSERT INTO schema_migrations(filename) VALUES(?)",
            (file.name,)
        )

    print("Done.")

if __name__ == "__main__":
    migrate()
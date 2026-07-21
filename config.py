import os
import secrets

def _get_persistent_secret_key(base_dir: str) -> str:
    key = os.environ.get("SECRET_KEY")
    if key:
        return key

    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("SECRET_KEY="):
                        return line.strip().split("=", 1)[1].strip()
        except Exception:
            pass

    new_key = secrets.token_hex(32)
    try:
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"\nSECRET_KEY={new_key}\n")
    except Exception:
        pass
    return new_key


class Config:
    """
    Configuració general de Missions
    """

    # Carpeta arrel del projecte
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Base de dades SQLite
    DATABASE = os.path.join(BASE_DIR, "data", "missions.db")

    # Clau de sessió de Flask
    SECRET_KEY = _get_persistent_secret_key(BASE_DIR)


    # Configuració Flask
    DEBUG = True

    # Configuració futura
    APP_NAME = "Missions"
    VERSION = "0.1.0"

    # Idioma
    LANGUAGE = "ca"

    # Zona horària
    TIMEZONE = "Europe/Madrid"

    # Gamificació
    DEFAULT_POINTS = 10

    # PWA (més endavant)
    PWA_NAME = "Missions"
    PWA_SHORT_NAME = "Missions"

    #password admin
    ADMIN_PIN = "9876"
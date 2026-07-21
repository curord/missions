from typing import List, Optional
import database
from models.user import User


class UserRepository:
    """
    Repositori per a gestionar les operacions de persistència d'usuaris.
    Utilitza exclusivament les funcions de database.py per interactuar amb la BD.
    """

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Recupera un usuari pel seu identificador.
        """
        user_row = database.get_user(user_id)
        if not user_row:
            return None
        return self._map_to_entity(user_row)

    def get_all(self) -> List[User]:
        """
        Recupera tots els usuaris ordénats per rol i nom.
        """
        user_rows = database.get_all_users()
        return [self._map_to_entity(row) for row in user_rows]

    def get_by_family_id(self, family_id: int = 1) -> List[User]:
        """
        Recupera tots els usuaris d'una família específica ordénats per rol i nom.
        """
        user_rows = database.get_family_users(family_id)
        return [self._map_to_entity(row) for row in user_rows]

    def _map_to_entity(self, row: dict) -> User:
        """
        Mapeja una fila de la base de dades (diccionari) a una entitat User.
        """
        # Extraiem camps que poden ser retornats de consultes o calculats
        return User(
            id=row.get("id"),
            family_id=row.get("family_id"),
            name=row.get("name"),
            role=row.get("role"),
            avatar=row.get("avatar"),
            favorite_color=row.get("favorite_color"),
            theme=row.get("theme", "default"),
            points=row.get("points", 0),
            level=row.get("level", 1),
            birthdate=row.get("birthdate"),
            last_login=row.get("last_login"),
            active=row.get("active", 1),
            created_at=row.get("created_at"),
            # Virtual fields with safe fallbacks
            streak=row.get("streak", 0),
            level_progress=row.get("level_progress", 0),
            coins=row.get("coins", 0)
        )

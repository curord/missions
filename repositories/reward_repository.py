from typing import List, Optional
import database
from models.reward import Reward


class RewardRepository:
    """
    Repositori per a gestionar operacions relacionades amb recompenses (rewards).
    Utilitza les funcions genèriques de consulta i execució de database.py.
    """

    def get_by_id(self, reward_id: int) -> Optional[Reward]:
        """
        Recupera una recompensa pel seu identificador.
        """
        row = database.query_one(
            """
            SELECT *
            FROM rewards
            WHERE id = ?
            """,
            (reward_id,)
        )
        if not row:
            return None
        return self._map_to_entity(row)

    def get_all(self) -> List[Reward]:
        """
        Recupera totes les recompenses ordenades per nom.
        """
        rows = database.query(
            """
            SELECT *
            FROM rewards
            ORDER BY name
            """
        )
        return [self._map_to_entity(row) for row in rows]

    def get_by_family_id(self, family_id: int = 1) -> List[Reward]:
        """
        Recupera totes les recompenses actives d'una família, ordenades pel cost en punts.
        """
        rows = database.query(
            """
            SELECT *
            FROM rewards
            WHERE family_id = ? AND active = 1
            ORDER BY points_required
            """,
            (family_id,)
        )
        return [self._map_to_entity(row) for row in rows]

    def create(self, reward: Reward) -> int:
        """
        Crea una nova recompensa a la base de dades i en retorna el nou ID.
        """
        new_id = database.execute(
            """
            INSERT INTO rewards (family_id, name, description, points_required, active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                reward.family_id,
                reward.name,
                reward.description,
                reward.points_required,
                reward.active
            )
        )
        reward.id = new_id
        return new_id

    def update(self, reward: Reward) -> None:
        """
        Actualitza les dades d'una recompensa existent.
        """
        if not reward.id:
            raise ValueError("No es pot actualitzar una recompensa sense ID.")
        database.execute(
            """
            UPDATE rewards
            SET name = ?, description = ?, points_required = ?, active = ?
            WHERE id = ?
            """,
            (
                reward.name,
                reward.description,
                reward.points_required,
                reward.active,
                reward.id
            )
        )

    def _map_to_entity(self, row: dict) -> Reward:
        """
        Mapeja un diccionari de la base de dades a una entitat Reward.
        """
        return Reward(
            id=row.get("id"),
            family_id=row.get("family_id"),
            name=row.get("name"),
            description=row.get("description"),
            points_required=row.get("points_required"),
            active=row.get("active", 1)
        )

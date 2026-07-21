from typing import List, Optional
from datetime import datetime
import database
from models.reward import Reward
from repositories.reward_repository import RewardRepository



class RewardService:
    """
    Servei per a centralitzar la lògica de negoci associada a les recompenses (rewards).
    """

    def __init__(self, reward_repository: Optional[RewardRepository] = None):
        self.reward_repo = reward_repository or RewardRepository()

    def get_reward_by_id(self, reward_id: int) -> Optional[Reward]:
        """
        Obté una recompensa pel seu identificador.
        """
        return self.reward_repo.get_by_id(reward_id)

    def get_all_rewards(self) -> List[Reward]:
        """
        Obté totes les recompenses ordenades pel nom.
        """
        return self.reward_repo.get_all()

    def get_rewards_by_family(self, family_id: int = 1) -> List[Reward]:
        """
        Obté totes les recompenses actives d'una família, ordenades per cost de punts.
        """
        return self.reward_repo.get_by_family_id(family_id)

    def create_reward(self, reward: Reward) -> int:
        """
        Crea una nova recompensa i en retorna l'ID assignat.
        """
        return self.reward_repo.create(reward)

    def update_reward(self, reward: Reward) -> None:
        """
        Actualitza una recompensa existent.
        """
        self.reward_repo.update(reward)

    def disable_reward(self, reward_id: int) -> None:
        """
        Marca una recompensa com a inactiva.
        """
        self.reward_repo.disable(reward_id)

    def buy_reward(self, user_id: int, reward_id: int) -> bool:
        """
        Realitza la compra d'una recompensa per part d'un usuari.
        Verifica saldo suficient, descompta el cost i registra la compra a l'historial.
        """
        reward = self.reward_repo.get_by_id(reward_id)
        if not reward or not reward.active:
            return False

        from services.user_service import UserService
        user_service = UserService()
        user = user_service.get_user_by_id(user_id)
        if not user:
            return False

        # Comprovar si té saldo suficient (monedes)
        if user.coins < reward.points_required:
            return False

        # Registrar compra a l'historial
        database.execute(
            """
            INSERT INTO reward_history (reward_id, user_id, requested_at, approved, delivered)
            VALUES (?, ?, ?, 1, 1)
            """,
            (reward_id, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        return True

    def get_user_reward_history(self, user_id: int) -> List[dict]:
        """
        Retorna l'historial de recompenses comprades per un nen, amb data de compra.
        """
        rows = database.query(
            """
            SELECT rh.id, rh.requested_at, r.name, r.points_required AS cost
            FROM reward_history rh
            JOIN rewards r ON r.id = rh.reward_id
            WHERE rh.user_id = ?
            ORDER BY rh.requested_at DESC
            """,
            (user_id,)
        )
        
        # Formatar la data
        for r in rows:
            if r.get("requested_at"):
                try:
                    dt = datetime.strptime(r["requested_at"], "%Y-%m-%d %H:%M:%S")
                    r["formatted_date"] = dt.strftime("%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    r["formatted_date"] = r["requested_at"]
            else:
                r["formatted_date"] = "No disponible"
        return rows


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

        # Registrar compra a l'historial segons la configuració familiar de lliurament
        from services.family_config_service import FamilyConfigService
        config = FamilyConfigService().get_config(user.family_id if user else 1)
        delivered_status = 0 if config.rewards_require_delivery else 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        database.execute(
            """
            INSERT INTO reward_history (reward_id, user_id, requested_at, approved, delivered, delivered_at)
            VALUES (?, ?, ?, 1, ?, ?)
            """,
            (reward_id, user_id, now_str, delivered_status, now_str if delivered_status == 1 else None)
        )
        return True

    def get_user_reward_history(self, user_id: int) -> List[dict]:
        """
        Retorna l'historial complet de recompenses sol·licitades per un usuari, auditant lliuraments.
        """
        rows = database.query(
            """
            SELECT 
                rh.id, 
                rh.requested_at, 
                rh.delivered, 
                rh.delivered_at, 
                rh.comment, 
                r.name, 
                COALESCE(r.icon, '🎁') AS icon, 
                r.points_required AS cost,
                v.name AS delivered_by_name
            FROM reward_history rh
            JOIN rewards r ON r.id = rh.reward_id
            LEFT JOIN users v ON v.id = rh.delivered_by
            WHERE rh.user_id = ?
            ORDER BY rh.requested_at DESC
            """,
            (user_id,)
        )
        
        for r in rows:
            if r.get("requested_at"):
                try:
                    dt = datetime.strptime(r["requested_at"], "%Y-%m-%d %H:%M:%S")
                    r["formatted_date"] = dt.strftime("%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    r["formatted_date"] = r["requested_at"]
            else:
                r["formatted_date"] = "No disponible"

            if r.get("delivered_at"):
                try:
                    dt_del = datetime.strptime(r["delivered_at"], "%Y-%m-%d %H:%M:%S")
                    r["formatted_delivered_date"] = dt_del.strftime("%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    r["formatted_delivered_date"] = r["delivered_at"]

        return rows

    def get_pending_deliveries_count(self, family_id: int = 1) -> int:
        """
        Retorna el recompte de recompenses compreses pendents de lliurar (delivered = 0).
        """
        row = database.query_one(
            """
            SELECT COUNT(*) AS total
            FROM reward_history rh
            JOIN rewards r ON r.id = rh.reward_id
            WHERE r.family_id = ? AND rh.delivered = 0
            """,
            (family_id,)
        )
        return row["total"] if row else 0

    def get_pending_deliveries(self, family_id: int = 1) -> List[dict]:
        """
        Llista de recompenses pendents de lliurament físic per a la família.
        """
        rows = database.query(
            """
            SELECT 
                rh.id, 
                rh.requested_at, 
                r.name AS reward_name, 
                COALESCE(r.icon, '🎁') AS reward_icon, 
                r.points_required AS cost, 
                u.name AS gamer_name, 
                u.avatar
            FROM reward_history rh
            JOIN rewards r ON r.id = rh.reward_id
            JOIN users u ON u.id = rh.user_id
            WHERE r.family_id = ? AND rh.delivered = 0
            ORDER BY rh.requested_at DESC
            """,
            (family_id,)
        )
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

    def deliver_reward(self, reward_history_id: int, admin_id: Optional[int] = None, comment: Optional[str] = None) -> bool:
        """
        Marca una recompensa com a lliurada físicament (delivered = 1) auditant l'administrador i la data.
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        database.execute(
            """
            UPDATE reward_history
            SET delivered = 1, delivered_by = ?, delivered_at = ?, comment = ?
            WHERE id = ?
            """,
            (admin_id, now_str, comment, reward_history_id)
        )
        return True





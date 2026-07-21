from typing import List, Optional
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

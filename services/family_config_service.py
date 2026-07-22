from typing import Optional
from models.family_config import FamilyConfig
from repositories.family_config_repository import FamilyConfigRepository


class FamilyConfigService:
    """
    Servei per a la gestió de la lògica de negoci de la configuració familiar.
    """

    def __init__(self, config_repository: Optional[FamilyConfigRepository] = None):
        self.config_repo = config_repository or FamilyConfigRepository()

    def get_config(self, family_id: int = 1) -> FamilyConfig:
        """
        Retorna la configuració per a una família. Si no existeix a la BD,
        la inicialitza amb els valors per defecte i la desa.
        """
        config = self.config_repo.get_by_family_id(family_id)
        if not config:
            config = FamilyConfig(family_id=family_id)
            config = self.config_repo.save(config)
        return config

    def update_config(
        self,
        family_id: int,
        auto_approve_admin_missions: bool,
        rewards_require_delivery: bool,
        count_weekends_streaks: bool,
        admin_validation_mode: str = "admin_only"
    ) -> FamilyConfig:
        """
        Actualitza els paràmetres de configuració d'una família.
        """
        config = FamilyConfig(
            family_id=family_id,
            auto_approve_admin_missions=auto_approve_admin_missions,
            rewards_require_delivery=rewards_require_delivery,
            count_weekends_streaks=count_weekends_streaks,
            admin_validation_mode=admin_validation_mode
        )
        return self.config_repo.save(config)


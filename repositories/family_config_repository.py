from typing import Optional
import database
from models.family_config import FamilyConfig


class FamilyConfigRepository:
    """
    Repositori per a la gestió de la configuració familiar a la base de dades.
    """

    def get_by_family_id(self, family_id: int) -> Optional[FamilyConfig]:
        """
        Recupera la configuració d'una família per la seva ID.
        """
        row = database.query_one(
            """
            SELECT family_id, auto_approve_admin_missions, rewards_require_delivery, count_weekends_streaks, admin_validation_mode, updated_at
            FROM family_config
            WHERE family_id = ?
            """,
            (family_id,)
        )
        if not row:
            return None
        return self._map_to_entity(row)

    def save(self, config: FamilyConfig) -> FamilyConfig:
        """
        Guarda o actualitza la configuració familiar a la base de dades.
        """
        existing = database.query_one(
            "SELECT family_id FROM family_config WHERE family_id = ?",
            (config.family_id,)
        )

        auto_approve = 1 if config.auto_approve_admin_missions else 0
        rewards_req = 1 if config.rewards_require_delivery else 0
        count_weekends = 1 if config.count_weekends_streaks else 0
        val_mode = config.admin_validation_mode or "admin_only"

        if existing:
            database.execute(
                """
                UPDATE family_config
                SET auto_approve_admin_missions = ?,
                    rewards_require_delivery = ?,
                    count_weekends_streaks = ?,
                    admin_validation_mode = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE family_id = ?
                """,
                (auto_approve, rewards_req, count_weekends, val_mode, config.family_id)
            )
        else:
            database.execute(
                """
                INSERT INTO family_config (family_id, auto_approve_admin_missions, rewards_require_delivery, count_weekends_streaks, admin_validation_mode)
                VALUES (?, ?, ?, ?, ?)
                """,
                (config.family_id, auto_approve, rewards_req, count_weekends, val_mode)
            )

        return self.get_by_family_id(config.family_id) or config

    def _map_to_entity(self, row: dict) -> FamilyConfig:
        """
        Mapeja una fila de la base de dades a una entitat FamilyConfig.
        """
        return FamilyConfig(
            family_id=row["family_id"],
            auto_approve_admin_missions=bool(row.get("auto_approve_admin_missions", 0)),
            rewards_require_delivery=bool(row.get("rewards_require_delivery", 1)),
            count_weekends_streaks=bool(row.get("count_weekends_streaks", 1)),
            admin_validation_mode=row.get("admin_validation_mode", "admin_only") or "admin_only",
            updated_at=row.get("updated_at")
        )


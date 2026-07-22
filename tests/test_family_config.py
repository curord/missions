import sys
import os

# Afegeix la ruta del projecte
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from services.family_config_service import FamilyConfigService
from repositories.family_config_repository import FamilyConfigRepository
from models.family_config import FamilyConfig


def test_family_config_repository_and_service():
    service = FamilyConfigService()
    repo = FamilyConfigRepository()
    
    # Crear una família temporal de prova
    family_id = database.execute("INSERT INTO families (name) VALUES ('Família Test')")

    try:
        # 1. Comprovar la lectura de la configuració per defecte (get_config crea un registre si no existeix)
        config = service.get_config(family_id)
        assert config is not None
        assert config.family_id == family_id
        assert config.auto_approve_admin_missions is False
        assert config.rewards_require_delivery is True
        assert config.count_weekends_streaks is True
        print("1. Configuració inicial creada amb valors per defecte.")

        # 2. Actualitzar els paràmetres de configuració
        updated = service.update_config(
            family_id=family_id,
            auto_approve_admin_missions=True,
            rewards_require_delivery=False,
            count_weekends_streaks=False
        )
        assert updated.auto_approve_admin_missions is True
        assert updated.rewards_require_delivery is False
        assert updated.count_weekends_streaks is False
        print("2. Configuració actualitzada correctament via Service.")

        # 3. Llegir directament del repositori per verificar la persistència a la BD
        from_db = repo.get_by_family_id(family_id)
        assert from_db is not None
        assert from_db.auto_approve_admin_missions is True
        assert from_db.rewards_require_delivery is False
        assert from_db.count_weekends_streaks is False
        print("3. Persistència verificada a la BD via Repository.")

        print("SUCCESS: Proves de FamilyConfig superades amb èxit!")

    finally:
        # Neteja de la base de dades
        if family_id:
            database.execute("DELETE FROM family_config WHERE family_id = ?", (family_id,))
            database.execute("DELETE FROM families WHERE id = ?", (family_id,))
            print("Neteja de la prova de FamilyConfig completada.")



if __name__ == "__main__":
    test_family_config_repository_and_service()

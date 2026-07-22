import sys
import os

# Afegeix la ruta del projecte
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mission_service import MissionService
from services.user_service import UserService


def test_history_loading():
    user_service = UserService()
    mission_service = MissionService()

    users = user_service.get_all_users()
    assert len(users) > 0

    for user in users:
        history = mission_service.get_user_mission_history(user.id)
        assert isinstance(history, list)
        print(f"[OK] Historial de {user.name} carregat correctament ({len(history)} elements).")

    print("\nSUCCESS: Pàgina d'historial provada sense cap error SQL!")


if __name__ == "__main__":
    test_history_loading()

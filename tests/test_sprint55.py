import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from services.user_service import UserService
from services.mission_service import MissionService


def test_sprint55_features():
    print("\n--- TEST SPRINT 5.5: Gestió d'Usuaris, En Curs i Esborranys ---")
    user_service = UserService()
    mission_service = MissionService()

    # 1. Creació i actualització d'usuari
    user_id = user_service.create_user(family_id=1, name="Usuari Test Sprint 5.5", role="child", avatar="🚀")
    assert user_id > 0

    u = user_service.get_user_by_id(user_id)
    assert u.name == "Usuari Test Sprint 5.5"
    assert u.avatar == "🚀"
    print("[OK] Creació d'usuari verificada correctament.")

    user_service.update_user(user_id, name="Usuari Editat", role="child", avatar="🦄")
    u_edited = user_service.get_user_by_id(user_id)
    assert u_edited.name == "Usuari Editat"
    assert u_edited.avatar == "🦄"
    print("[OK] Actualització d'usuari verificada correctament.")

    # 2. Estat "En curs" (in_progress)
    mission_id = database.execute(
        "INSERT INTO missions (family_id, category_id, title, points, active) VALUES (1, 1, 'Missió Sprint 5.5', 15, 1)"
    )
    assignment_id = database.execute(
        "INSERT INTO mission_assignments (mission_id, user_id, status) VALUES (?, ?, 'pending')",
        (mission_id, user_id)
    )

    mission_service.start_mission(assignment_id, user_id)
    row = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (assignment_id,))
    assert row["status"] == "in_progress"
    print("[OK] Transició a l'estat 'in_progress' (En Curs) verificada correctament.")

    mission_service.complete_mission(assignment_id, user_id)
    row = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (assignment_id,))
    assert row["status"] == "waiting_validation"
    print("[OK] Transició de 'in_progress' a 'waiting_validation' verificada correctament.")

    # Neteja de dades de la prova
    database.execute("DELETE FROM mission_assignments WHERE id = ?", (assignment_id,))
    database.execute("DELETE FROM missions WHERE id = ?", (mission_id,))
    database.execute("DELETE FROM users WHERE id = ?", (user_id,))

    print("\nALL SPRINT 5.5 TODO TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_sprint55_features()

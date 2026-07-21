import sys
import os

# Afegeix la ruta del projecte
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from services.user_service import UserService
from services.mission_service import MissionService

def test_full_mission_flow():
    user_service = UserService()
    mission_service = MissionService()

    # Usuari de prova: Iris (id=3, child)
    user_id = 3
    # Administrador per a validació: Laura (id=1, admin)
    admin_id = 1
    # Missió de prova: "Fer el llit" (id=1, points=10)
    mission_id = 1
    mission_points = 10

    # 1. Recuperar l'usuari inicial i desar els seus punts
    user_before = user_service.get_user_by_id(user_id)
    assert user_before is not None
    initial_points = user_before.points
    print(f"Punts inicials de {user_before.name}: {initial_points}")

    assignment_id = None
    try:
        # 2. ASSIGNAR la missió
        assignment_id = mission_service.assign_mission(mission_id, user_id, "owner")
        assert assignment_id is not None
        print(f"1. ASSIGNAR: Creada assignació {assignment_id} amb estat 'pending'")

        # Comprovar estat a la base de dades
        res = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (assignment_id,))
        assert res is not None
        assert res["status"] == "pending"

        # 3. COMPLETAR la missió (el nen la marca com a feta)
        mission_service.complete_mission(assignment_id, user_id)
        print("2. COMPLETAR: Missió marcada com a completa, esperant validació")

        # Comprovar estat a la base de dades
        res = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (assignment_id,))
        assert res is not None
        assert res["status"] == "waiting_validation"

        # 4. VALIDAR (APROVAR) la missió (el pare aprova)
        success = mission_service.approve_mission(assignment_id, admin_id)
        assert success is True
        print("3. VALIDAR: Missió aprovada per l'administrador")

        # Comprovar estat final a la base de dades
        res = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (assignment_id,))
        assert res is not None
        assert res["status"] == "completed"

        # 5. Comprovar l'augment de punts de l'usuari
        user_after = user_service.get_user_by_id(user_id)
        assert user_after.points == initial_points + mission_points
        print(f"Punts finals de {user_after.name}: {user_after.points} (Guanyat: +{mission_points} XP)")

        print("SUCCESS: El flux complet d'assignació, completat i aprovació ha funcionat correctament!")

    finally:
        # 6. NETEJA: Restablir la base de dades a l'estat original (sense efectes secundaris)
        print("Netejant dades de la prova de flux...")
        if assignment_id:
            # Eliminar l'assignació
            database.execute("DELETE FROM mission_assignments WHERE id = ?", (assignment_id,))
            # Eliminar historial de punts
            database.execute("DELETE FROM points_history WHERE user_id = ? AND mission_id = ?", (user_id, mission_id))
            # Restablir els punts de l'usuari
            database.execute("UPDATE users SET points = ? WHERE id = ?", (initial_points, user_id))
            print("Base de dades netejada correctament.")


def test_mission_crud():
    mission_service = MissionService()

    # Dades de prova de creació de missió
    new_mission_data = {
        "category_id": 1,
        "title": "Netejar el cotxe",
        "description": "Netejar cotxe familiar amb aigua i sabó",
        "icon": "🚗",
        "difficulty": 3,
        "points": 50,
        "coins": 5,
        "requires_validation": "on",
        "active": "on"
    }

    mission_id = None
    try:
        # 1. CREAR la plantilla de missió
        mission_id = mission_service.create_mission(new_mission_data, family_id=1)
        assert mission_id is not None
        print(f"Missió creada amb èxit, ID: {mission_id}")

        # 2. LLEGIR per comprovar valors
        m = mission_service.get_mission_by_id(mission_id)
        assert m is not None
        assert m.title == "Netejar el cotxe"
        assert m.points == 50
        assert m.requires_validation == 1
        assert m.active == 1

        # 3. ACTUALITZAR la plantilla de missió
        updated_data = {
            "category_id": 1,
            "title": "Netejar el cotxe (Actualitzat)",
            "description": "Netejar cotxe familiar i interior",
            "icon": "🏎️",
            "difficulty": 4,
            "points": 60,
            "requires_validation": "on",
            "active": "on"
        }
        mission_service.update_mission(mission_id, updated_data)
        print(f"Missió {mission_id} actualitzada.")

        # 4. LLEGIR per comprovar valors actualitzats
        m_up = mission_service.get_mission_by_id(mission_id)
        assert m_up.title == "Netejar el cotxe (Actualitzat)"
        assert m_up.points == 60
        assert m_up.difficulty == 4
        assert m_up.icon == "🏎️"
        print("SUCCESS: Proves de creació, lectura i actualització de missions superades!")


    finally:
        # 5. NETEJA: Eliminar la missió de prova
        if mission_id:
            database.execute("DELETE FROM missions WHERE id = ?", (mission_id,))
            print("Missió de prova de creació/actualització eliminada.")


if __name__ == "__main__":
    test_full_mission_flow()
    test_mission_crud()

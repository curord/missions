import sys
import os

# Afegeix la ruta del projecte
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from services.user_service import UserService
from services.mission_service import MissionService
from services.reward_service import RewardService


def test_refactoring_suite():
    print("\n--- TEST 1: Reintent de missions rebutjades ---")
    user_service = UserService()
    mission_service = MissionService()
    reward_service = RewardService()

    # Obtenir usuaris de prova
    users = user_service.get_family_users(1)
    gamer = users[0]
    admin = [u for u in users if u.role == "admin"][0]

    # Crear una assignació de prova
    mission_id = database.execute(
        "INSERT INTO missions (family_id, category_id, title, points) VALUES (1, 1, 'Missió Test Reintent', 20)"
    )
    assignment_id = database.execute(
        "INSERT INTO mission_assignments (mission_id, user_id, status) VALUES (?, ?, 'pending')",
        (mission_id, gamer.id)
    )

    # 1. Completar
    mission_service.complete_mission(assignment_id, gamer.id)
    row = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (assignment_id,))
    assert row["status"] == "waiting_validation"
    print("[OK] Completada correctament -> waiting_validation")

    # 2. Rebutjar
    mission_service.reject_mission(assignment_id, "Falta netejar el racó", admin_id=admin.id)
    row = database.query_one("SELECT status, comment, validated_by FROM mission_assignments WHERE id = ?", (assignment_id,))
    assert row["status"] == "rejected"
    assert row["comment"] == "Falta netejar el racó"
    assert row["validated_by"] == admin.id
    print("[OK] Rebutjada correctament -> status='rejected', comentari i validador deats")

    # 3. Reintentar (Revertir a pending)
    mission_service.retry_rejected_mission(assignment_id, gamer.id)
    row = database.query_one("SELECT status, comment FROM mission_assignments WHERE id = ?", (assignment_id,))
    assert row["status"] == "pending"
    assert row["comment"] is None
    print("[OK] Reintentat -> Tornada a status='pending' sense comentari")

    # 4. Tornar a completar i aprovar
    mission_service.complete_mission(assignment_id, gamer.id)
    mission_service.approve_mission(assignment_id, admin.id)
    row = database.query_one("SELECT status, validated_by FROM mission_assignments WHERE id = ?", (assignment_id,))
    assert row["status"] == "completed"
    print("[OK] Aprovada finalment -> status='completed'")

    # Verificar que el nom del validador apareix a l'historial
    history = mission_service.get_user_mission_history(gamer.id)
    matched = [h for h in history if h["assignment_id"] == assignment_id]
    assert len(matched) == 1
    assert matched[0]["validated_by_name"] == admin.name
    print(f"[OK] Nom del validador a l'historial verificat: {matched[0]['validated_by_name']}")

    print("\n--- TEST 2: Missions Compartides (Shared Missions) ---")
    gamer2 = users[1] if len(users) > 1 else gamer
    shared_mission_id = database.execute(
        "INSERT INTO missions (family_id, category_id, title, points) VALUES (1, 1, 'Missió Compartida Test', 30)"
    )
    as1 = database.execute(
        "INSERT INTO mission_assignments (mission_id, user_id, status, assignment_type) VALUES (?, ?, 'pending', 'shared')",
        (shared_mission_id, gamer.id)
    )
    as2 = database.execute(
        "INSERT INTO mission_assignments (mission_id, user_id, status, assignment_type) VALUES (?, ?, 'pending', 'shared')",
        (shared_mission_id, gamer2.id)
    )

    # Gamer 1 la completa i l'admin l'aprova
    mission_service.complete_mission(as1, gamer.id)
    mission_service.approve_mission(as1, admin.id)

    row1 = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (as1,))
    row2 = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (as2,))
    assert row1["status"] == "completed"
    assert row2["status"] == "cancelled"
    print("[OK] Missió compartida aprovada per Gamer 1 -> Gamer 2 cancel·lada automàticament!")

    print("\n--- TEST 3: Lliurament Físic de Recompenses ---")
    reward_id = database.execute(
        "INSERT INTO rewards (family_id, name, points_required, active) VALUES (1, 'Sopar Especial', 10, 1)"
    )
    rh_id = database.execute(
        "INSERT INTO reward_history (reward_id, user_id, requested_at, approved, delivered) VALUES (?, ?, '2026-07-22 18:00:00', 1, 0)",
        (reward_id, gamer.id)
    )

    pending_count_before = reward_service.get_pending_deliveries_count(1)
    assert pending_count_before >= 1

    reward_service.deliver_reward(rh_id)
    row_rh = database.query_one("SELECT delivered FROM reward_history WHERE id = ?", (rh_id,))
    assert row_rh["delivered"] == 1
    print("[OK] Recompensa marcada com a lliurada físicament (delivered = 1)!")

    # Neteja de dades de la prova
    database.execute("DELETE FROM points_history WHERE mission_id IN (?, ?)", (mission_id, shared_mission_id))
    database.execute("DELETE FROM mission_assignments WHERE id IN (?, ?, ?)", (assignment_id, as1, as2))
    database.execute("DELETE FROM missions WHERE id IN (?, ?)", (mission_id, shared_mission_id))
    database.execute("DELETE FROM reward_history WHERE id = ?", (rh_id,))
    database.execute("DELETE FROM rewards WHERE id = ?", (reward_id,))


    print("\nALL REFACTORING TESTS PASSED 100% CLEANLY!")


if __name__ == "__main__":
    test_refactoring_suite()

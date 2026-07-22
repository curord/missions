import sys
import os

# Afegeix la ruta del projecte
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from services.user_service import UserService
from services.mission_service import MissionService
from services.family_config_service import FamilyConfigService


def test_admin_validation_scenarios():
    user_service = UserService()
    mission_service = MissionService()
    config_service = FamilyConfigService()

    # Usuaris de prova existents a seed:
    # id=1: Laura (admin, family_id=1)
    # id=2: Marc (admin, family_id=1)
    # id=3: Iris (child, family_id=1)
    admin1 = user_service.get_user_by_id(1)
    admin2 = user_service.get_user_by_id(2)
    gamer = user_service.get_user_by_id(3)

    assert admin1 is not None and admin2 is not None and gamer is not None

    family_id = admin1.family_id
    initial_admin1_points = admin1.points

    # Crear una plantilla de missió de prova
    mission_id = database.execute(
        """
        INSERT INTO missions (family_id, category_id, title, points, active)
        VALUES (?, 1, 'Missió Test Admin', 25, 1)
        """,
        (family_id,)
    )


    try:
        # =========================================================================
        # PROVA 1: auto_approve_admin_missions = True
        # =========================================================================
        print("\n--- TEST 1: Autoaprovar activat ---")
        config_service.update_config(
            family_id=family_id,
            auto_approve_admin_missions=True,
            rewards_require_delivery=True,
            count_weekends_streaks=True,
            admin_validation_mode="admin_only"
        )

        assign_id_1 = mission_service.assign_mission(mission_id, admin1.id)
        mission_service.complete_mission(assign_id_1, admin1.id)

        # Ha d'haver passat a estat 'completed' automàticament
        row_1 = database.query_one("SELECT status, validated_by FROM mission_assignments WHERE id = ?", (assign_id_1,))
        assert row_1["status"] == "completed"
        assert row_1["validated_by"] == admin1.id
        print("[OK] Missio autoaprovada immediatament per a l'administrador.")


        # =========================================================================
        # PROVA 2: auto_approve_admin_missions = False, admin_validation_mode = 'admin_only'
        # =========================================================================
        print("\n--- TEST 2: Autoaprovar deshabilitat, Mode 'admin_only' ---")
        config_service.update_config(
            family_id=family_id,
            auto_approve_admin_missions=False,
            rewards_require_delivery=True,
            count_weekends_streaks=True,
            admin_validation_mode="admin_only"
        )

        assign_id_2 = mission_service.assign_mission(mission_id, admin1.id)
        mission_service.complete_mission(assign_id_2, admin1.id)

        # En completar, ha de quedar en 'waiting_validation'
        row_2 = database.query_one("SELECT status FROM mission_assignments WHERE id = ?", (assign_id_2,))
        assert row_2["status"] == "waiting_validation"
        print("[OK] Missio de l'admin queda en 'waiting_validation'.")

        # Comprovar permisos de validació:
        assign_obj_2 = mission_service.mission_repo._map_to_assignment(
            database.query_one("SELECT * FROM mission_assignments WHERE id = ?", (assign_id_2,))
        )

        # El mateix admin no es pot validar a ell mateix
        assert mission_service.can_user_validate_assignment(admin1, assign_obj_2) is False
        # El gamer (nen) NO pot validar si el mode és 'admin_only'
        assert mission_service.can_user_validate_assignment(gamer, assign_obj_2) is False
        # Un altre admin SI pot validar
        assert mission_service.can_user_validate_assignment(admin2, assign_obj_2) is True
        print("[OK] Permisos de validacio correctes per al mode 'admin_only'.")

        # Admin2 aprova la missió
        success = mission_service.approve_mission(assign_id_2, admin2.id)
        assert success is True
        row_2_after = database.query_one("SELECT status, validated_by FROM mission_assignments WHERE id = ?", (assign_id_2,))
        assert row_2_after["status"] == "completed"
        assert row_2_after["validated_by"] == admin2.id
        print("[OK] Missio aprovada correctament per un altre administrador.")

        # =========================================================================
        # PROVA 3: auto_approve_admin_missions = False, admin_validation_mode = 'authorized_gamers'
        # =========================================================================
        print("\n--- TEST 3: Mode 'authorized_gamers' (Gamer valida l'admin) ---")
        config_service.update_config(
            family_id=family_id,
            auto_approve_admin_missions=False,
            rewards_require_delivery=True,
            count_weekends_streaks=True,
            admin_validation_mode="authorized_gamers"
        )

        assign_id_3 = mission_service.assign_mission(mission_id, admin1.id)
        mission_service.complete_mission(assign_id_3, admin1.id)

        assign_obj_3 = mission_service.mission_repo._map_to_assignment(
            database.query_one("SELECT * FROM mission_assignments WHERE id = ?", (assign_id_3,))
        )

        # El Gamer ara SI té permís per a validar la missió de l'admin
        assert mission_service.can_user_validate_assignment(gamer, assign_obj_3) is True
        print("[OK] Gamer autoritzat te permis per a validar la missio de l'administrador.")

        # El Gamer executa l'aprovació de la missió de l'admin
        success_gamer = mission_service.approve_mission(assign_id_3, gamer.id)
        assert success_gamer is True

        row_3_after = database.query_one("SELECT status, validated_by FROM mission_assignments WHERE id = ?", (assign_id_3,))
        assert row_3_after["status"] == "completed"
        assert row_3_after["validated_by"] == gamer.id
        print("[OK] Missio de l'administrador aprovada pel Gamer autoritzat! (validated_by = Gamer ID)")

        # Comprovar augment de punts d'Admin1 (Owner de la missió)
        admin1_updated = user_service.get_user_by_id(admin1.id)
        expected_points = initial_admin1_points + (25 * 3)  # 3 missions aprovades de 25 punts
        assert admin1_updated.points == expected_points
        print(f"[OK] Punts totals d'Admin1 actualitzats correctament (+75 XP = {admin1_updated.points} XP).")


        print("\nALL TESTS PASSED SUCCESSFULLY!")

    finally:
        # Neteja de les dades de prova
        print("Netejant dades de la prova...")
        database.execute("DELETE FROM points_history WHERE user_id = ?", (admin1.id,))
        database.execute("DELETE FROM mission_assignments WHERE mission_id = ?", (mission_id,))
        database.execute("DELETE FROM missions WHERE id = ?", (mission_id,))
        database.execute("UPDATE users SET points = ? WHERE id = ?", (initial_admin1_points, admin1.id))
        print("Neteja completada.")


if __name__ == "__main__":
    test_admin_validation_scenarios()

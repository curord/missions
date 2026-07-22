import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from models.reward import Reward
from services.user_service import UserService
from services.reward_service import RewardService


def test_rewards_sprint56():
    print("\n--- TEST SPRINT 5.6: Cicle de Vida Complet de Recompenses ---")
    user_service = UserService()
    reward_service = RewardService()

    # Obtenir usuaris de prova
    users = user_service.get_family_users(1)
    gamer = [u for u in users if u.role == "child"][0]
    admin = [u for u in users if u.role == "admin"][0]

    # Donar monedes inicials al gamer per a la prova
    initial_coins = gamer.coins
    # Simular aprovació d'una missió amb punts per augmentar monedes
    mission_id = database.execute(
        "INSERT INTO missions (family_id, category_id, title, points) VALUES (1, 1, 'Missió Monedes Test', 50)"
    )
    as_id = database.execute(
        "INSERT INTO mission_assignments (mission_id, user_id, status, coins, completed_points) VALUES (?, ?, 'waiting_validation', 10, 100)",
        (mission_id, gamer.id)
    )
    database.approve_mission(as_id, admin.id)

    gamer_updated = user_service.get_user_by_id(gamer.id)
    print(f"[OK] Monedes disponibles del Gamer: {gamer_updated.coins} (Abans: {initial_coins})")

    # 1. Creació de recompensa amb icona
    reward = Reward(
        family_id=1,
        name="Cinema i Palometes",
        description="Una tarda de cinema en família",
        points_required=5,
        icon="🍿",
        active=1
    )
    reward_id = reward_service.create_reward(reward)
    assert reward_id > 0
    print(f"[OK] Recompensa creada amb ID {reward_id} i icona de cinema")


    # 2. Bescanvi de recompensa (Redeem)
    coins_before_buy = user_service.get_user_by_id(gamer.id).coins
    success = reward_service.buy_reward(gamer.id, reward_id)
    assert success is True
    coins_after_buy = user_service.get_user_by_id(gamer.id).coins
    assert coins_after_buy == coins_before_buy - 5
    print(f"[OK] Recompensa comprada. Monedes descomptades: {coins_before_buy} -> {coins_after_buy}")

    # 3. Llista de pendents de lliurar (Pending Deliveries)
    pending = reward_service.get_pending_deliveries(1)
    matched_pending = [p for p in pending if p["reward_name"] == "Cinema i Palometes"]
    assert len(matched_pending) >= 1
    rh_id = matched_pending[0]["id"]
    print(f"[OK] Sol·licitud pendent trobada a la cua d'administració (ID sol·licitud: {rh_id})")

    # 4. Lliurament d'administrador amb comentari i auditoria (Delivery)
    reward_service.deliver_reward(rh_id, admin_id=admin.id, comment="Entregades les entrades físiques!")
    
    row_rh = database.query_one("SELECT * FROM reward_history WHERE id = ?", (rh_id,))
    assert row_rh["delivered"] == 1
    assert row_rh["delivered_by"] == admin.id
    assert row_rh["delivered_at"] is not None
    assert row_rh["comment"] == "Entregades les entrades físiques!"
    print(f"[OK] Recompensa lliurada amb auditoria (Admin ID: {admin.id}, Data: {row_rh['delivered_at']})")

    # 5. Historial de recompenses de l'usuari amb auditoria (History)
    history = reward_service.get_user_reward_history(gamer.id)
    matched_history = [h for h in history if h["id"] == rh_id]
    assert len(matched_history) == 1
    assert matched_history[0]["delivered_by_name"] == admin.name
    assert matched_history[0]["comment"] == "Entregades les entrades físiques!"
    print(f"[OK] Historial d'usuari auditat correctament. Validador: {matched_history[0]['delivered_by_name']}")

    # 6. Protecció de concurrència i monedes en negatiu
    # Intentar comprar una recompensa caríssima que no es pot pagar
    expensive_reward = Reward(family_id=1, name="Viatge a la Lluna", points_required=99999, active=1)
    exp_id = reward_service.create_reward(expensive_reward)
    fail_buy = reward_service.buy_reward(gamer.id, exp_id)
    assert fail_buy is False
    assert user_service.get_user_by_id(gamer.id).coins >= 0
    print("[OK] Protecció de saldo verificada: No es permeten compres amb saldo insuficient ni monedes en negatiu.")

    # Neteja de dades de la prova
    database.execute("DELETE FROM reward_history WHERE id = ?", (rh_id,))
    database.execute("DELETE FROM rewards WHERE id IN (?, ?)", (reward_id, exp_id))
    database.execute("DELETE FROM points_history WHERE user_id = ? AND mission_id = ?", (gamer.id, mission_id))
    database.execute("DELETE FROM mission_assignments WHERE id = ?", (as_id,))
    database.execute("DELETE FROM missions WHERE id = ?", (mission_id,))


    print("\nALL SPRINT 5.6 REWARDS TESTS PASSED 100% CLEANLY!")


if __name__ == "__main__":
    test_rewards_sprint56()

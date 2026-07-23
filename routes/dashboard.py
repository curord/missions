from flask import Blueprint, render_template, session, redirect, url_for
from pathlib import Path
from datetime import datetime
from config import Config
import database
from services.user_service import UserService
from services.mission_service import MissionService
from services.reward_service import RewardService

dashboard_bp = Blueprint("dashboard", __name__)
user_service = UserService()
mission_service = MissionService()
reward_service = RewardService()


@dashboard_bp.route("/dashboard")
def dashboard():
    """
    Renderitza la vista de dashboard principal de l'usuari (gamer o administrador),
    calculant llistes de missions completades, pendents i de validació en curs.
    Incolu el panell de diagnòstic si Config.DEBUG és True.
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = user_service.get_user_by_id(session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    missions = mission_service.get_user_missions(user.id)

    pending_missions = [
        m for m in missions
        if m["status"] in ("pending", "in_progress")
    ]

    waiting_missions = [
        m for m in missions
        if m["status"] == "waiting_validation"
    ]

    total_missions = len(missions)
    total_points = user["points"]

    waiting = mission_service.get_waiting_validations_for_user(user.id)
    waiting_count = len(waiting)

    completed_missions = [
        m for m in missions
        if m["status"] == "completed"
    ]

    rejected_missions = [
        m for m in missions
        if m["status"] == "rejected"
    ]

    # Construcció del Panell de Diagnòstic (DEBUG) si Config.DEBUG és True
    debug_info = None
    if getattr(Config, "DEBUG", False):
        db_path_obj = Path(Config.DATABASE).resolve()

        # Verificació de la connexió a la BD
        conn_ok = False
        try:
            with database.get_connection() as conn:
                conn_ok = True
        except Exception:
            conn_ok = False

        # Comptadors reals de totes les taules sol·licitades via SQL directe
        target_tables = [
            "families", "users", "categories", "mission_types",
            "missions", "mission_assignments", "rewards",
            "reward_history", "activities", "activity_users", "points_history"
        ]
        db_table_counts = {}
        for tbl in target_tables:
            if database.table_exists(tbl):
                try:
                    res = database.query_one(f"SELECT COUNT(*) AS total FROM {tbl}")
                    db_table_counts[tbl] = res["total"] if res else 0
                except Exception:
                    db_table_counts[tbl] = "Error"
            else:
                db_table_counts[tbl] = "0 (no creada)"

        # Comptadors carregats pels serveis
        all_missions = mission_service.get_all_missions()
        all_users = user_service.get_all_users()
        family_users = user_service.get_family_users(user.family_id)
        user_history = mission_service.get_user_mission_history(user.id)
        all_rewards = reward_service.get_all_rewards()
        user_purchases = reward_service.get_user_reward_history(user.id)
        pending_deliveries = reward_service.get_pending_deliveries_count(user.family_id)

        service_counts = {
            "mission_service_all_missions": len(all_missions),
            "mission_service_user_assignments": len(missions),
            "mission_service_waiting_validations": len(waiting),
            "mission_service_user_history": len(user_history),
            "user_service_all_users": len(all_users),
            "user_service_family_users": len(family_users),
            "reward_service_all_rewards": len(all_rewards),
            "reward_service_user_purchases": len(user_purchases),
            "reward_service_pending_deliveries": pending_deliveries
        }

        total_db_assignments = db_table_counts.get("mission_assignments", 0)

        debug_info = {
            "db_engine": "PostgreSQL" if getattr(database, "IS_POSTGRES", False) else "SQLite",
            "db_path": str(db_path_obj),
            "file_exists": db_path_obj.exists(),
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "connection_ok": conn_ok,
            "db_table_counts": db_table_counts,
            "service_counts": service_counts,
            "total_db_assignments": total_db_assignments,
            "session_data": {
                "user_id": session.get("user_id"),
                "role": session.get("role"),
                "user_name": session.get("user_name"),
                "family_id": user.family_id
            }
        }

    return render_template(
        "dashboard.html",
        user=user,
        missions=missions,
        pending_missions=pending_missions,
        waiting_missions=waiting_missions,
        total_missions=total_missions,
        total_points=total_points,
        waiting_count=waiting_count,
        completed_missions=completed_missions,
        rejected_missions=rejected_missions,
        waiting=waiting,
        debug_info=debug_info
    )

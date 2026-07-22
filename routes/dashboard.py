from flask import Blueprint, render_template, session, redirect, url_for
from services.user_service import UserService
from services.mission_service import MissionService

dashboard_bp = Blueprint("dashboard", __name__)
user_service = UserService()
mission_service = MissionService()


@dashboard_bp.route("/dashboard")
def dashboard():
    """
    Renderitza la vista de dashboard principal de l'usuari (gamer o administrador),
    calculant llistes de missions completades, pendents i de validació en curs.
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
        waiting=waiting
    )

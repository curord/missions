from flask import Blueprint, render_template, redirect, session, url_for
from services.user_service import UserService
from services.mission_service import MissionService

import logging

missions_bp = Blueprint("missions", __name__)
user_service = UserService()
mission_service = MissionService()


@missions_bp.get("/missions")
def missions():
    """
    Renderitza la llista de missions de l'usuari actual que estan actives.
    """
    logging.info("Sessió actual: %s", session)
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = user_service.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    missions = mission_service.get_user_missions(user.id)

    return render_template(
        "missions.html",
        user=user,
        missions=missions
    )



@missions_bp.post("/mission/<int:assignment_id>/complete")
def complete(assignment_id):
    """
    Marca una missió assignada com a completada per l'usuari actual i redirigeix al dashboard.
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    mission_service.complete_mission(
        assignment_id,
        session["user_id"]
    )

    return redirect(url_for("dashboard.dashboard"))


@missions_bp.get("/missions/history")
def history():
    """
    Renderitza la vista de l'historial complet de missions (aprovades, rebutjades, cancel·lades)
    de l'usuari gamer actualment autenticat.
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = user_service.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    history = mission_service.get_user_mission_history(user.id)

    return render_template(
        "history.html",
        user=user,
        history=history
    )





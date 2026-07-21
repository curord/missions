from flask import Blueprint, render_template, session, redirect, url_for, request, g
from config import Config
from services.user_service import UserService
from services.mission_service import MissionService
from database import approve_mission, reject_mission
import logging

ADMIN_PIN = Config.ADMIN_PIN
admin_bp = Blueprint("admin", __name__)
user_service = UserService()
mission_service = MissionService()


@admin_bp.before_request
def require_admin():
    """
    Hook global per a validar que l'usuari estigui autenticat i tingui rol d'administrador.
    Emmagatzema l'usuari obtingut al context global 'g.user'.
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = user_service.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    if user["role"] != "admin":
        return redirect(url_for("dashboard.dashboard"))

    # Guardem l'usuari al context global g per a les rutes de Blueprint
    g.user = user


@admin_bp.route("/admin", methods=["GET", "POST"])
def admin():
    """
    Renderitza el panell de control de l'administrador (amb validacions pendents).
    Exigeix verificació de PIN abans d'accedir-hi.
    """
    logging.info("Accedint a la vista admin")

    # Demanar PIN si encara no està validat
    if not session.get("admin_verified"):
        logging.info("Cal validar el PIN de l'administrador")
        if request.method == "POST":
            pin = request.form.get("pin")
            if pin == Config.ADMIN_PIN:
                session["admin_verified"] = True
                return redirect(url_for("admin.admin"))

        return render_template("admin_pin.html")

    waiting = mission_service.get_waiting_validations()

    return render_template(
        "admin.html",
        user=g.user,
        waiting=waiting
    )


@admin_bp.post("/admin/mission/<int:assignment_id>/approve")
def approve(assignment_id):
    """
    Aprova la finalització d'una missió i atorga els punts/monedes al gamer.
    """
    approve_mission(assignment_id, session["user_id"])
    return redirect(url_for("admin.admin"))


@admin_bp.post("/admin/mission/<int:assignment_id>/reject")
def reject(assignment_id):
    """
    Rebutja la validació d'una missió, tornant-la a l'estat pendent.
    """
    reject_mission(assignment_id)
    return redirect(url_for("admin.admin"))


@admin_bp.post("/admin/missions/<int:id>/edit")
def update_mission_post(id):
    """
    Processa el formulari de modificació d'una missió existent.
    """
    mission_service.update_mission(id, request.form)
    return redirect(url_for("admin.missions"))


@admin_bp.get("/admin/missions")
def missions():
    """
    Renderitza el catàleg complet de missions per a la seva visualització o edició.
    """
    missions = mission_service.get_all_missions()
    return render_template(
        "admin/missions.html",
        user=g.user,
        missions=missions
    )


@admin_bp.route("/admin/missions/new",  methods=["GET", "POST"])
def mission_new():
    """
    Renderitza el formulari de creació o processa la creació d'una nova plantilla de missió.
    """
    if request.method == "POST":
        mission_service.create_mission(request.form, family_id=g.user["family_id"])
        return redirect(url_for("admin.missions"))

    categories = mission_service.get_categories()
    users = user_service.get_family_users()

    return render_template(
        "admin/mission_form.html",
        user=g.user,
        mission=None,
        categories=categories,
        users=users
    )


@admin_bp.route("/admin/missions/<int:id>/edit")
def mission_edit(id):
    """
    Renderitza el formulari de modificació d'una missió ja existent amb les dades precarregades.
    """
    mission = mission_service.get_mission_by_id(id)
    categories = mission_service.get_categories()
    users = user_service.get_family_users()

    return render_template(
        "admin/mission_form.html",
        user=g.user,
        mission=mission,
        categories=categories,
        users=users
    )
from flask import Blueprint, render_template, session, redirect, url_for, request, g
from config import Config
from services.user_service import UserService
from services.mission_service import MissionService
import logging
import database

ADMIN_PIN = Config.ADMIN_PIN
admin_bp = Blueprint("admin", __name__)
user_service = UserService()
mission_service = MissionService()


def sync_mission_assignments(mission_id, target_user_ids):
    """
    Sincronitza les assignacions de missions (crea noves assignacions de tipus 'pending'
    i marca com a 'cancelled' les assignacions pendents dels usuaris desassignats).
    """
    current_rows = database.query(
        "SELECT id, user_id, status FROM mission_assignments WHERE mission_id = ?",
        (mission_id,)
    )
    current_by_user = {row["user_id"]: row for row in current_rows}

    # Assignar a nous usuaris o reactivar cancel·lades
    for uid in target_user_ids:
        if uid not in current_by_user:
            database.execute(
                "INSERT INTO mission_assignments (mission_id, user_id, status) VALUES (?, ?, 'pending')",
                (mission_id, uid)
            )
        elif current_by_user[uid]["status"] == "cancelled":
            database.execute(
                "UPDATE mission_assignments SET status = 'pending' WHERE id = ?",
                (current_by_user[uid]["id"],)
            )

    # Cancel·lar assignacions pendents per a usuaris desassignats
    for uid, row in current_by_user.items():
        if uid not in target_user_ids:
            if row["status"] in ("pending", "waiting_validation"):
                database.execute(
                    "UPDATE mission_assignments SET status = 'cancelled' WHERE id = ?",
                    (row["id"],)
                )



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
    mission_service.approve_mission(assignment_id, session["user_id"])
    return redirect(url_for("admin.admin"))


@admin_bp.post("/admin/mission/<int:assignment_id>/reject")
def reject(assignment_id):
    """
    Rebutja la validació d'una missió, registrant-ne el motiu de devolució.
    """
    reason = request.form.get("reason")
    mission_service.reject_mission(assignment_id, reason)
    return redirect(url_for("admin.admin"))



@admin_bp.post("/admin/missions/<int:id>/edit")
def update_mission_post(id):
    """
    Processa el formulari de modificació d'una missió existent.
    """
    mission_service.update_mission(id, request.form)

    # Sincronitzar assignacions de membres de la família
    assignee_type = request.form.get("assignee_type")
    if assignee_type == "all":
        members = [u.id for u in user_service.get_family_users(g.user["family_id"])]
        sync_mission_assignments(id, members)
    else:
        selected_users = [int(uid) for uid in request.form.getlist("assigned_users")]
        sync_mission_assignments(id, selected_users)


    return redirect(url_for("admin.missions"))



@admin_bp.get("/admin/missions")
def missions():
    """
    Renderitza el catàleg complet de missions per a la seva visualització o edició,
    recuperant a més els membres assignats a cadascuna d'elles.
    """
    missions = mission_service.get_all_missions()

    # Obtenir els usuaris assignats a cada missió de la família
    assignments = database.query(
        """
        SELECT ma.mission_id, u.name
        FROM mission_assignments ma
        JOIN users u ON u.id = ma.user_id
        WHERE ma.status <> 'cancelled'
        """
    )
    from collections import defaultdict
    assigned_members = defaultdict(list)
    for a in assignments:
        assigned_members[a["mission_id"]].append(a["name"])

    # Adjuntar els noms dels membres a cada missió
    for m in missions:
        m.assigned_names = assigned_members[m.id]

    active_missions = [m for m in missions if m.active]
    inactive_missions = [m for m in missions if not m.active]

    return render_template(
        "admin/missions.html",
        user=g.user,
        active_missions=active_missions,
        inactive_missions=inactive_missions
    )


@admin_bp.post("/admin/missions/<int:id>/toggle-active")
def toggle_active(id):
    """
    Activa o desactiva una missió del catàleg.
    """
    mission = mission_service.get_mission_by_id(id)
    if mission:
        new_active = 0 if mission.active else 1
        database.execute("UPDATE missions SET active = ? WHERE id = ?", (new_active, id))
    return redirect(url_for("admin.missions"))




@admin_bp.route("/admin/missions/new",  methods=["GET", "POST"])
def mission_new():
    """
    Renderitza el formulari de creació o processa la creació d'una nova plantilla de missió.
    """
    if request.method == "POST":
        mission_id = mission_service.create_mission(request.form, family_id=g.user["family_id"])

        # Sincronitzar assignacions de membres de la família
        assignee_type = request.form.get("assignee_type")
        if assignee_type == "all":
            members = [u.id for u in user_service.get_family_users(g.user["family_id"])]
            sync_mission_assignments(mission_id, members)
        else:
            selected_users = [int(uid) for uid in request.form.getlist("assigned_users")]
            sync_mission_assignments(mission_id, selected_users)


        return redirect(url_for("admin.missions"))

    categories = mission_service.get_categories()
    users = user_service.get_family_users()

    return render_template(
        "admin/mission_form.html",
        user=g.user,
        mission=None,
        categories=categories,
        users=users,
        assigned_user_ids=[]
    )


@admin_bp.route("/admin/missions/<int:id>/edit")
def mission_edit(id):
    """
    Renderitza el formulari de modificació d'una missió ja existent amb les dades precarregades.
    """
    mission = mission_service.get_mission_by_id(id)
    categories = mission_service.get_categories()
    users = user_service.get_family_users()

    # Obtenir els usuaris assignats actualment (que no estiguin cancel·lats)
    rows = database.query("SELECT user_id FROM mission_assignments WHERE mission_id = ? AND status <> 'cancelled'", (id,))
    assigned_user_ids = [row["user_id"] for row in rows]

    return render_template(
        "admin/mission_form.html",
        user=g.user,
        mission=mission,
        categories=categories,
        users=users,
        assigned_user_ids=assigned_user_ids
    )
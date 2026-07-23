from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from services.user_service import UserService
from services.stats_service import StatsService

stats_bp = Blueprint("stats", __name__)
user_service = UserService()
stats_service = StatsService()


@stats_bp.route("/stats")
def stats():
    """
    Renderitza la vista principal del Centre d'Estadístiques.
    Controla l'accés per rol (Gamers només a Les meves estadístiques; Administradors accés complet).
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = user_service.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    is_admin = (user.role == "admin")

    # Si és Gamer, només pot veure la pestanya 1
    requested_tab = request.args.get("tab", "my_stats")
    if not is_admin:
        active_tab = "my_stats"
    else:
        active_tab = requested_tab if requested_tab in ("my_stats", "family_stats", "rankings") else "my_stats"

    # Si l'administrador vol veure les estadístiques d'un membre específic
    target_user_id = user.id
    inspect_member = None
    if is_admin and request.args.get("user_id"):
        try:
            inspect_id = int(request.args.get("user_id"))
            member = user_service.get_user_by_id(inspect_id)
            if member and member.family_id == user.family_id:
                target_user_id = inspect_id
                inspect_member = member
        except (ValueError, TypeError):
            pass

    # Obtenir dades individuals de l'usuari seleccionat
    user_stats = stats_service.get_user_stats_summary(target_user_id)

    # Obtenir dades familiars i classificacions si és administrador
    family_stats = stats_service.get_family_stats_summary(user.family_id) if is_admin else None
    leaderboards = stats_service.get_leaderboards(user.family_id) if is_admin else None

    # Obtenir sèrie d'evolució inicial (per defecte "total")
    evolution_series = stats_service.get_user_evolution_series(target_user_id, period="total")

    return render_template(
        "stats.html",
        user=user,
        is_admin=is_admin,
        active_tab=active_tab,
        user_stats=user_stats,
        family_stats=family_stats,
        leaderboards=leaderboards,
        evolution_series=evolution_series,
        inspect_member=inspect_member
    )


@stats_bp.get("/api/stats/evolution")
def api_evolution():
    """
    API JSON per a actualitzar dinàmicament la gràfica d'evolució segons el filtre temporal
    (Setmana, Mes, Any, Total).
    """
    if "user_id" not in session:
        return jsonify({"error": "No autoritzat"}), 401

    user = user_service.get_user_by_id(session["user_id"])
    if not user:
        return jsonify({"error": "Usuari no trobat"}), 404

    period = request.args.get("period", "total")
    target_id = request.args.get("user_id", user.id)

    try:
        target_id = int(target_id)
        if user.role != "admin" and target_id != user.id:
            target_id = user.id
    except (ValueError, TypeError):
        target_id = user.id

    series = stats_service.get_user_evolution_series(target_id, period=period)
    return jsonify(series)


@stats_bp.get("/api/stats/member/<int:member_id>")
def api_member_detail(member_id):
    """
    API JSON per a carregar el detall complet d'un membre de la família per al Modal Bootstrap.
    """
    if "user_id" not in session:
        return jsonify({"error": "No autoritzat"}), 401

    user = user_service.get_user_by_id(session["user_id"])
    if not user or user.role != "admin":
        return jsonify({"error": "Només administradors"}), 403

    member_stats = stats_service.get_user_stats_summary(member_id)
    if not member_stats:
        return jsonify({"error": "Membre no trobat"}), 404

    # Sanetitzar l'objecte user per a JSON
    member = member_stats["user"]
    member_dict = {
        "id": member.id,
        "name": member.name,
        "role": member.role,
        "avatar": member.avatar,
        "favorite_color": member.favorite_color,
        "level": member.level,
        "points": member.points,
        "coins": member.coins,
        "streak": member.streak
    }
    member_stats["user"] = member_dict
    
    # Treure objectes no serialitzables (Categories/Missions) o simplificar-los
    member_stats["categories"] = [c.to_dict() if hasattr(c, 'to_dict') else {"id": c.id, "name": c.name} for c in member_stats.get("categories", [])]
    member_stats["history"] = [
        {
            "mission_id": h.mission_id,
            "title": h.title,
            "status": h.status,
            "coins": h.coins,
            "points": h.points,
            "validated_date": getattr(h, "validated_date", "")
        } for h in member_stats.get("history", [])[:10]
    ]

    return jsonify(member_stats)

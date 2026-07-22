from flask import Blueprint, render_template, session, redirect, url_for, request, g, flash
from services.reward_service import RewardService
from services.user_service import UserService
from models.reward import Reward

rewards_bp = Blueprint("rewards", __name__)
reward_service = RewardService()
user_service = UserService()


@rewards_bp.before_request
def require_login():
    """
    Hook abans de cada petició per a verificar que l'usuari estigui autenticat
    i carregar les seves dades d'usuari a g.user.
    """
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    g.user = user_service.get_user_by_id(session["user_id"])
    if not g.user:
        session.clear()
        return redirect(url_for("auth.login"))


@rewards_bp.get("/rewards")
def rewards():
    """
    Mostra la llista de recompenses disponibles per a la família del nen.
    Separa les recompenses en assolibles i no assolibles segons el seu saldo.
    També mostra l'historial de compres de l'usuari.
    """
    rewards_list = reward_service.get_rewards_by_family(g.user.family_id)
    history = reward_service.get_user_reward_history(g.user.id)

    # Separar disponibles de no assolibles segons monedes del nen
    affordable_rewards = [r for r in rewards_list if r.active and g.user.coins >= r.points_required]
    unaffordable_rewards = [r for r in rewards_list if r.active and g.user.coins < r.points_required]

    return render_template(
        "rewards.html",
        user=g.user,
        affordable=affordable_rewards,
        unaffordable=unaffordable_rewards,
        history=history
    )


@rewards_bp.post("/rewards/<int:id>/buy")
def buy(id):
    """
    Processa la compra d'una recompensa per part d'un nen.
    Verifica el saldo i mostra missatges flash informatius.
    """
    if g.user.role != "child":
        flash("Només els nens poden comprar recompenses! 🎁", "danger")
        return redirect(url_for("rewards.rewards"))

    success = reward_service.buy_reward(g.user.id, id)
    if success:
        flash("Recompensa comprada correctament! 🎁 Enhorabona!", "success")
    else:
        flash("No tens prou monedes per comprar aquesta recompensa! 💰", "danger")
    return redirect(url_for("rewards.rewards"))


# ==========================================
# ADMIN ROUTES (RECOMPENSES)
# ==========================================

@rewards_bp.get("/admin/rewards")
def admin_rewards():
    """
    Llista les recompenses del catàleg per a administració (actives/inactives) i les compres pendents de lliurar.
    """
    if g.user.role != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if not session.get("admin_verified"):
        return redirect(url_for("admin.admin"))

    all_rewards = reward_service.get_all_rewards()
    active_rewards = [r for r in all_rewards if r.active]
    inactive_rewards = [r for r in all_rewards if not r.active]
    pending_deliveries = reward_service.get_pending_deliveries(g.user.family_id)

    return render_template(
        "admin/rewards.html",
        user=g.user,
        active_rewards=active_rewards,
        inactive_rewards=inactive_rewards,
        pending_deliveries=pending_deliveries
    )


@rewards_bp.post("/admin/rewards/deliver/<int:history_id>")
def admin_reward_deliver(history_id):
    """
    Marca una recompensa com a lliurada físicament a l'usuari registrant l'administrador i un comentari.
    """
    if g.user.role != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if not session.get("admin_verified"):
        return redirect(url_for("admin.admin"))

    comment = request.form.get("comment")
    reward_service.deliver_reward(history_id, admin_id=g.user.id, comment=comment)
    flash("Recompensa marcada com a lliurada correctament! 🎁", "success")
    return redirect(url_for("rewards.admin_rewards"))


@rewards_bp.route("/admin/rewards/new", methods=["GET", "POST"])
def admin_reward_new():
    """
    Formulari de creació de recompenses de la família.
    """
    if g.user.role != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if not session.get("admin_verified"):
        return redirect(url_for("admin.admin"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        points_required = int(request.form.get("points_required", 0))
        icon = request.form.get("icon", "🎁")

        new_reward = Reward(
            family_id=g.user.family_id,
            name=name,
            description=description,
            points_required=points_required,
            icon=icon,
            active=1
        )
        reward_service.create_reward(new_reward)
        flash("Recompensa creada correctament!", "success")
        return redirect(url_for("rewards.admin_rewards"))

    return render_template(
        "admin/reward_form.html",
        user=g.user,
        reward=None
    )


@rewards_bp.route("/admin/rewards/<int:id>/edit", methods=["GET", "POST"])
def admin_reward_edit(id):
    """
    Formulari de modificació de recompenses existents.
    """
    if g.user.role != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if not session.get("admin_verified"):
        return redirect(url_for("admin.admin"))

    reward = reward_service.get_reward_by_id(id)
    if not reward:
        flash("Recompensa no trobada!", "danger")
        return redirect(url_for("rewards.admin_rewards"))

    if request.method == "POST":
        reward.name = request.form.get("name")
        reward.description = request.form.get("description")
        reward.points_required = int(request.form.get("points_required", 0))
        reward.icon = request.form.get("icon", "🎁")
        reward.active = 1 if request.form.get("active") else 0

        reward_service.update_reward(reward)
        flash("Recompensa actualitzada correctament!", "success")
        return redirect(url_for("rewards.admin_rewards"))

    return render_template(
        "admin/reward_form.html",
        user=g.user,
        reward=reward
    )



@rewards_bp.post("/admin/rewards/<int:id>/toggle-active")
def admin_reward_toggle(id):
    """
    Activa o desactiva una recompensa de la llista d'administració.
    """
    if g.user.role != "admin":
        return redirect(url_for("dashboard.dashboard"))
    if not session.get("admin_verified"):
        return redirect(url_for("admin.admin"))

    reward = reward_service.get_reward_by_id(id)
    if reward:
        reward.active = 0 if reward.active else 1
        reward_service.update_reward(reward)
    return redirect(url_for("rewards.admin_rewards"))

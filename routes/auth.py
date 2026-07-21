from flask import Blueprint, render_template, redirect, session, url_for
from services.user_service import UserService

auth_bp = Blueprint("auth", __name__)
user_service = UserService()


@auth_bp.route("/login")
def login():
    """
    Renderitza la pàgina de login principal llistant tots els usuaris disponibles.
    """
    users = user_service.get_all_users()

    if not users:
        return "No hi ha usuaris a la base de dades."

    return render_template(
        "login.html",
        users=users
    )


@auth_bp.route("/login/<username>")
def login_user(username):
    """
    Autentica un usuari pel seu nom de pila i inicialitza la sessió de Flask.
    """
    user = user_service.get_user_by_name(username)

    if not user:
        return redirect(url_for("auth.login"))

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["role"] = user["role"]

    if user["role"] == "admin":
        return redirect(url_for("admin.admin"))
    else:
        return redirect(url_for("dashboard.dashboard"))


@auth_bp.route("/logout")
def logout():
    """
    Tanca la sessió actual i neteja les dades emmagatzemades a Flask.
    """
    session.clear()
    return redirect(url_for("auth.login"))

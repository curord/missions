from flask import Blueprint, render_template

ui_bp = Blueprint("ui", __name__)


@ui_bp.route("/ui")
def ui():
    """
    Renderitza la pàgina de la guia d'elements de la interfície d'usuari (UI Kit).
    """
    return render_template("ui.html")
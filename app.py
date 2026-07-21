from flask import Flask, redirect, session, url_for
from config import Config
from database import init_database
from routes.ui import ui_bp
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


# Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.missions import missions_bp
from routes.admin import admin_bp


app = Flask(__name__)
app.config.from_object(Config)

# Inicialitza la base de dades
init_database()

# Registrar rutes
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(missions_bp)
app.register_blueprint(ui_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def index():

    if session.get("user_id"):
        return redirect(url_for("dashboard.dashboard"))

    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
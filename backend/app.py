import os
import locale
from flask import Flask, render_template
from backend.routes.upload_routes import upload_bp
from backend.routes.user_routes import user_bp
from backend.routes.annotation_routes import annotate_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.greenit_routes import greenit_bp
from datetime import datetime


# === Chemins absolus pour les dossiers templates et statics ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "..", "frontend")  # ../frontend (ex-templates)
STATIC_FOLDER = os.path.join(BASE_DIR, "..", "static")       # ../static

# === Création de l'application Flask ===
app = Flask(__name__, template_folder=TEMPLATES_FOLDER, static_folder=STATIC_FOLDER)
app.secret_key = "dev_une_clé_pas_sécurisée"

# === Configuration du dossier d'upload ===
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, "uploads")

# Pour avoir les mois et jours en français (ex : juillet)
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    pass  # utile si le serveur ne supporte pas cette locale

def format_date_fr(value):
    try:
        dt = datetime.fromisoformat(value.rstrip('Z'))
        return dt.strftime("%d %B %Y")  # Exemple : 02 juillet 2025
    except ValueError:
        return value

def format_time_fr(value):
    try:
        dt = datetime.fromisoformat(value.rstrip('Z'))
        return dt.strftime("%H:%M")  # Exemple : 14:25
    except ValueError:
        return value

app.jinja_env.filters['date_fr'] = format_date_fr
app.jinja_env.filters['heure_fr'] = format_time_fr


# === Enregistrement des blueprints avec des préfixes ===
app.register_blueprint(upload_bp, url_prefix="/upload")
app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(annotate_bp, url_prefix="/annotate")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(greenit_bp, url_prefix="/greenit")

# === Pages principales ===
@app.route("/")
def home():
    return render_template("accueil.html")


@app.route("/help")
def aide():
    return render_template("aide.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/cookies")
def cookies():
    return render_template("cookies.html")

if __name__ == "__main__":
    app.run(debug=True)


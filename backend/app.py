import os
from flask import Flask, render_template
from backend.routes.upload_routes import upload_bp
from backend.routes.user_routes import user_bp
from backend.routes.annotation_routes import annotate_bp

# === Chemins absolus pour les dossiers templates et statics ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "..", "frontend")  # ../frontend (ex-templates)
STATIC_FOLDER = os.path.join(BASE_DIR, "..", "static")       # ../static

# === Création de l'application Flask ===
app = Flask(__name__, template_folder=TEMPLATES_FOLDER, static_folder=STATIC_FOLDER)
app.secret_key = "dev_une_clé_pas_sécurisée"

# === Configuration du dossier d'upload ===
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, "uploads")

# === Enregistrement des blueprints avec des préfixes ===
app.register_blueprint(upload_bp, url_prefix="/upload")
app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(annotate_bp, url_prefix="/annotate")

# === Pages principales ===
@app.route("/")
def home():
    return render_template("accueil.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/greenit")
def greenit():
    return render_template("greenit.html")

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

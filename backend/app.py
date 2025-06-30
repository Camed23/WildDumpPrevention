import os
from flask import Flask, render_template
from backend.routes.upload_routes import upload_bp
from backend.routes.user_routes import user_bp
from backend.routes.annotation_routes import annotate_bp


app = Flask(__name__)
app.secret_key = "dev_une_clé_pas_sécurisée"

# Chemin absolu vers le dossier 'uploads' dans 'backend'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, "uploads")

app.register_blueprint(upload_bp)
app.register_blueprint(user_bp)
app.register_blueprint(annotate_bp)

@app.route("/")
def home():
    return render_template("hello.html")

if __name__ == "__main__":
    app.run(debug=True)

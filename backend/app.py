import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement (.env)

def create_app():
    app = Flask(__name__)

    # Configurations globales
    app.secret_key = "dev_une_clé_pas_sécurisée"
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'backend', 'uploads')

    # Import et enregistrement des Blueprints (routes)
    from routes.upload import bp as upload_bp
    from routes.user import bp as user_bp
    from routes.home import bp as home_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(home_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)


from flask import Flask, send_from_directory, render_template
from config import UPLOAD_FOLDER
from routes.upload_routes import upload_bp
from routes.user_routes import user_bp
from routes.gallery_routes import gallery_bp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "dev_une_clé_pas_sécurisée"

app.register_blueprint(upload_bp)
app.register_blueprint(user_bp)
app.register_blueprint(gallery_bp)

@app.route('/')
def home():
    return render_template("hello.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)


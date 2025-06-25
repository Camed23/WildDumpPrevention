import os
from flask import Flask, render_template, flash, request, redirect, send_from_directory, url_for
from supabase import create_client

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "dev_une_clé_pas_sécurisée"

url = "https://bqkxmcrmolfjlglmmqlj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJxa3htY3Jtb2xmamxnbG1tcWxqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3NzI1ODgsImV4cCI6MjA2NjM0ODU4OH0.QrcFfKD2aHZP-PwVoWWq1hnNZ5cOCckL4YvmPHsSmt0"
supabase = create_client(url, key)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(extension):
    upload_path = app.config['UPLOAD_FOLDER']

    # Crée le dossier s’il n’existe pas
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    max_index = 0
    for filename in os.listdir(upload_path):
        if filename.startswith("image") and '.' in filename:
            base, ext = filename.rsplit('.', 1)
            if ext.lower() in ALLOWED_EXTENSIONS:
                number_str = base.replace("image", "")
                try:
                    number = int(number_str)
                    if number > max_index:
                        max_index = number
                except ValueError:
                    pass
    return f"image{max_index + 1}.{extension}"

def insert_image_metadata(filename, annotation="inconnue"):
    response = supabase.rpc("creation_image", {
        "p_user_id": 4,  # ou l’ID réel de l’utilisateur uploader
        "p_file_path": f"/uploads/{filename}",
        "p_name_image": filename,
        "p_size": os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename)) / 1024,
        "p_width": 0,
        "p_height": 0,
        "p_avg_red": 0,
        "p_avg_green": 0,
        "p_avg_blue": 0,
        "p_contrast": 0,
        "p_edges_detected": 0
    }).execute()
    return response


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            extension = file.filename.rsplit('.', 1)[1].lower()
            filename = generate_unique_filename(extension)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            insert_image_metadata(filename)
            flash(f"Fichier {filename} uploadé avec succès !")
            return redirect(url_for('show_image', filename=filename))

        flash("Fichier non autorisé")
        return redirect(request.url)

    return render_template("image_form.html")


@app.route("/")
def home():
    return render_template("hello.html")

@app.route('/image/<filename>')
def show_image(filename):
    return render_template("show_image.html", filename=filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/gallery')
def gallery():
    files = [
        f for f in os.listdir(app.config['UPLOAD_FOLDER'])
        if allowed_file(f)
    ]
    return render_template("gallery.html", images=files)

@app.route("/supabase-gallery")
def supabase_gallery():
    result = supabase.table("image").select("*").execute()
    images = result.data
    return render_template("supabase_gallery.html", images=images)


if __name__ == "__main__":
    app.run(debug=True)

import os
from flask import Blueprint, render_template, flash, request, redirect, url_for, send_from_directory
from services.supabase_client import supabase

bp = Blueprint('upload', __name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'backend', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(extension):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    max_index = max(
        [int(f[5:].split('.')[0]) for f in os.listdir(UPLOAD_FOLDER) if f.startswith("image") and allowed_file(f)],
        default=0
    )
    return f"image{max_index + 1}.{extension}"

def insert_image_metadata(filename):
    response = supabase.rpc("creation_image", {
        "p_user_id": 4,  # ou l’ID réel
        "p_file_path": f"/uploads/{filename}",
        "p_name_image": filename,
        "p_size": os.path.getsize(os.path.join(UPLOAD_FOLDER, filename)) / 1024,
        "p_width": 0, "p_height": 0,
        "p_avg_red": 0, "p_avg_green": 0, "p_avg_blue": 0,
        "p_contrast": 0, "p_edges_detected": False
    }).execute()
    return response

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash("Aucun fichier sélectionné")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = generate_unique_filename(ext)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            insert_image_metadata(filename)
            flash(f"Fichier {filename} uploadé avec succès !")
            return redirect(url_for('upload.show_image', filename=filename))
        flash("Fichier non autorisé")
    return render_template("image_form.html")

@bp.route('/image/<filename>')
def show_image(filename):
    return render_template("show_image.html", filename=filename)

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@bp.route('/gallery')
def gallery():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    return render_template("gallery.html", images=files)

@bp.route("/supabase-gallery")
def supabase_gallery():
    result = supabase.table("image").select("*").execute()
    images = result.data
    return render_template("supabase_gallery.html", images=images)

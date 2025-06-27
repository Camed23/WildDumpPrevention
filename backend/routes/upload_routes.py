import os
from flask import Blueprint, render_template, request, redirect, flash, url_for, send_from_directory, current_app
from backend.services.image_service import insert_image_metadata
from backend.utils.helpers import allowed_file, generate_unique_filename

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if request.method == 'POST':
        file = request.files.get('file')
        # check if the post request has the file part
        if not file or file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            extension = file.filename.rsplit('.', 1)[1].lower()
            filename = generate_unique_filename(upload_folder, extension)
            filepath = str(os.path.join(upload_folder, filename))
            file.save(filepath)
            insert_image_metadata(filename, filepath)
            flash(f"Fichier {filename} uploadé avec succès !")
            return redirect(url_for('upload.show_image', filename=filename))
        flash("Fichier non autorisé")
        return redirect(request.url)
    return render_template("image_form.html")


@upload_bp.route('/image/<filename>')
def show_image(filename):
    return render_template("show_image.html", filename=filename)

@upload_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@upload_bp.route('/gallery')
def gallery():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    images = [f for f in os.listdir(upload_folder) if allowed_file(f)]
    return render_template("gallery.html", images=images)

import os
from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, send_from_directory, session
from backend.services.image_service import insert_image_metadata, insert_annotation, get_image_id_by_filename
from backend.services.feature_extractor import calculate_image_properties
from backend.services.user_service import get_or_create_user
from backend.utils.helpers import allowed_file, generate_unique_filename




upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Aucun fichier sélectionné.', 'error')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash("Fichier non autorisé.", 'error')
            return redirect(request.url)

        # Sauvegarde du fichier
        upload_folder = current_app.config['UPLOAD_FOLDER']
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = generate_unique_filename(upload_folder, ext)
        filepath = os.path.join(upload_folder, filename)
        file.save(str(filepath))

        # Infos du formulaire
        location = request.form.get("location")
        session["temp_date"] = request.form.get("date")
        session["temp_time"] = request.form.get("time")
        session["temp_notes"] = request.form.get("notes")

        choice = request.form.get("choice")

        # Caractéristiques de l’image
        size, width, height, avg_r, avg_g, avg_b, contrast, edges_detected = calculate_image_properties(filepath)

        # Insertion des métadonnées (sans date/time/notes)
        user_id = get_or_create_user()
        insert_image_metadata(
            filename=filename,
            user_id=user_id,
            location=location,
            size=size,
            width=width,
            height=height,
            avg_red=avg_r,
            avg_green=avg_g,
            avg_blue=avg_b,
            contrast=contrast,
            edges_detected=bool(edges_detected)  # ou int(edges_detected) si Supabase exige un entier
        )

        # Annotation
        image_id = get_image_id_by_filename(filename)
        label = None
        source = 'manuel'

        if choice == "IA":
            prediction = "plein" if avg_r < 100 and size > 150 else "vide"
            label = prediction
            source = 'auto'
        elif choice and choice.lower() in ["vide", "pleine"]:
            label = choice.lower()

        if label and image_id:
            insert_annotation(image_id=image_id, label=label, source=source)

        return redirect(url_for("annotate.show_annotation", filename=filename))

    return render_template("upload.html")

@upload_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

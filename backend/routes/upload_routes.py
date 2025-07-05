import os
from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, send_from_directory, session, jsonify
from backend.services.image_service import insert_image_metadata, insert_annotation, get_image_id_by_filename
from backend.services.feature_extractor import calculate_image_properties
from backend.services.user_service import get_or_create_user
from backend.utils.helpers import allowed_file, generate_unique_filename
from backend.services.rule_service import get_all_rules, update_rule_threshold, reset_all_thresholds



upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Gestion de la mise à jour d'une règle 
        if "rule_name" in request.form and "threshold_value" in request.form:
            rule_name = request.form.get("rule_name")
            new_value = float(request.form.get("threshold_value"))
            update_rule_threshold(rule_name, new_value)
            flash(f"Seuil mis à jour pour la règle '{rule_name}'", "success")
            return redirect(request.url)
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

    rules = get_all_rules()  # Ajouté pour le rendu HTML
    return render_template("upload.html", rules=rules)

@upload_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)



@upload_bp.route('/get_rules_json')
def get_rules_json():
    try:
        rules = get_all_rules()
        response = jsonify([{
            'rule_name': r.rule_name,
            'description': r.description,
            'threshold_operator': r.threshold_operator,
            'threshold_value': float(r.threshold_value),
            'weight': float(r.weight),
            'category': r.category
        } for r in rules])
        
        # Forcer les bons en-têtes
        response.headers['Connection'] = 'keep-alive'
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        print(f"DEBUG - Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    
@upload_bp.route('/reset_rules', methods=['POST'])
def reset_rules():
    try:
        # Réinitialise les règles
        reset_all_thresholds()
        
        # Retourne simplement un succès sans données
        return jsonify({
            "status": "success",
            "message": "Rules reset successfully"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in reset_rules: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    

@upload_bp.route('/update_rule', methods=['POST'])
def update_rule():
    try:
        rule_name = request.form.get('rule_name')
        threshold_value = float(request.form.get('threshold_value'))
        
        # Mettre à jour la règle
        update_rule_threshold(rule_name, threshold_value)
        
        return jsonify({
            "status": "success",
            "message": f"Règle {rule_name} mise à jour"
        })
    except Exception as e:
        current_app.logger.error(f"Error in update_rule: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
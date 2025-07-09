import os
from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, send_from_directory, session, jsonify
from backend.services.image_service import insert_image_metadata, insert_annotation, get_image_id_by_filename
from backend.services.feature_extractor import calculate_image_properties, ImageFeatures
from backend.services.user_service import  get_user_id_by_email
from backend.utils.helpers import allowed_file, generate_unique_filename
from backend.services.rule_service import get_all_rules, update_rule_threshold, reset_all_thresholds
from backend.services.classifier import BinClassifier
from backend.services.rules_engine import RulesEngine

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
        session["temp_date"] = request.form.get("date")
        session["temp_time"] = request.form.get("time")
        session["temp_notes"] = request.form.get("notes")

        villes_possibles = [
            "Paris", "Lyon", "Marseille", "Toulouse", "Nice",
            "Lille", "Nantes", "Strasbourg", "Bordeaux", "Montpellier",
            "Rennes", "Reims", "Le Havre"
        ]

        location = request.form.get("location")
        if location not in villes_possibles:
            flash("La ville sélectionnée n'est pas autorisée.", "error")
            return redirect(request.url)

        choice = request.form.get("choice")

        # Caractéristiques de l’image
        size, width, height, avg_r, avg_g, avg_b, contrast, edges_detected = calculate_image_properties(filepath)

        # Insertion des métadonnées (sans date/time/notes)
        if "user_id" in session:
            user_id = session["user_id"]
        else:
            user_id = get_user_id_by_email("anon@trashalyser.test")

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
            # ✅ UTILISATION COMPLÈTE DU MOTEUR DE RÈGLES AVANCÉ
            try:
                # Créer le moteur de règles et le classifier
                rules_engine = RulesEngine()
                classifier = BinClassifier(rules_engine=rules_engine)
                
                # Extraire toutes les features avancées avec ImageFeatures
                base_features = {
                    'avg_red': avg_r,
                    'avg_green': avg_g,
                    'avg_blue': avg_b,
                    'size': size,
                    'width': width,
                    'height': height,
                    'contrast': contrast,
                    'edges_detected': edges_detected
                }
                
                # Utiliser ImageFeatures pour extraire les features avancées
                image_features = ImageFeatures(base_features)
                advanced_features = image_features.extract_all_features()
                
                # Classification avec le moteur de règles sophistiqué
                result = classifier.classify(advanced_features)
                prediction = result['prediction']
                confidence = result['confidence']
                
                label = prediction
                source = 'auto'  # L'enum n'accepte que 'manuel' ou 'auto'
                
                # Log pour debugging
                print(f"🤖 Classification IA: {prediction} (confiance: {confidence:.2f})")
                print(f"⚙️ Règles actives: {len(result['details']['active_rules'])}")
                print(f"📊 Score: {result['score']:.3f}")
                
            except Exception as e:
                # Fallback simple en cas d'erreur
                print(f"❌ Erreur classification IA: {e}")
                prediction = "plein" if avg_r < 100 and size > 150 else "vide"
                label = prediction
                source = 'auto'  # Utiliser 'auto' au lieu de 'auto (fallback)'

        elif choice and choice.lower() in ["vide", "plein"]:
            if session.get("role") == "Admin":
                label = choice.lower()
                source = 'manuel'
            else:
                flash("Seuls les administrateurs peuvent faire une annotation manuelle.", "error")
                return redirect(request.url)

        if label and image_id:
            insert_annotation(image_id=image_id, label=label, source=source)

        return redirect(url_for("annotate.show_annotation", filename=filename))
    rules = get_all_rules()  # Ajouté pour le rendu HTML
    return render_template("upload.html",rules=rules)

@upload_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)



@upload_bp.route('/get_rules_json')
def get_rules_json():
    try:
        data = get_all_rules()           # ← liste de dicts
        return jsonify(data)             # ← JSON = liste
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=str(e)), 500


@upload_bp.route('/reset_rules', methods=['POST'])
def reset_rules():
    try:
        reset_all_thresholds()
        #  ❯❯ Rien d’autre : juste « Pas de contenu »
        return "", 204
    except Exception as e:
        current_app.logger.error(f"Error in reset_rules: {e}")
        return jsonify(status="error", message=str(e)), 500


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

@upload_bp.route('/classify_image', methods=['POST'])
def classify_image():
    """
    Route API pour classifier une image uploadée via AJAX
    Permet au frontend de tester la classification avant soumission
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "Aucun fichier fourni"
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "status": "error", 
                "message": "Aucun fichier sélectionné"
            }), 400
            
        if not allowed_file(file.filename):
            return jsonify({
                "status": "error",
                "message": "Type de fichier non autorisé"
            }), 400
        
        # Sauvegarder temporairement le fichier
        upload_folder = current_app.config['UPLOAD_FOLDER']
        ext = file.filename.rsplit('.', 1)[1].lower()
        temp_filename = f"temp_classify.{ext}"
        filepath = os.path.join(upload_folder, temp_filename)
        file.save(str(filepath))
        
        try:
            # Extraire les features de l'image
            size, width, height, avg_r, avg_g, avg_b, contrast, edges_detected = calculate_image_properties(filepath)
            
            # Utiliser le moteur de règles pour classifier
            rules_engine = RulesEngine()
            classifier = BinClassifier(rules_engine=rules_engine)
            
            # Extraire toutes les features avancées
            base_features = {
                'avg_red': avg_r,
                'avg_green': avg_g,
                'avg_blue': avg_b,
                'size': size,
                'width': width,
                'height': height,
                'contrast': contrast,
                'edges_detected': edges_detected
            }
            
            image_features = ImageFeatures(base_features)
            advanced_features = image_features.extract_all_features()
            
            # Classification
            result = classifier.classify(advanced_features)
            
            return jsonify({
                "status": "success",
                "prediction": result['prediction'],
                "confidence": round(result['confidence'], 3),
                "score": round(result['score'], 3),
                "active_rules": result['details']['active_rules'],
                "rules_count": len(result['details']['active_rules']),
                "advanced_rules": result.get('advanced_rules', []),
                "features_extracted": len(advanced_features),
                "message": f"Classification réussie: {result['prediction']} (confiance: {result['confidence']:.1%})"
            })
            
        finally:
            # Supprimer le fichier temporaire
            if os.path.exists(filepath):
                os.remove(filepath)
        
    except Exception as e:
        current_app.logger.error(f"Error in classify_image: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur lors de la classification: {str(e)}"
        }), 500


@upload_bp.route('/test_classifier', methods=['POST'])
def test_classifier():
    """
    Route API pour tester le moteur de règles avec des paramètres personnalisés
    """
    try:
        # Récupérer les features de test depuis la requête JSON
        data = request.get_json() or {}
        
        # Features par défaut pour le test
        test_features = {
            'avg_red': data.get('avg_red', 120),
            'avg_green': data.get('avg_green', 100), 
            'avg_blue': data.get('avg_blue', 80),
            'size': data.get('size', 200),
            'width': data.get('width', 800),
            'height': data.get('height', 600),
            'contrast': data.get('contrast', 0.5),
            'edges_detected': data.get('edges_detected', 150)
        }
        
        # Utiliser le moteur de règles
        rules_engine = RulesEngine()
        classifier = BinClassifier(rules_engine=rules_engine)
        
        # Extraire toutes les features avancées
        image_features = ImageFeatures(test_features)
        advanced_features = image_features.extract_all_features()
        
        # Classification
        result = classifier.classify(advanced_features)
        
        # Informations sur le moteur de règles
        thresholds = rules_engine.get_thresholds()
        
        return jsonify({
            "status": "success",
            "classification": {
                "prediction": result['prediction'],
                "confidence": round(result['confidence'], 3),
                "score": round(result['score'], 3)
            },
            "rules_engine": {
                "total_thresholds": len(thresholds),
                "active_rules": result['details']['active_rules'],
                "rules_count": len(result['details']['active_rules'])
            },
            "features": {
                "input_features": len(test_features),
                "extracted_features": len(advanced_features),
                "advanced_rules_used": len(result.get('advanced_rules', []))
            },
            "message": "Test du moteur de règles réussi"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in test_classifier: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du test: {str(e)}"
        }), 500


from flask import Blueprint, request, redirect, flash, url_for
from backend.services.image_service import insert_annotation
from backend.services.image_service import get_image_id_by_filename
annotate_bp = Blueprint('annotate', __name__)

@annotate_bp.route('/annotate/<filename>', methods=['POST'])
def submit_annotation(filename):
    label = request.form.get('label')

    if not label or label not in ['plein', 'vide']:
        flash("Annotation invalide.", "error")
        return redirect(url_for('upload.gallery'))

    image_id = get_image_id_by_filename(filename)
    if image_id is None:
        flash("Image introuvable pour annotation.", "error")
        return redirect(url_for('upload.gallery'))

    insert_annotation(image_id=image_id, label=label, source='manuel')
    flash(f"Annotation '{label}' enregistrée avec succès !", "success")
    return redirect(url_for('upload.gallery'))

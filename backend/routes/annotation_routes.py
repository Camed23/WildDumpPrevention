from flask import Blueprint, render_template, flash, url_for, redirect, session
from backend.services.image_service import get_image_id_by_filename
from backend.config import supabase

annotate_bp = Blueprint('annotate', __name__)

@annotate_bp.route('/annotate/<filename>', methods=['GET'])
def show_annotation(filename):
    image_id = get_image_id_by_filename(filename)
    if not image_id:
        flash("Image non trouvée.", "error")
        return redirect(url_for('upload.upload_file'))

    # Récupération des métadonnées image
    image_result = supabase.table("image").select("*").eq("image_id", image_id).execute()
    if not image_result.data:
        flash("Aucune donnée disponible pour cette image.", "error")
        return redirect(url_for('upload.upload_file'))
    image_data = image_result.data[0]

    # Récupération de l’annotation liée à cette image
    annotation_result = supabase.table("annotation").select("*").eq("image_id", image_id).execute()
    annotation_data = annotation_result.data[0] if annotation_result.data else None

    image_info = {
        "location": image_data.get("localisation"),
        "date_user": session.pop("temp_date", None),  # date saisie par l'utilisateur
        "time": session.pop("temp_time", None),
        "notes": session.pop("temp_notes", None),
        "choice": annotation_data.get("source") if annotation_data else None,
        "prediction": annotation_data.get("label") if annotation_data else None,
        "file_size_kb": round(image_data["size"], 2),
        "dimensions": f"{image_data['width']} x {image_data['height']}",
        "avg_r": round(image_data["avg_red"], 2),
        "avg_g": round(image_data["avg_green"], 2),
        "avg_b": round(image_data["avg_blue"], 2),
        "contrast": round(image_data["contrast"], 2),
        "edges_detected": round(image_data["edges_detected"], 2),
        "upload_date": image_data.get("upload_date"),
        "image_url": url_for('upload.uploaded_file', filename=image_data["name_image"])
    }

    return render_template("annotate.html", image_info=image_info)

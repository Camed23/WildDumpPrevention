from flask import Blueprint, render_template, send_from_directory
import os
from flask import abort

greenit_bp = Blueprint('greenit', __name__)

@greenit_bp.route('/')
def greenit():
    return render_template('greenit.html')

@greenit_bp.route('/documents/<path:filename>')
def download_document(filename):
    directory = os.path.join(os.getcwd(), 'static/documents')
    full_path = os.path.abspath(os.path.join(directory, filename))

    # Empêche l'accès en dehors du dossier
    if not full_path.startswith(os.path.abspath(directory)):
        abort(403)

    return send_from_directory(directory, filename, as_attachment=True)

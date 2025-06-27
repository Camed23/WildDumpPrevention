import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(upload_path, extension):
    """Génère un nom de fichier unique comme image1.jpg, image2.jpg, etc."""
    os.makedirs(upload_path, exist_ok=True)  # Crée le dossier si nécessaire

    max_index = 0
    for filename in os.listdir(upload_path):
        if filename.startswith("image") and '.' in filename:
            base, ext = filename.rsplit('.', 1)
            if ext.lower() in ALLOWED_EXTENSIONS:
                try:
                    number = int(base.replace("image", ""))
                    if number > max_index:
                        max_index = number
                except ValueError:
                    continue

    return f"image{max_index + 1}.{extension}"

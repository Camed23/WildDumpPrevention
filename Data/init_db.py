from supabase import create_client, Client
import os
from PIL import Image, ImageStat, ImageFilter
from supabase import create_client
import numpy as np
import random

# Liste de villes possibles
villes_possibles = [
    "Paris", "Lyon", "Marseille", "Toulouse", "Nice",
    "Lille", "Nantes", "Strasbourg", "Bordeaux", "Montpellier",
    "Rennes", "Reims", "Le Havre"
]
# Remplace avec tes infos Supabase
url = "https://bqkxmcrmolfjlglmmqlj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJxa3htY3Jtb2xmamxnbG1tcWxqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3NzI1ODgsImV4cCI6MjA2NjM0ODU4OH0.QrcFfKD2aHZP-PwVoWWq1hnNZ5cOCckL4YvmPHsSmt0"

supabase: Client = create_client(url, key)

"""
response = supabase.rpc("creation_user", {
    "p_username": "Dataimport",
    "p_email": "Dataimport@email.com",
    "p_password": "motdepasse",
    "p_role": "Admin"
}).execute()


# Récupérer tous les utilisateurs
response = supabase.table("User").select("*").execute()

# Afficher les résultats
for user in response.data:
    print(f"Username: {user['username']}, Email: {user['email']}, Role: {user['role']}")
"""

#%% Récupérer toutes les images dans train, wuth_label, clean et extraire leur méthadonnée pour les insérer dans la talbe
"""
print("Répertoire courant :", os.getcwd())

user_id = 4
# 📁 Répertoire contenant les images                                                                           

def calculate_image_properties(image_path):
    img = Image.open(image_path).convert('RGB')
    stat = ImageStat.Stat(img)

    avg_red, avg_green, avg_blue = stat.mean
    width, height = img.size

    # Taille fichier en kilo-octets (ou octets)
    size = os.path.getsize(image_path) / 1024  # en ko

    # Calcul du contraste (écart-type des pixels)
    contrast = np.std(np.array(img))

    # Détection des bords : on applique un filtre de contours puis on calcule la moyenne
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges_stat = ImageStat.Stat(edges)
    edges_mean = np.mean(edges_stat.mean)
    edges_detected = edges_mean > 10  # seuil arbitraire à ajuster

    return size, width, height, avg_red, avg_green, avg_blue, contrast, edges_detected

# Chemin du dossier images (relatif au script)
folder_path = "Data/train/with_label/clean"

for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        full_path = os.path.join(folder_path, filename)
        file_path_for_db = f"{folder_path}/{filename}"  # chemin selon ta table

        props = calculate_image_properties(full_path)
        size, width, height, avg_red, avg_green, avg_blue, contrast, edges_detected = props
        localisation = random.choice(villes_possibles) # A enlever si ajout via le site avec la localsisation fourni

        # Appel de la fonction stockée creation_image
        response = supabase.rpc("creation_image", {
            "p_user_id": user_id,
            "p_file_path": file_path_for_db,
            "p_name_image": filename,
            "p_size": size,
            "p_width": width,
            "p_height": height,
            "p_avg_red": avg_red,
            "p_avg_green": avg_green,
            "p_avg_blue": avg_blue,
            "p_contrast": contrast,
            "p_edges_detected": int(edges_detected),
            "p_localisation": localisation  # Ville aléatoire pour les images su train
        }).execute()

        if response.data is None:
            print("[ERREUR]", filename)
        else:
            print("[OK]", filename)
"""
#suppression des images de teste
"""
for image_id in range(88, 108):  # 28 exclu => jusqu'à 27
    response = supabase.rpc("supp_image", {"p_image_id": image_id}).execute()
    print(f"Suppression image {image_id} -> {response.data}")
"""
# Afficher toutes les images
"""
response = supabase.table("image").select("*").execute()

# Afficher les résultats
for image in response.data:
    print(f"ID: {image['image_id']}, Nom: {image.get('name_image', 'N/A')}, Chemin: {image['file_path']}, "
          f"Taille: {image.get('size', 'N/A')}, Dimensions: {image.get('width', 'N/A')}x{image.get('height', 'N/A')}, "
          f"Date upload: {image.get('upload_date', 'N/A')}, "
          f"Couleurs moyennes (R,G,B): ({image.get('avg_red', 'N/A')}, {image.get('avg_green', 'N/A')}, {image.get('avg_blue', 'N/A')}), "
          f"Contraste: {image.get('contrast', 'N/A')}, Bords détectés: {image.get('edges_detected', 'N/A')}, "
          f"User ID: {image.get('user_id', 'N/A')}")
"""
# Ajoute de l'anottation manuel a vide pour les image récupérer dans clean
"""
for image_id in range(130, 150):  # 48 exclu, donc de 28 à 47
    response = supabase.rpc("creation_annotation", {
        "p_image_id": image_id,
        "p_label": "vide",
        "p_source": "manuel"
    }).execute()
    print(f"Annotation ajoutée pour image {image_id} -> {response.data}")
"""


#%% Récupérer toutes les images dans train, wuth_label, dirty et extraire leur méthadonnée pour les insérer dans la talbe
"""
print("Répertoire courant :", os.getcwd())

user_id = 4
# 📁 Répertoire contenant les images
local_path = "Data/train/with_label/dirty"
storage_path_prefix = "/Data/train/with_label/dirty"


def calculate_image_properties(image_path):
    img = Image.open(image_path).convert('RGB')
    stat = ImageStat.Stat(img)

    avg_red, avg_green, avg_blue = stat.mean
    width, height = img.size

    # Taille fichier en kilo-octets (ou octets)
    size = os.path.getsize(image_path) / 1024  # en ko

    # Calcul du contraste (écart-type des pixels)
    contrast = np.std(np.array(img))

    # Détection des bords : on applique un filtre de contours puis on calcule la moyenne
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges_stat = ImageStat.Stat(edges)
    edges_mean = np.mean(edges_stat.mean)
    edges_detected = edges_mean > 10  # seuil arbitraire à ajuster

    return size, width, height, avg_red, avg_green, avg_blue, contrast, edges_detected

# Chemin du dossier images (relatif au script)
folder_path = "Data/train/with_label/dirty"

for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        full_path = os.path.join(folder_path, filename)
        file_path_for_db = f"{folder_path}/{filename}"  # chemin selon ta table

        props = calculate_image_properties(full_path)
        size, width, height, avg_red, avg_green, avg_blue, contrast, edges_detected = props
        localisation = random.choice(villes_possibles) # A enlever si ajout via le site avec la localsisation fourni

        # Appel de la fonction stockée creation_image
        response = supabase.rpc("creation_image", {
            "p_user_id": user_id,
            "p_file_path": file_path_for_db,
            "p_name_image": filename,
            "p_size": size,
            "p_width": width,
            "p_height": height,
            "p_avg_red": avg_red,
            "p_avg_green": avg_green,
            "p_avg_blue": avg_blue,
            "p_contrast": contrast,
            "p_edges_detected": int(edges_detected),
            "p_localisation": localisation  # Ville aléatoire pour les images su train
        }).execute()

        if response.data is None:
            print("[ERREUR]", filename)
        else:
            print("[OK]", filename)
"""

# Récupérer toutes les images
"""
response = supabase.table("image").select("*").execute()

# Afficher les résultats

for image in response.data:
    print(f"ID: {image['image_id']}, Nom: {image.get('name_image', 'N/A')}, Chemin: {image['file_path']}, "
          f"Taille: {image.get('size', 'N/A')}, Dimensions: {image.get('width', 'N/A')}x{image.get('height', 'N/A')}, "
          f"Date upload: {image.get('upload_date', 'N/A')}, "
          f"Couleurs moyennes (R,G,B): ({image.get('avg_red', 'N/A')}, {image.get('avg_green', 'N/A')}, {image.get('avg_blue', 'N/A')}), "
          f"Contraste: {image.get('contrast', 'N/A')}, Bords détectés: {image.get('edges_detected', 'N/A')}, "
          f"User ID: {image.get('user_id', 'N/A')}")
"""
# Ajoute de l'anottation manuel a plein pour les image récupérer dans dirty
"""
for image_id in range(150, 170):  # 68 exclu, donc de 48 à 68
    response = supabase.rpc("creation_annotation", {
        "p_image_id": image_id,
        "p_label": "plein",
        "p_source": "manuel"
    }).execute()
    print(f"Annotation ajoutée pour image {image_id} -> {response.data}")
"""
#suppression des annotation de teste
"""
for image_id in range(61, 68): 
    response = supabase.rpc("supp_image", {"p_image_id": image_id}).execute()
    print(f"Suppression image {image_id} -> {response.data}")
"""

#%% test de récupératio des données gps : 
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if not exif_data:
        return None

    exif = {}
    for tag, value in exif_data.items():
        decoded = TAGS.get(tag, tag)
        exif[decoded] = value
    return exif

def get_gps_info(exif_data):
    if 'GPSInfo' not in exif_data:
        return None

    gps_info = {}
    for key in exif_data['GPSInfo'].keys():
        decode = GPSTAGS.get(key, key)
        gps_info[decode] = exif_data['GPSInfo'][key]

    # Convert GPS coordinates to decimal
    def convert_to_degrees(value):
        d = value[0][0] / value[0][1]
        m = value[1][0] / value[1][1]
        s = value[2][0] / value[2][1]
        return d + (m / 60.0) + (s / 3600.0)

    lat = convert_to_degrees(gps_info['GPSLatitude'])
    if gps_info['GPSLatitudeRef'] != 'N':
        lat = -lat

    lon = convert_to_degrees(gps_info['GPSLongitude'])
    if gps_info['GPSLongitudeRef'] != 'E':
        lon = -lon

    return lat, lon

# Exemple d'utilisation
exif_data = get_exif_data("Data/train/with_label/clean/0e02598e-acbb-423e-912e-cf2b922b5bd7.jpeg")
if exif_data:
    gps_coords = get_gps_info(exif_data)
    if gps_coords:
        print("Latitude:", gps_coords[0])
        print("Longitude:", gps_coords[1])
    else:
        print("Aucune info GPS trouvée.")
else:
    print("Aucune métadonnée EXIF trouvée.")

#%% Teste de récupération de l'image et de l'annotation lié

for image_id in [130, 169]:
    image_data = supabase.table("image").select("*").eq("image_id", image_id).single().execute()
    annotation_data = supabase.table("annotation").select("*").eq("image_id", image_id).single().execute()

    print(f"\n{'='*40}")
    print(f"🖼️  Image ID : {image_id}")
    print(f"{'-'*40}")
    print("📷 Image :")
    for key, value in image_data.data.items():
        print(f"   - {key}: {value}")

    print(f"\n📝 Annotation :")
    if annotation_data.data:
        for key, value in annotation_data.data.items():
            print(f"   - {key}: {value}")
    else:
        print("   - Aucune annotation trouvée.")

    print(f"{'='*40}\n")

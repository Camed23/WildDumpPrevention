from PIL import Image, ImageStat, ImageFilter
import numpy as np
import os

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

"""int image_id unique
string file_path
string name
datetime upload_date
real  size
int width 
int height
real avg_red
real avg_green
real avg_blue
real contrast
bool edges_detected
string localisation #nom de la ville""" # inutile de recoder ces features, elles sont déjà dans la base de données

"""
from PIL import Image
import numpy as np

class ImageFeatures:
    def __init__(self, path):
        # 1. Charger l’image
        self.path = path
        self.img = Image.open(path)
        self.pixels = np.array(self.img)

    def compute_mean_brightness(self):
        # 2. Calculer la luminosité moyenne (R+G+B)/3
        # Ici on simplifie : on prend juste la moyenne de tous les canaux
        return self.pixels.mean()

    def compute_edge_density(self):
        # 3. Détecter les contours (simplifié sans OpenCV)
        # Juste un stub qui renvoie 0.1 en attendant
        return 0.1

    def compute_area_ratio(self):
        # 4. Estimer la zone occupée (stub)
        # On renvoie 0.5 par défaut, à remplacer plus tard
        return 0.5
"""
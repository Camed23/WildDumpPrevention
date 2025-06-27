# backend/services/feature_extractor.py

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

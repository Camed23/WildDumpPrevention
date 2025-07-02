from PIL import Image, ImageStat, ImageFilter
import numpy as np
import cv2
import os

def calculate_image_properties(image_path):
    """
    Calculates various properties of an image file need in the database.
    Args:
        image_path (str): The file path to the image.
    Returns:
        tuple: A tuple containing the following properties:
            - size (float): The file size in kilobytes (KB).
            - width (int): The width of the image in pixels.
            - height (int): The height of the image in pixels.
            - avg_red (float): The average red channel value.
            - avg_green (float): The average green channel value.
            - avg_blue (float): The average blue channel value.
            - contrast (float): The standard deviation of pixel values (contrast).
            - edges_detected (bool): Whether edges are detected in the image (based on a threshold).
    """

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

class ImageFeatures:
    """
    Classe pour extraire toutes les features nécessaires au rules engine.
    """
    def __init__(self, image_data):
        """
        Args:
            image_data (dict): Données de l'image depuis le cache JSON contenant:
                - file_path: chemin vers l'image
                - size, width, height, avg_red, avg_green, avg_blue, contrast, edges_detected
        """
        self.image_data = image_data
        self.file_path = image_data.get('file_path', '')
        
        # Charger l'image si le fichier existe
        if os.path.exists(self.file_path):
            self.img = Image.open(self.file_path).convert('RGB')
            self.pixels = np.array(self.img)
        else:
            self.img = None
            self.pixels = None

    def compute_mean_brightness(self):
        """Calculer la luminosité moyenne (R+G+B)/3"""
        if self.pixels is not None:
            return float(self.pixels.mean())
        # Utiliser les données du cache si l'image n'est pas accessible
        avg_rgb = (self.image_data.get('avg_red', 0) + 
                  self.image_data.get('avg_green', 0) + 
                  self.image_data.get('avg_blue', 0)) / 3
        return float(avg_rgb)

    def compute_edge_density(self):
        """Calculer la densité de contours"""
        if self.img is not None:
            edges = self.img.filter(ImageFilter.FIND_EDGES)
            edges_stat = ImageStat.Stat(edges)
            edges_mean = np.mean(edges_stat.mean)
            return float(edges_mean / 255.0)  # Normaliser entre 0 et 1
        # Utiliser les données du cache
        return 0.1 if self.image_data.get('edges_detected', False) else 0.05

    def compute_area_ratio(self):
        """Estimer la zone occupée (basée sur la variabilité des couleurs)"""
        if self.pixels is not None:
            # Calculer la variabilité des couleurs comme proxy de la zone occupée
            color_std = np.std(self.pixels, axis=(0, 1)).mean()
            return min(color_std / 100.0, 1.0)  # Normaliser approximativement
        # Utiliser le contraste du cache comme proxy
        contrast = self.image_data.get('contrast', 0)
        return min(contrast / 200.0, 1.0)

    def compute_contrast_iqr(self):
        """Calculer le contraste inter-quartile"""
        if self.pixels is not None:
            gray_pixels = np.mean(self.pixels, axis=2).flatten()
            q75, q25 = np.percentile(gray_pixels, [75, 25])
            return float(q75 - q25)
        # Utiliser le contraste du cache
        return float(self.image_data.get('contrast', 0))

    def compute_file_size_mb(self):
        """Calculer la taille du fichier en MB"""
        size_kb = self.image_data.get('size', 0)
        return float(size_kb / 1024.0)  # Convertir KB en MB

    def compute_hue_std(self):
        """Calculer l'écart-type de la teinte (variabilité des couleurs)"""
        if self.pixels is not None:
            # Convertir en HSV et calculer l'écart-type de la teinte
            from PIL import Image as PILImage
            hsv_img = self.img.convert('HSV')
            hsv_pixels = np.array(hsv_img)
            hue_values = hsv_pixels[:, :, 0].flatten()
            return float(np.std(hue_values))
        # Approximation basée sur la variabilité RGB
        rgb_std = np.std([
            self.image_data.get('avg_red', 0),
            self.image_data.get('avg_green', 0), 
            self.image_data.get('avg_blue', 0)
        ])
        return float(rgb_std)

    def extract_all_features(self):
        """Extraire toutes les features nécessaires pour le rules engine"""
        return {
            "mean_brightness": self.compute_mean_brightness(),
            "edge_density": self.compute_edge_density(),
            "area_ratio": self.compute_area_ratio(),
            "contrast_iqr": self.compute_contrast_iqr(),
            "file_size_mb": self.compute_file_size_mb(),
            "hue_std": self.compute_hue_std()
        }


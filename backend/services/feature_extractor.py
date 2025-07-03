import numpy as np
from PIL import Image, ImageStat, ImageFilter
import cv2
import os
#from skimage.feature import hog, greycomatrix, greycoprops
#from sklearn.cluster import KMeans

# Metadonnées de l'image dans la base de données
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
real contrasts
bool edges_detected
string localisation #nom de la ville""" 

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

    def compute_texture_entropy(self):
        """Calculer l'entropie de texture - mesure la complexité/désordre de l'image"""
        if self.pixels is not None:
            # Convertir en niveaux de gris
            gray = np.mean(self.pixels, axis=2).astype(np.uint8)
            # Calculer l'histogramme
            hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
            # Normaliser l'histogramme
            hist = hist / hist.sum()
            # Calculer l'entropie
            entropy = -np.sum(hist * np.log2(hist + 1e-7))  # +1e-7 pour éviter log(0)
            return float(entropy)
        return 5.0  # Valeur par défaut

    def compute_color_complexity(self):
        """Calculer la complexité des couleurs - nombre de couleurs distinctes (VERSION OPTIMISÉE)"""
        if self.pixels is not None:
            # OPTIMISATION: Réduire drastiquement la résolution
            small_img = self.pixels[::8, ::8]  # Prendre 1 pixel sur 8 (au lieu de 4)
            
            # Quantifier plus agressivement les couleurs
            colors = small_img.reshape(-1, 3)
            quantized = (colors // 64) * 64  # Réduire à 4 niveaux par canal (au lieu de 8)
            
            # Compter les couleurs uniques
            unique_colors = len(np.unique(quantized.view(np.dtype((np.void, quantized.dtype.itemsize*3)))))
            return float(unique_colors / len(colors))
        return 0.1

    def compute_brightness_variance(self):
        """Calculer la variance de luminosité - détecte les ombres et variations"""
        if self.pixels is not None:
            brightness = np.mean(self.pixels, axis=2)
            return float(np.var(brightness))
        # Utiliser le contraste du cache comme approximation
        contrast = self.image_data.get('contrast', 0)
        return float(contrast ** 2)  # Variance ≈ contraste²

    def compute_edge_coherence(self):
        """Calculer la cohérence des contours - structure vs chaos"""
        if self.img is not None:
            # Appliquer différents filtres de contours
            edges_h = self.img.filter(ImageFilter.Kernel((3, 3), [-1, -1, -1, 0, 0, 0, 1, 1, 1]))
            edges_v = self.img.filter(ImageFilter.Kernel((3, 3), [-1, 0, 1, -1, 0, 1, -1, 0, 1]))
            
            # Calculer la cohérence (faible = chaos, élevée = structure)
            edges_h_std = np.std(np.array(edges_h))
            edges_v_std = np.std(np.array(edges_v))
            coherence = abs(edges_h_std - edges_v_std) / (edges_h_std + edges_v_std + 1e-7)
            return float(coherence)
        return 0.5

    def compute_spatial_frequency(self):
        """Calculer la fréquence spatiale - détecte les motifs répétitifs vs aléatoires"""
        if self.pixels is not None:
            gray = np.mean(self.pixels, axis=2)
            # Calculer les gradients
            grad_x = np.diff(gray, axis=1)
            grad_y = np.diff(gray, axis=0)
            # Fréquence spatiale = moyenne des gradients
            spatial_freq = np.sqrt(np.mean(grad_x**2) + np.mean(grad_y**2))
            return float(spatial_freq)
        return 10.0

    def compute_fill_ratio_advanced(self):
        """Calculer un ratio de remplissage plus sophistiqué basé sur la segmentation"""
        if self.pixels is not None:
            # Convertir en HSV pour une meilleure segmentation
            hsv = np.array(self.img.convert('HSV'))
            
    def compute_fill_ratio_advanced(self):
        """Calculer un ratio de remplissage plus sophistiqué basé sur la segmentation (VERSION OPTIMISÉE)"""
        if self.pixels is not None:
            # OPTIMISATION 1: Réduire la taille de l'image pour accélérer
            h, w = self.pixels.shape[:2]
            scale_factor = 4  # Traiter 1 pixel sur 4
            small_pixels = self.pixels[::scale_factor, ::scale_factor]
            
            # Convertir en HSV
            small_img = Image.fromarray(small_pixels).convert('HSV')
            hsv = np.array(small_img)
            
            # OPTIMISATION 2: Utiliser un kernel plus grand et moins de calculs
            h_small, w_small = hsv[:,:,0].shape
            kernel_size = max(3, min(h_small, w_small) // 20)  # Kernel plus grand
            
            # OPTIMISATION 3: Calculer seulement sur une grille, pas tous les pixels
            step = max(1, kernel_size // 2)  # Calculer 1 point sur 2 ou 3
            variance_samples = []
            
            for i in range(kernel_size//2, h_small - kernel_size//2, step):
                for j in range(kernel_size//2, w_small - kernel_size//2, step):
                    region = hsv[i-kernel_size//2:i+kernel_size//2+1, 
                               j-kernel_size//2:j+kernel_size//2+1, :]
                    variance_samples.append(np.var(region))
            
            if variance_samples:
                # Ratio de zones à forte variance
                threshold = np.percentile(variance_samples, 60)
                high_variance_ratio = sum(1 for v in variance_samples if v > threshold) / len(variance_samples)
                return float(high_variance_ratio)
        
        # Fallback rapide
        return self.compute_area_ratio()

    
    def extract_all_features(self):
        """Extraire toutes les features nécessaires pour le rules engine"""
        return {
            # Features existantes (rapides)
            "mean_brightness": self.compute_mean_brightness(),
            "edge_density": self.compute_edge_density(),
            "area_ratio": self.compute_area_ratio(),
            "contrast_iqr": self.compute_contrast_iqr(),
            "file_size_mb": self.compute_file_size_mb(),
            "hue_std": self.compute_hue_std(),
            
            # Nouvelles features optimisées (plus rapides)
            "texture_entropy": self.compute_texture_entropy(),
            "color_complexity": self.compute_color_complexity(),
            "brightness_variance": self.compute_brightness_variance(),
            "spatial_frequency": self.compute_spatial_frequency(),
            "fill_ratio_advanced": self.compute_fill_ratio_advanced(),
            
            # Feature lente désactivée temporairement
            # "edge_coherence": self.compute_edge_coherence(),  # TROP LENTE
        }

